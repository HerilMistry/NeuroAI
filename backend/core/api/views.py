"""
DRF ViewSets and Views for NeuroAI API.

Uses only pre-trained models for predictions:
- GraphDTA for binding affinity
- MedGemma for toxicity assessment and validation
- ESM-2 for protein embeddings
- RDKit for molecular features
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend
import logging

from core.models import (
    Drug, Target, DrugTarget, Pathway, PathwayTarget,
    DrugPathwayEffect, DiseaseState, DatasetProvenance
)
from .serializers import (
    DrugSerializer, DrugDetailSerializer, TargetSerializer,
    PathwaySerializer, PathwayTargetSerializer, DrugPathwayEffectSerializer,
    DiseaseStateSerializer, SimulationRequestSerializer,
    SimulationResponseSerializer, DatasetProvenanceSerializer,
)
from core.simulations import run_simulation

# Import real ML models with graceful fallback for development
try:
    from core.ml.inference import get_unified_predictor
    ML_AVAILABLE = True
    logger = logging.getLogger(__name__)
except ImportError as e:
    ML_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning(f"ML models not available: {e}. Using mock predictions for development.")


class DrugViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for drugs.
    
    list: Returns paginated list of drugs with basic info.
    retrieve: Returns detailed drug info with targets and pathway effects.
    """
    queryset = Drug.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['cns_viable', 'is_approved']
    search_fields = ['name', 'drugbank_id', 'chembl_id']
    ordering_fields = ['name', 'cns_mpo_score', 'molecular_weight']
    ordering = ['name']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DrugDetailSerializer
        return DrugSerializer

    @action(detail=True, methods=['get'])
    def mechanism_summary(self, request, pk=None):
        """
        Returns MedGemma-generated mechanism summary for a drug.
        """
        from core.medgemma.inference import summarize_drug_mechanism
        drug = self.get_object()
        description = drug.synonyms[0] if drug.synonyms else drug.name
        summary = summarize_drug_mechanism(drug.name, description)
        return Response({
            'drug': drug.name,
            'mechanism_summary': summary,
        })
    
    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'retrieve':
            qs = qs.prefetch_related(
                'target_interactions__target',
                'pathway_effects__pathway',
            )
        return qs
    
    @action(detail=True, methods=['get'])
    def targets(self, request, pk=None):
        """Get all target interactions for a drug."""
        drug = self.get_object()
        interactions = drug.target_interactions.select_related('target').all()
        from .serializers import DrugTargetSerializer
        serializer = DrugTargetSerializer(interactions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def pathway_effects(self, request, pk=None):
        """Get all pathway effects for a drug."""
        drug = self.get_object()
        effects = drug.pathway_effects.select_related('pathway').all()
        serializer = DrugPathwayEffectSerializer(effects, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def cns_viable(self, request):
        """Get only CNS-viable drugs."""
        drugs = self.get_queryset().filter(cns_viable=True)
        page = self.paginate_queryset(drugs)
        if page is not None:
            serializer = DrugSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = DrugSerializer(drugs, many=True)
        return Response(serializer.data)


class TargetViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for targets."""
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_toxicity_associated', 'brain_expression_level']
    search_fields = ['gene_symbol', 'gene_name', 'protein_name']
    ordering_fields = ['gene_symbol', 'disease_relevance_score']
    ordering = ['gene_symbol']
    
    @action(detail=True, methods=['get'])
    def drugs(self, request, pk=None):
        """Get all drugs that interact with this target."""
        target = self.get_object()
        interactions = target.drug_interactions.select_related('drug').all()
        data = [{
            'drug_id': i.drug.id,
            'drug_name': i.drug.name,
            'drugbank_id': i.drug.drugbank_id,
            'affinity_nm': i.affinity_nm,
            'activity_type': i.activity_type,
        } for i in interactions]
        return Response(data)


class PathwayViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for pathways."""
    serializer_class = PathwaySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['category', 'disease_relevance']
    search_fields = ['name', 'pathway_id']
    
    def get_queryset(self):
        return Pathway.objects.annotate(target_count=Count('targets'))
    
    @action(detail=True, methods=['get'])
    def targets(self, request, pk=None):
        """Get all targets in this pathway."""
        pathway = self.get_object()
        mappings = pathway.targets.select_related('target').all()
        serializer = PathwayTargetSerializer(mappings, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def drug_effects(self, request, pk=None):
        """Get all drug effects on this pathway."""
        pathway = self.get_object()
        effects = pathway.drug_effects.select_related('drug').all()
        serializer = DrugPathwayEffectSerializer(effects, many=True)
        return Response(serializer.data)


class DrugPathwayEffectViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for drug pathway effects."""
    queryset = DrugPathwayEffect.objects.select_related('drug', 'pathway').all()
    serializer_class = DrugPathwayEffectSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['direction', 'disease_impact', 'has_safety_concern']
    ordering_fields = ['perturbation_score', 'confidence']
    ordering = ['-perturbation_score']


class DiseaseStateViewSet(viewsets.ModelViewSet):
    """API endpoint for disease states."""
    queryset = DiseaseState.objects.all()
    serializer_class = DiseaseStateSerializer
    
    @action(detail=False, methods=['get'])
    def default(self, request):
        """Get the default disease state."""
        default = self.get_queryset().filter(is_default=True).first()
        if default:
            serializer = self.get_serializer(default)
            return Response(serializer.data)
        
        # Return default parameters if no default state
        return Response({
            'id': None,
            'name': 'Default State',
            'parameters': DiseaseState.get_default_parameters(),
            'is_default': True,
        })


class SimulationView(APIView):
    """
    Run disease progression simulation.
    
    POST /api/v1/simulate/
    
    Body:
    - drug_id: Optional drug to simulate
    - disease_state_id: Optional disease state to use
    - initial_parameters: Optional custom initial state
    - time_steps: Number of simulation steps (default 10)
    
    Returns baseline and intervention trajectories with comparison.
    
    WARNING: This is a mechanistic exploration tool, NOT a clinical prediction.
    """
    
    def post(self, request):
        serializer = SimulationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        drug_id = data.get('drug_id')
        disease_state_id = data.get('disease_state_id')
        initial_params = data.get('initial_parameters', {})
        time_steps = data.get('time_steps', 10)
        
        # Get initial state
        if disease_state_id:
            try:
                state = DiseaseState.objects.get(id=disease_state_id)
                initial_params = {**state.parameters, **initial_params}
            except DiseaseState.DoesNotExist:
                pass
        
        # Get drug pathway effects
        pathway_effects = None
        drug_name = 'Intervention'
        
        if drug_id:
            try:
                drug = Drug.objects.get(id=drug_id)
                drug_name = drug.name
                effects = drug.pathway_effects.select_related('pathway').all()
                pathway_effects = [{
                    'pathway_category': e.pathway.category,
                    'perturbation_score': e.perturbation_score,
                    'direction': e.direction,
                } for e in effects]
            except Drug.DoesNotExist:
                return Response(
                    {'error': 'Drug not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Run simulation
        result = run_simulation(
            initial_state=initial_params or None,
            pathway_effects=pathway_effects,
            time_steps=time_steps,
            drug_name=drug_name,
        )
        
        # Format response
        response_data = {
            'baseline': {
                'label': result.baseline.label,
                'time_steps': result.baseline.time_steps,
                'trajectory': [
                    {
                        'time_step': pt.time_step,
                        'parameters': pt.parameters,
                        'uncertainty': pt.uncertainty,
                    }
                    for pt in result.baseline.trajectory
                ],
                'final_state': result.baseline.final_state,
                'key_changes': result.baseline.key_changes,
                'explanation': result.baseline.explanation,
            },
            'intervention': None,
            'comparison': result.comparison,
            'overall_assessment': result.overall_assessment,
            'caveats': result.caveats,
        }
        
        if result.intervention:
            response_data['intervention'] = {
                'label': result.intervention.label,
                'time_steps': result.intervention.time_steps,
                'trajectory': [
                    {
                        'time_step': pt.time_step,
                        'parameters': pt.parameters,
                        'uncertainty': pt.uncertainty,
                    }
                    for pt in result.intervention.trajectory
                ],
                'final_state': result.intervention.final_state,
                'key_changes': result.intervention.key_changes,
                'explanation': result.intervention.explanation,
            }
        
        return Response(response_data)


class SystemInfoView(APIView):
    """System information and data summary."""
    
    def get(self, request):
        return Response({
            'platform': 'NeuroAI',
            'version': '2.0.0',
            'description': (
                'AI-powered drug discovery platform using pre-trained models. '
                'Combines molecular predictions with medical reasoning via MedGemma.'
            ),
            'ml_models': {
                'binding_affinity': 'GraphDTA (pre-trained)',
                'protein_embeddings': 'ESM-2-33M (Meta)',
                'toxicity_assessment': 'MedGemma-7B (Google)',
                'molecular_features': 'RDKit + Morgan fingerprints + ChemBERTA',
                'reasoning': 'MedGemma-7B (medical reasoning)',
            },
            'statistics': {
                'drug_count': Drug.objects.count(),
                'target_count': Target.objects.count(),
                'pathway_count': Pathway.objects.count(),
                'cns_viable_drugs': Drug.objects.filter(cns_viable=True).count(),
            },
            'data_sources': list(
                DatasetProvenance.objects.values_list('dataset_name', flat=True).distinct()
            ),
            'disclaimers': [
                'This platform uses pre-trained ML models for predictions.',
                'All predictions are exploratory and NOT clinically validated.',
                'Results should be reviewed by domain experts.',
                'No diagnostic or treatment recommendations are made.',
            ],
        })


class BindingAffinityPredictionView(APIView):
    """
    Predict drug-target binding affinity using GraphDTA.
    
    POST /api/v1/predictions/binding-affinity/
    
    Body:
    {
        "molecule_smiles": "CCO",
        "target_name": "TNF-alpha",
        "target_sequence": "MGSSDQ..." (optional)
    }
    
    Returns:
    {
        "molecule_analysis": {...},
        "binding_affinity": {
            "target": "TNF-alpha",
            "binding_score": 7.5,
            "confidence": "high",
            "method": "GraphDTA (pre-trained)",
            "reasoning": "..."
        },
        "status": "success"
    }
    """
    
    def post(self, request):
        try:
            molecule_smiles = request.data.get('molecule_smiles')
            target_name = request.data.get('target_name', 'Unknown Target')
            target_sequence = request.data.get('target_sequence')
            
            if not molecule_smiles:
                return Response(
                    {'error': 'molecule_smiles is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get predictor
            predictor = get_unified_predictor()
            
            # Predict binding affinity
            binding = predictor.predict_binding_affinity(
                molecule_smiles,
                target_name,
                target_sequence=target_sequence,
                validate_with_medgemma=True
            )
            
            # Analyze molecule
            mol_analysis = predictor.analyze_molecule(molecule_smiles)
            
            return Response({
                'molecule_analysis': mol_analysis.to_dict(),
                'binding_affinity': binding.to_dict(),
                'status': 'success',
                'model_info': {
                    'method': 'GraphDTA (pre-trained weights)',
                    'paper': 'Öztürk et al., 2020',
                    'validation': 'MedGemma medical reasoning',
                }
            })
            
        except Exception as e:
            logger.error(f"Binding affinity prediction error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ToxicityAssessmentView(APIView):
    """
    Assess molecular toxicity using MedGemma.
    
    POST /api/v1/predictions/toxicity/
    
    Body:
    {
        "molecule_smiles": "CCO",
        "molecule_name": "Ethanol" (optional)
    }
    
    Returns:
    {
        "toxicity": {
            "molecule": "Ethanol",
            "toxicity_risk": "low",
            "mechanism": "...",
            "confidence": "medium",
            "reasoning": "..."
        },
        "status": "success"
    }
    """
    
    def post(self, request):
        try:
            molecule_smiles = request.data.get('molecule_smiles')
            molecule_name = request.data.get('molecule_name', 'Unknown')
            
            if not molecule_smiles:
                return Response(
                    {'error': 'molecule_smiles is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get predictor
            predictor = get_unified_predictor()
            
            # Assess toxicity
            toxicity = predictor.assess_toxicity(molecule_smiles, molecule_name)
            
            return Response({
                'toxicity': toxicity.to_dict(),
                'status': 'success',
                'model': 'MedGemma-7B (medical reasoning)'
            })
            
        except Exception as e:
            logger.error(f"Toxicity assessment error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DrugResponsePredictionView(APIView):
    """
    Comprehensive drug response prediction combining multiple models.
    
    POST /api/v1/predictions/drug-response/
    
    Body:
    {
        "molecule_smiles": "CCO",
        "target_name": "TNF-alpha",
        "target_sequence": "MGSSDQ..." (optional),
        "disease_context": "Neuroinflammation" (optional)
    }
    
    Returns comprehensive assessment including:
    - Molecular analysis
    - Binding affinity
    - Toxicity
    - Overall recommendation
    """
    
    def post(self, request):
        try:
            molecule_smiles = request.data.get('molecule_smiles')
            target_name = request.data.get('target_name', 'Unknown')
            disease_context = request.data.get('disease_context')
            
            if not molecule_smiles:
                return Response(
                    {'error': 'molecule_smiles is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get predictor
            predictor = get_unified_predictor()
            
            # Comprehensive prediction
            result = predictor.predict_drug_response(
                molecule_smiles,
                target_name,
                disease_context=disease_context
            )
            
            return Response({
                'drug_response_prediction': result,
                'status': 'success',
                'models_used': [
                    'GraphDTA (binding affinity)',
                    'MedGemma-7B (toxicity, reasoning)',
                    'ESM-2 (protein embeddings)',
                    'RDKit (molecular features)',
                ]
            })
            
        except Exception as e:
            logger.error(f"Drug response prediction error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class DemoMoleculeAnalysisView(APIView):
    """
    Quick molecular analysis without binding/toxicity predictions.
    
    POST /api/v1/predictions/molecule-analysis/
    
    Body:
    {
        "molecule_smiles": "CCO"
    }
    """
    
    def post(self, request):
        try:
            molecule_smiles = request.data.get('molecule_smiles')
            
            if not molecule_smiles:
                return Response(
                    {'error': 'molecule_smiles is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            predictor = get_unified_predictor()
            analysis = predictor.analyze_molecule(molecule_smiles)
            
            return Response({
                'analysis': analysis.to_dict(),
                'status': 'success'
            })
            
        except Exception as e:
            logger.error(f"Molecule analysis error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
