# NeuroAI Testing Strategy & Implementation Guide

**Version**: 1.0.0  
**Status**: Ready for Implementation  
**Target Coverage**: >80% code coverage

---

## Overview

This document outlines the comprehensive testing strategy for NeuroAI across all layers: backend API, frontend UI, ML/DL models, and Android mobile application. It serves as a roadmap for quality assurance and continuous integration.

---

## Testing Pyramid

```
                    ████████
                  End-to-End (5%)
                ████████████████
              Integration Tests (20%)
            ████████████████████████
          Unit Tests (75%)
```

**Breakdown**:
- **Unit Tests (75%)**: Individual functions, models, components
- **Integration Tests (20%)**: Component interactions, API contracts, database operations
- **End-to-End Tests (5%)**: Full user workflows, critical paths

---

## Backend Testing Strategy

### 1. ML Module Unit Tests

**File**: `backend/core/tests/test_ml_modules.py`

#### Molecular Representation Tests

```python
# Test molecular encoder
def test_molecular_encoder_initialization():
    """Verify GAT encoder loads correctly"""
    encoder = MolecularGraphEncoder()
    assert encoder is not None
    assert encoder.gat is not None

def test_smiles_to_graph_conversion():
    """Test SMILES → PyG Data conversion"""
    encoder = MolecularGraphEncoder()
    for smiles in ['CC', 'c1ccccc1', 'O=C(O)c1ccccc1']:  # Ethane, Benzene, Aspirin
        graph = encoder.smiles_to_graph(smiles)
        assert graph.x is not None
        assert graph.edge_index is not None
        assert graph.x.shape[0] > 0

def test_molecular_embedding_dimension():
    """Verify embedding output dimension"""
    encoder = MolecularGraphEncoder()
    graph = encoder.smiles_to_graph('CC')
    embedding = encoder(graph.unsqueeze(0))
    assert embedding.shape == (1, 256)

def test_descriptor_extraction():
    """Test RDKit descriptor calculation"""
    desc = PhysicochemicalDescriptors()
    mol = Chem.MolFromSmiles('CC')
    descriptors = desc.extract_descriptors(mol)
    assert len(descriptors) == 10
    for d in descriptors:
        assert isinstance(d, float)
        assert 0 <= d <= 1000  # Reasonable bounds

def test_unified_embedding_fusion():
    """Test multi-view embedding fusion"""
    pipeline = MolecularRepresentationPipeline()
    embedding, metadata = pipeline.process_molecule('c1ccccc1')
    assert embedding.shape == (256,)
    assert 'graph_contribution' in metadata
    assert 'descriptor_contribution' in metadata
    assert metadata['graph_contribution'] + metadata['descriptor_contribution'] <= 1.01
```

#### Target Engagement Tests

```python
def test_binding_affinity_predictor_initialization():
    """Verify model loading"""
    predictor = BindingAffinityPredictor.from_pretrained()
    assert predictor is not None
    assert predictor.binding_head is not None

def test_affinity_prediction():
    """Test IC50/Kd predictions"""
    predictor = BindingAffinityPredictor.from_pretrained()
    drug_emb = torch.randn(1, 256)
    target_emb = torch.randn(1, 512)
    
    output = predictor(drug_emb, target_emb)
    assert output['ic50'].shape == (1,)
    assert output['kd'].shape == (1,)
    assert 0 <= output['bind_prob'][0] <= 1

def test_mc_dropout_uncertainty():
    """Test Monte Carlo dropout uncertainty"""
    predictor = BindingAffinityPredictor.from_pretrained()
    drug_emb = torch.randn(1, 256)
    target_emb = torch.randn(1, 512)
    
    predictions = []
    for _ in range(10):
        output = predictor(drug_emb, target_emb)
        predictions.append(output['ic50'].item())
    
    # Should have reasonable variance (Not all identical)
    std = np.std(predictions)
    assert std > 0, "MC Dropout not producing variance"
    assert std < 5, "MC Dropout producing unreasonable variance"

def test_toxicity_classification():
    """Test 5-class toxicity prediction"""
    predictor = ToxicityPredictor()
    drug_emb = torch.randn(1, 256)
    
    logits = predictor(drug_emb)
    probs = torch.softmax(logits, dim=-1)
    
    assert probs.shape == (1, 5)
    assert torch.allclose(probs.sum(dim=-1), torch.ones(1), atol=0.01)

def test_off_target_detection():
    """Test off-target risk scoring"""
    predictor = OffTargetPredictor()
    drug_emb = torch.randn(1, 256)
    
    scores = predictor(drug_emb)  # 100 off-targets
    assert scores.shape == (1, 100)
    assert torch.all(scores >= 0) and torch.all(scores <= 1)
```

#### Disease Model Tests

```python
def test_vae_encoder_decoder():
    """Test VAE reconstruction"""
    vae = DiseaseStateVAE(input_dim=64, latent_dim=16)
    x = torch.randn(4, 64)  # Batch of 4 patients
    
    x_recon, mu, logvar = vae(x)
    assert x_recon.shape == x.shape
    assert mu.shape == (4, 16)
    assert logvar.shape == (4, 16)

def test_neural_ode_dynamics():
    """Test ODE integration"""
    ode_cell = NeuralODECell(input_dim=16, hidden_dim=32)
    z0 = torch.randn(4, 16)
    t_span = torch.linspace(0, 1, 10)
    
    z_t = ode_cell.solve_ode(z0, t_span)
    assert z_t.shape == (4, 10, 16)
    
    # Ensure smooth dynamics (small differences between consecutive time points)
    diffs = torch.abs(z_t[:, 1:, :] - z_t[:, :-1, :])
    assert torch.mean(diffs) < 0.5

def test_disease_trajectory_prediction():
    """Test full VAE→ODE→prediction"""
    model = IntegratedDiseaseModel()
    patient_data = torch.randn(2, 64)
    drug_emb = torch.randn(2, 256)
    t_future = torch.linspace(0, 1, 12)  # 1 year
    
    output = model.predict_trajectory(patient_data, drug_emb, t_future)
    
    assert output['severity'].shape == (2, 12)
    assert output['progression_rate'].shape == (2,)
    assert output['adverse_risk'].shape == (2,)
    assert torch.all(output['severity'] >= 0) and torch.all(output['severity'] <= 10)

def test_vae_kl_divergence():
    """Test KL divergence calculation"""
    vae = DiseaseStateVAE(input_dim=64, latent_dim=16)
    x = torch.randn(4, 64)
    x_recon, mu, logvar = vae(x)
    
    kl_loss = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())
    assert kl_loss > 0, "KL divergence should be positive"
    assert kl_loss < 1000, "KL divergence unreasonably large"
```

#### MedGemma Service Tests

```python
def test_rag_vector_database_initialization():
    """Verify ChromaDB collections creation"""
    rag = RAGVectorDatabase()
    
    assert rag.drug_collection is not None
    assert rag.target_collection is not None
    assert rag.pathway_collection is not None
    assert rag.evidence_collection is not None

def test_drug_knowledge_ingestion():
    """Test adding drugs to knowledge base"""
    rag = RAGVectorDatabase()
    
    drug_data = {
        'name': 'Aspirin',
        'smiles': 'CC(=O)Oc1ccccc1C(=O)O',
        'mechanism': 'COX inhibitor',
        'targets': ['PTGS1', 'PTGS2'],
        'adverse_effects': ['GI bleeding', 'Aspirin sensitivity']
    }
    
    rag.add_drug_knowledge(drug_data)
    
    # Verify retrieval
    results = rag.retrieve_relevant_knowledge('Aspirin mechanism', n_results=1)
    assert len(results) > 0

def test_semantic_search():
    """Test RAG retrieval accuracy"""
    rag = RAGVectorDatabase()
    
    # Seed with example data
    rag.add_drug_knowledge({
        'name': 'Levodopa',
        'mechanism': 'Dopamine replacement therapy',
        'disease': 'Parkinson disease'
    })
    
    query = "dopamine parkinson treatment"
    results = rag.retrieve_relevant_knowledge(query, n_results=1)
    
    assert len(results) > 0
    assert 'Levodopa' in results[0] or 'dopamine' in results[0].lower()

def test_plausibility_validation():
    """Test biological plausibility assessment"""
    service = MedGemmaService()
    
    # Mock validation
    drug_name = "Test Drug"
    target_name = "BDNF"
    mechanism = "Neuroprotective"
    
    result = service.validate_plausibility(drug_name, target_name, mechanism)
    
    assert 'is_plausible' in result
    assert 'confidence' in result
    assert 'reasoning' in result
    assert 0 <= result['confidence'] <= 1

def test_constraint_enforcement():
    """Verify safety constraints are applied"""
    service = MedGemmaService()
    
    # Should reject unsourced claims
    invalid_mechanism = "Completely novel mechanism unseen in literature"
    prompt = service._build_constraint_prompt(invalid_mechanism)
    
    assert "constraint" in prompt.lower() or "citation" in prompt.lower()

def test_redis_caching():
    """Test cache hit/miss behavior"""
    service = MedGemmaService()
    
    drug = "Aspirin"
    target = "PTGS1"
    mechanism = "COX inhibition"
    
    # First call (cache miss)
    result1 = service.validate_plausibility(drug, target, mechanism)
    metrics1 = service.get_usage_statistics()
    miss_count1 = metrics1['cache_misses']
    
    # Second call (cache hit)
    result2 = service.validate_plausibility(drug, target, mechanism)
    metrics2 = service.get_usage_statistics()
    
    assert result1 == result2, "Cached result should be identical"
    assert metrics2['cache_misses'] == miss_count1, "Cache miss count shouldn't increase"
    assert metrics2['cache_hit_rate'] > metrics1['cache_hit_rate']
```

### 2. API Integration Tests

**File**: `backend/core/tests/test_api_integration.py`

```python
import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def authenticated_client(api_client):
    user = User.objects.create_user(username='testuser', password='testpass')
    api_client.force_authenticate(user=user)
    return api_client

def test_drug_list_endpoint(authenticated_client):
    """Test GET /api/v1/drugs/"""
    response = authenticated_client.get('/api/v1/drugs/')
    
    assert response.status_code == 200
    assert isinstance(response.data, list) or isinstance(response.data, dict)

def test_drug_create_endpoint(authenticated_client):
    """Test POST /api/v1/drugs/"""
    payload = {
        'name': 'Test Drug',
        'smiles': 'CC',
        'mechanism': 'Test mechanism'
    }
    response = authenticated_client.post('/api/v1/drugs/', payload, format='json')
    
    assert response.status_code in [201, 400]  # Either created or validation error

def test_binding_prediction_endpoint(authenticated_client):
    """Test POST /api/v1/predict/binding/"""
    payload = {
        'drug_id': 1,
        'target_id': 1
    }
    response = authenticated_client.post('/api/v1/predict/binding/', payload, format='json')
    
    assert response.status_code in [200, 400, 404]
    if response.status_code == 200:
        assert 'ic50' in response.data or 'error' in response.data

def test_authentication_required(api_client):
    """Test that endpoints require authentication"""
    response = api_client.get('/api/v1/drugs/')
    
    assert response.status_code == 401

def test_rate_limiting(authenticated_client):
    """Test rate limiting (if configured)"""
    # Make 101 requests (assuming limit is 100/hour)
    for i in range(101):
        response = authenticated_client.get('/api/v1/drugs/')
        if i < 100:
            assert response.status_code == 200
        # Last request might be rate limited

def test_invalid_json_handling(authenticated_client):
    """Test API handles invalid JSON gracefully"""
    response = authenticated_client.post(
        '/api/v1/drugs/',
        'invalid json',
        content_type='application/json'
    )
    
    assert response.status_code == 400
```

### 3. Database Tests

**File**: `backend/core/tests/test_database.py`

```python
import pytest
from django.db import connection
from core.models import Drug, Target, DrugTarget, Pathway

@pytest.mark.django_db
def test_drug_model_creation():
    """Test Drug model creation and constraints"""
    drug = Drug.objects.create(
        name='Test Drug',
        smiles='CC',
        molecular_weight=30.0
    )
    
    assert drug.id is not None
    assert drug.name == 'Test Drug'
    assert Drug.objects.filter(name='Test Drug').exists()

@pytest.mark.django_db
def test_drug_target_relationship():
    """Test many-to-many relationship"""
    drug = Drug.objects.create(name='Drug A', smiles='CC')
    target = Target.objects.create(name='Target B', uniprot_id='P12345')
    
    relationship = DrugTarget.objects.create(
        drug=drug,
        target=target,
        affinity_value=7.5,
        affinity_unit='pIC50'
    )
    
    assert drug.targets.count() == 1
    assert target.drugs.count() == 1

@pytest.mark.django_db
def test_pathway_association():
    """Test pathway-target associations"""
    pathway = Pathway.objects.create(name='Neuroprotection')
    target = Target.objects.create(name='BDNF', uniprot_id='P23560')
    
    pathway.targets.add(target)
    
    assert target in pathway.targets.all()

@pytest.mark.django_db
def test_database_indexes():
    """Verify indexes are present for performance"""
    with connection.cursor() as cursor:
        # Check for drug name index
        cursor.execute("""
            SELECT name FROM pg_indexes
            WHERE tablename='core_drug' AND indexname LIKE '%name%'
        """)
        indexes = cursor.fetchall()
        assert len(indexes) > 0, "Drug name index missing"

@pytest.mark.django_db
def test_cascade_delete():
    """Test cascade delete behavior"""
    drug = Drug.objects.create(name='Drug A', smiles='CC')
    target = Target.objects.create(name='Target B', uniprot_id='P12345')
    DrugTarget.objects.create(drug=drug, target=target)
    
    drug.delete()
    
    assert DrugTarget.objects.filter(drug=drug).count() == 0
```

---

## Frontend Testing Strategy

### 1. React Component Tests

**File**: `frontend/src/__tests__/components.test.tsx`

```typescript
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { Header, Sidebar, Dashboard } from '../components';

describe('Header Component', () => {
  it('renders header with title', () => {
    render(<Header />);
    expect(screen.getByText(/NeuroAI/i)).toBeInTheDocument();
  });

  it('displays user menu when authenticated', () => {
    render(<Header currentUser={{ name: 'John' }} />);
    expect(screen.getByText(/John/i)).toBeInTheDocument();
  });

  it('shows login button when not authenticated', () => {
    render(<Header currentUser={null} />);
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('handles logout click', async () => {
    const mockLogout = jest.fn();
    render(<Header currentUser={{ name: 'John' }} onLogout={mockLogout} />);
    
    const logoutButton = screen.getByRole('button', { name: /logout/i });
    await userEvent.click(logoutButton);
    
    expect(mockLogout).toHaveBeenCalled();
  });
});

describe('Dashboard Component', () => {
  it('loads and displays drugs list', async () => {
    const mockDrugs = [
      { id: 1, name: 'Aspirin' },
      { id: 2, name: 'Levodopa' }
    ];
    
    jest.spyOn(global, 'fetch').mockResolvedValueOnce({
      json: async () => mockDrugs
    });

    render(<Dashboard />);
    
    expect(await screen.findByText('Aspirin')).toBeInTheDocument();
    expect(screen.getByText('Levodopa')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    jest.spyOn(global, 'fetch').mockRejectedValueOnce(new Error('API Error'));
    
    render(<Dashboard />);
    
    expect(await screen.findByText(/error/i)).toBeInTheDocument();
  });

  it('allows filtering drugs', async () => {
    render(<Dashboard />);
    
    const filterInput = screen.getByPlaceholderText(/filter/i);
    await userEvent.type(filterInput, 'Aspirin');
    
    expect(screen.getByDisplayValue('Aspirin')).toBeInTheDocument();
  });
});
```

### 2. Integration Tests

**File**: `frontend/src/__tests__/integration.test.tsx`

```typescript
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import App from '../App';

describe('End-to-End Workflows', () => {
  it('completes drug search and view detail flow', async () => {
    const mockDrugs = [{ id: 1, name: 'Aspirin', mechanism: 'COX inhibitor' }];
    
    jest.spyOn(global, 'fetch')
      .mockResolvedValueOnce({ json: async () => mockDrugs })
      .mockResolvedValueOnce({ json: async () => mockDrugs[0] });

    render(<App />);

    // Search for drug
    const searchInput = screen.getByPlaceholderText(/search/i);
    await userEvent.type(searchInput, 'Aspirin');

    // Click drug result
    const drugLink = await screen.findByRole('link', { name: /Aspirin/i });
    await userEvent.click(drugLink);

    // Verify detail view
    await waitFor(() => {
      expect(screen.getByText('COX inhibitor')).toBeInTheDocument();
    });
  });
});
```

---

## ML Model Validation Tests

### 1. Benchmark Validation

**File**: `backend/core/tests/test_model_validation.py`

```python
import pytest
from sklearn.metrics import roc_auc_score, mean_squared_error
from core.ml.target_engagement import BindingAffinityPredictor
from core.ml.disease_models import IntegratedDiseaseModel

class TestBindingAffinityBenchmark:
    """Validate against KIBA dataset"""
    
    @pytest.fixture
    def model(self):
        return BindingAffinityPredictor.from_pretrained()
    
    @pytest.fixture
    def kiba_data(self):
        # Load KIBA test set
        import pandas as pd
        return pd.read_csv('data/kiba_test.csv')
    
    def test_auc_score(self, model, kiba_data):
        """AUC on KIBA should be > 0.85"""
        predictions = model.predict_batch(kiba_data['drug_smiles'], kiba_data['target_seq'])
        auc = roc_auc_score(kiba_data['label'], predictions['bind_prob'])
        
        assert auc > 0.85, f"AUC {auc} below target 0.85"
    
    def test_affinity_rmse(self, model, kiba_data):
        """RMSE on affinity prediction < 0.5 log units"""
        predictions = model.predict_batch(kiba_data['drug_smiles'], kiba_data['target_seq'])
        rmse = np.sqrt(mean_squared_error(kiba_data['affinity'], predictions['ic50']))
        
        assert rmse < 0.5, f"RMSE {rmse} exceeds target 0.5"

class TestDiseasePredictionBenchmark:
    """Validate disease trajectory prediction"""
    
    def test_synthetic_disease_progression(self):
        """Test on synthetic disease data"""
        model = IntegratedDiseaseModel()
        
        # Generate synthetic patient data
        n_patients = 100
        patient_data = np.random.randn(n_patients, 64)
        ground_truth_severity = np.sin(np.linspace(0, np.pi, n_patients))
        
        predictions = model.predict_trajectory(patient_data, n_steps=12)
        severity = predictions['severity'].mean(axis=1)
        
        # Correlation with ground truth
        correlation = np.corrcoef(ground_truth_severity, severity)[0, 1]
        assert correlation > 0.7, f"Correlation {correlation} too low"
```

### 2. Robustness Tests

```python
def test_molecular_encoder_adversarial():
    """Test encoder robustness to similar molecules"""
    encoder = MolecularGraphEncoder()
    
    # Similar molecules should have similar embeddings
    aspirin_emb = encoder(encoder.smiles_to_graph('CC(=O)Oc1ccccc1C(=O)O')).squeeze()
    salicylate_emb = encoder(encoder.smiles_to_graph('O=C(O)c1ccccc1O')).squeeze()
    
    # Cosine similarity should be high
    similarity = torch.nn.functional.cosine_similarity(aspirin_emb, salicylate_emb, dim=0)
    assert similarity > 0.7, "Similar molecules should have similar embeddings"

def test_predictions_with_missing_data():
    """Test model handles missing values gracefully"""
    model = BindingAffinityPredictor()
    
    # Drug without protein sequence
    drug_data = torch.randn(1, 256)
    target_data = torch.zeros(1, 512)  # Zeros for missing data
    
    output = model(drug_data, target_data)
    assert not torch.isnan(output['ic50']).any(), "Model produces NaN with missing data"

def test_inference_stability():
    """Test consistency across multiple runs"""
    model = BindingAffinityPredictor.from_pretrained()
    drug_data = torch.randn(1, 256)
    target_data = torch.randn(1, 512)
    
    predictions = []
    model.eval()  # Turn off dropout
    with torch.no_grad():
        for _ in range(10):
            output = model(drug_data, target_data)
            predictions.append(output['ic50'].item())
    
    # Should be identical (no dropout)
    assert all(p == predictions[0] for p in predictions)
```

---

## Android Testing Strategy

### 1. Unit Tests

**File**: `android/app/src/test/java/com/neuroai/neurodrug/ViewModel.kt`

```kotlin
import androidx.arch.core.executor.testing.InstantTaskExecutorRule
import androidx.lifecycle.LiveData
import kotlinx.coroutines.test.StandardTestDispatcher
import org.junit.Rule
import org.junit.Test

class DrugViewModelTest {
    @get:Rule
    val instantExecutorRule = InstantTaskExecutorRule()

    private val testDispatcher = StandardTestDispatcher()

    @Test
    fun testLoadDrugs() {
        val viewModel = DrugViewModel(mockRepository)
        viewModel.drugs.observeForever { drugs ->
            assert(drugs.isNotEmpty())
        }
        viewModel.loadDrugs()
    }

    @Test
    fun testDrugSelection() {
        val viewModel = DrugViewModel(mockRepository)
        viewModel.selectDrug(1)
        assert(viewModel.selectedDrug.value?.id == 1)
    }

    @Test
    fun testErrorHandling() {
        val mockRepository = MockRepository(throwError = true)
        val viewModel = DrugViewModel(mockRepository)
        viewModel.loadDrugs()
        assert(viewModel.errorMessage.value != null)
    }
}
```

### 2. UI Tests (Compose)

**File**: `android/app/src/androidTest/java/com/neuroai/neurodrug/UITest.kt`

```kotlin
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createComposeRule
import org.junit.Rule
import org.junit.Test

class DashboardScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun testDashboardDisplaysDrugs() {
        composeTestRule.setContent {
            DashboardScreen(mockViewModel)
        }

        composeTestRule.onNodeWithText("Drugs").assertIsDisplayed()
        composeTestRule.onNodeWithTag("drug_list").assertIsDisplayed()
    }

    @Test
    fun testDrugSearch() {
        composeTestRule.setContent {
            DashboardScreen(mockViewModel)
        }

        composeTestRule.onNodeWithTag("search_input").performTextInput("Aspirin")
        composeTestRule.onNodeWithText("Aspirin").assertIsDisplayed()
    }

    @Test
    fun testNavigateToDrugDetail() {
        composeTestRule.setContent {
            DashboardScreen(mockViewModel)
        }

        composeTestRule.onNodeWithText("Aspirin").performClick()
        assert(mockViewModel.selectedDrug.value?.id == 1)
    }
}
```

---

## CI/CD Test Automation

### GitHub Actions Workflow

**File**: `.github/workflows/test.yml`

```yaml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r backend/requirements.txt
        pip install pytest pytest-cov pytest-django
    
    - name: Run migrations
      run: |
        cd backend
        python manage.py migrate
    
    - name: Run tests
      run: |
        cd backend
        pytest --cov=core --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        files: ./backend/coverage.xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Node
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install dependencies
      run: cd frontend && npm install
    
    - name: Run tests
      run: cd frontend && npm test
    
    - name: Build
      run: cd frontend && npm run build

  android-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up JDK
      uses: actions/setup-java@v3
      with:
        java-version: '17'
    
    - name: Run tests
      run: cd android && ./gradlew test
```

---

## Test Execution Commands

### Backend Testing

```bash
# Run all tests
cd backend
pytest

# Run specific test file
pytest core/tests/test_ml_modules.py

# Run with coverage report
pytest --cov=core --cov-report=html

# Run specific test class
pytest core/tests/test_ml_modules.py::TestMolecularRepresentation

# Run with verbose output
pytest -v

# Run with logging
pytest -v --log-cli-level=INFO

# Run performance tests
pytest -v -m performance
```

### Frontend Testing

```bash
# Run all React tests
npm test

# Watch mode (auto-rerun on file changes)
npm test -- --watch

# Coverage report
npm test -- --coverage

# Run E2E tests
npm run test:e2e

# Specific test file
npm test -- Dashboard.test.tsx
```

### ML Model Testing

```bash
# Run ML validation tests
cd backend
pytest core/tests/test_model_validation.py -v

# Validate specific model
pytest core/tests/test_model_validation.py::TestBindingAffinityBenchmark -v

# Run with detailed output
pytest -vv --tb=long
```

### Android Testing

```bash
# Unit tests
cd android
./gradlew test

# Instrumented tests (on device/emulator)
./gradlew connectedAndroidTest

# Specific test class
./gradlew test:testDebugUnitTest --tests com.neuroai.neurodrug.ViewModelTest

# Coverage
./gradlew test --coverage
```

---

## Test Coverage Goals

| Component | Target Coverage | Current | Status |
|-----------|-----------------|---------|--------|
| ML Modules | 85% | To be implemented | ⏳ |
| API Views | 80% | To be implemented | ⏳ |
| Models | 90% | To be implemented | ⏳ |
| React Components | 75% | To be implemented | ⏳ |
| Android ViewModels | 80% | To be implemented | ⏳ |
| **Overall** | **>80%** | TBD | ⏳ |

---

## Test Data Management

### Fixture Creation

```python
# backend/core/tests/fixtures.py
import factory
from core.models import Drug, Target

class DrugFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Drug
    
    name = factory.Faker('sentence', nb_words=2)
    smiles = 'CC'  # Ethane
    molecular_weight = factory.Faker('pydecimal', positive=True, max_digits=5)

class TargetFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Target
    
    name = factory.Faker('word')
    uniprot_id = factory.Faker('bothify', text='P?????')
```

### Test Database Isolation

```python
# All tests should use @pytest.mark.django_db decorator
@pytest.mark.django_db
def test_drug_creation():
    drug = DrugFactory()
    assert drug.id is not None
```

---

## Performance Testing

```python
# backend/core/tests/test_performance.py
import pytest
import time

@pytest.mark.performance
def test_api_endpoint_latency():
    """API should respond within 500ms"""
    start = time.time()
    response = client.get('/api/v1/drugs/')
    elapsed = time.time() - start
    
    assert elapsed < 0.5, f"API latency {elapsed}s exceeds 500ms target"

@pytest.mark.performance
def test_binding_prediction_speed():
    """Binding prediction should complete in <100ms"""
    model = BindingAffinityPredictor.from_pretrained()
    
    start = time.time()
    for _ in range(10):
        _ = model(torch.randn(1, 256), torch.randn(1, 512))
    avg_time = (time.time() - start) / 10
    
    assert avg_time < 0.1, f"Inference {avg_time}s exceeds 100ms target"
```

---

## Security Testing

```python
# backend/core/tests/test_security.py

def test_sql_injection_protection():
    """Test ORM prevents SQL injection"""
    malicious_input = "'; DROP TABLE drugs; --"
    
    # Should not execute DROP TABLE
    drugs = Drug.objects.filter(name=malicious_input)
    assert Drug.objects.count() > 0  # Table still exists

def test_csrf_protection():
    """Test CSRF tokens required"""
    response = client.post('/api/v1/drugs/', data={}, follow=True)
    
    # Should fail without CSRF token
    assert response.status_code in [403, 400]

def test_xss_protection():
    """Test XSS payload is escaped"""
    payload = '<script>alert("xss")</script>'
    drug = Drug.objects.create(name=payload, smiles='CC')
    
    response = client.get(f'/api/v1/drugs/{drug.id}/')
    assert '<script>' not in response.content.decode()
```

---

## Success Criteria

✅ **Unit Test Coverage**: >80% of all modules  
✅ **Integration Tests**: All API endpoints tested  
✅ **ML Validation**: Benchmarks achieved (AUC, RMSE, latency)  
✅ **UI Tests**: Critical user paths verified  
✅ **Security Tests**: OWASP Top 10 vulnerabilities checked  
✅ **Performance**: Response times < targets  
✅ **CI/CD**: Automated testing on every push  
✅ **Regression Prevention**: Test suite prevents breaking changes  

---

**Status**: Ready for Implementation  
**Next Step**: Create test files and integrate into CI/CD pipeline  
**Target Completion**: 2-3 weeks after ML implementation
