# NeuroAI Quick Start & Deployment Guide

**Version**: 1.0.0  
**Date**: 2024  
**Status**: Ready for Production Deployment

---

## 🚀 5-Minute Quick Start

### Prerequisites
- macOS/Linux/Windows with Docker installed
- Python 3.9+ (for local development)
- Node.js 16+ (for frontend development)
- Android SDK (optional, for mobile development)

### Option A: Docker Compose (Recommended)

```bash
# 1. Clone repository
git clone <repo-url>
cd NeuroAI

# 2. Create environment file
cat > .env << EOF
# Django
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://neurodegenrx:neurodegenrx@postgres:5432/neurodegenrx

# Redis
REDIS_URL=redis://redis:6379/0

# MedGemma API
MEDGEMMA_API_KEY=your-google-api-key

# Email (optional)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EOF

# 3. Launch full stack
docker-compose -f docker-compose.prod.yml up -d

# 4. Verify services are running
docker-compose ps

# 5. Access services
echo "✅ Frontend:  http://localhost:5173"
echo "✅ API:       http://localhost:8000"
echo "✅ Flower:    http://localhost:5555"
echo "✅ pgAdmin:   http://localhost:5050"
```

**Wait 30 seconds for services to initialize.**

### Option B: Local Development

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Database
python manage.py migrate
python manage.py seed_sample_data  # Load sample data

# Start server
python manage.py runserver 0.0.0.0:8000

# In a new terminal - Frontend
cd frontend
npm install
npm run dev

# In another terminal - Celery (for async tasks)
cd backend
celery -A neurodegenrx_backend worker -l info

# In another terminal - Celery Beat (for scheduled tasks)
celery -A neurodegenrx_backend beat -l info
```

---

## 📋 Detailed Setup Guide

### Step 1: Environment Configuration

Create `.env` file in project root:

```bash
# Core Django Settings
DJANGO_SECRET_KEY=django-insecure-change-this-in-production-!@#$%^&*(
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,api.example.com

# Database Configuration
DATABASE_URL=postgresql://neurodegenrx:neurodegenrx@localhost:5432/neurodegenrx
# OR with Docker: postgresql://neurodegenrx:neurodegenrx@postgres:5432/neurodegenrx

# Redis Cache & Task Broker
REDIS_URL=redis://localhost:6379/0
# OR with Docker: redis://redis:6379/0

# MedGemma API (Required for medical reasoning)
MEDGEMMA_API_KEY=your-google-api-key-from-makersuite.google.com

# Optional: Other LLM Providers
OPENAI_API_KEY=your-openai-key-optional
ANTHROPIC_API_KEY=your-anthropic-key-optional

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/neurodegenrx.log
```

### Step 2: Database Setup

```bash
# With Docker Compose (automatic)
docker-compose -f docker-compose.prod.yml up -d postgres redis

# With local PostgreSQL
psql postgres
CREATE DATABASE neurodegenrx;
CREATE USER neurodegenrx WITH PASSWORD 'neurodegenrx';
ALTER ROLE neurodegenrx SET client_encoding TO 'utf8';
ALTER ROLE neurodegenrx SET default_transaction_isolation TO 'read committed';
ALTER ROLE neurodegenrx SET default_transaction_deferrable TO on;
ALTER ROLE neurodegenrx SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE neurodegenrx TO neurodegenrx;
\c neurodegenrx
CREATE EXTENSION IF NOT EXISTS pgvector;
```

### Step 3: Backend Initialization

```bash
cd backend

# Apply migrations
python manage.py migrate

# Create superuser (for admin)
python manage.py createsuperuser

# Load sample data
python manage.py seed_sample_data

# Collect static files (production)
python manage.py collectstatic --noinput

# Verify setup
python manage.py check
python manage.py test core.tests.test_ml_modules --verbosity=2
```

### Step 4: Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Development server
npm run dev          # Runs on http://localhost:5173

# Production build
npm run build        # Creates optimized bundle
npm run preview      # Preview production build
```

### Step 5: Android Build

```bash
cd android

# Build APK
./gradlew assembleDebug           # Unoptimized APK
./gradlew bundleRelease           # Optimized bundle for Play Store

# Build options
./gradlew assembleRelease         # Optimized APK for production

# Automated testing
./gradlew test                    # Run unit tests
./gradlew connectedAndroidTest    # Run instrumented tests

# Install on device
adb install -r app/build/outputs/apk/debug/app-debug.apk

# View logs
adb logcat | grep NeuroAI
```

---

## 🔧 Service Management

### Docker Compose Commands

```bash
# View logs from all services
docker-compose -f docker-compose.prod.yml logs -f

# View logs from specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Stop all services
docker-compose -f docker-compose.prod.yml down

# Restart a service
docker-compose -f docker-compose.prod.yml restart backend

# Execute command in container
docker-compose -f docker-compose.prod.yml exec backend python manage.py shell

# View resource usage
docker-compose -f docker-compose.prod.yml stats
```

### Service Health Checks

```bash
# Check if all services are healthy
curl http://localhost:8000/api/v1/health/

# API status
curl http://localhost:8000/api/v1/status/

# Database connection
docker-compose exec backend python manage.py dbshell

# Redis connection
docker-compose exec redis redis-cli ping

# Celery status
docker-compose exec celery celery -A neurodegenrx_backend inspect active
```

---

## 📊 Testing

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific module tests
pytest core/tests/test_molecular_representations.py

# Run with coverage
pytest --cov=core --cov-report=html

# Run specific test case
pytest core/tests/test_ml_modules.py::TestMolecularRepresentation::test_smiles_to_embedding
```

### Frontend Tests

```bash
cd frontend

# Run React tests
npm run test

# Run with coverage
npm run test:coverage

# E2E testing
npm run test:e2e
```

### ML Model Validation

```bash
cd backend

# Validate molecular encoder
python -c "from core.ml.molecular_representations import MolecularRepresentationPipeline; p = MolecularRepresentationPipeline(); print(p.validate())"

# Test binding predictor
python -c "from core.ml.target_engagement import BindingAffinityPredictor; b = BindingAffinityPredictor.from_pretrained(); print('Loaded successfully')"

# Validate disease model
python core/ml/disease_models.py
```

---

## 🚢 Production Deployment

### Pre-Deployment Checklist

```bash
# Security
- [ ] Change all default passwords
- [ ] Update DJANGO_SECRET_KEY with cryptographically secure value
- [ ] Set DEBUG=False in .env
- [ ] Configure ALLOWED_HOSTS with your domain
- [ ] Enable HTTPS/SSL certificates
- [ ] Configure CORS properly (not '*')

# Database
- [ ] Run migrations
- [ ] Create database backups
- [ ] Configure automated backup schedule
- [ ] Test disaster recovery procedure

# Static Files
- [ ] Run collectstatic
- [ ] Configure CDN for static assets (optional)
- [ ] Set proper Cache-Control headers

# API
- [ ] Review API authentication
- [ ] Configure rate limiting
- [ ] Set up API monitoring/alerting
- [ ] Test all endpoints

# Performance
- [ ] Enable caching (Redis)
- [ ] Configure database connection pooling
- [ ] Enable gzip compression
- [ ] Set up CDN for frontend assets

# Monitoring
- [ ] Set up Prometheus metrics
- [ ] Configure Grafana dashboards
- [ ] Set up logging (ELK or equivalent)
- [ ] Configure error tracking (Sentry)

# Compliance
- [ ] HIPAA BAA (if handling patient data)
- [ ] GDPR Data Processing Agreement
- [ ] Vulnerability scanning
- [ ] Security audit
```

### Kubernetes Deployment (Advanced)

```bash
# Generate Kubernetes manifests from Docker Compose
kompose convert -f docker-compose.prod.yml -o k8s/

# Deploy to cluster
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl describe pod <pod-name>

# View logs
kubectl logs -f deployment/backend

# Scale backend workers
kubectl scale deployment backend --replicas=3

# Update image version
kubectl set image deployment/backend backend=neuroai:v1.1.0
```

---

## 🔍 Monitoring & Debugging

### System Monitoring

```bash
# View system metrics
docker stats

# Check API performance
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/drugs/

# Monitor Celery tasks
docker-compose exec flower cat /logs/flower.log

# Database query performance
docker-compose exec backend python manage.py shell
>>> from django.db import connection
>>> from django.test.utils import CaptureQueriesContext
>>> with CaptureQueriesContext(connection) as context:
...     # Your query here
>>> print(f"Executed {len(context)} queries in {context.duration}ms")
```

### Debugging Common Issues

```bash
# Issue: API returns 500 error
Solution: Check logs with `docker-compose logs backend` 
          and check Django error page at http://localhost:8000

# Issue: Celery tasks not running
Solution: Check Redis connection
          docker-compose exec redis redis-cli ping
          Verify Celery worker is running
          docker-compose ps | grep celery

# Issue: Database connection errors
Solution: Verify PostgreSQL is running
          Verify DATABASE_URL in .env
          Check pgAdmin at http://localhost:5050

# Issue: MedGemma API errors
Solution: Verify MEDGEMMA_API_KEY is set correctly
          Test API key: curl -H "Authorization: Bearer $MEDGEMMA_API_KEY" ...
          Check API quota at makersuite.google.com

# Issue: Mobile app won't connect
Solution: Verify api.neuroai.example.com resolves on device
          Check firewall rules
          Verify SSL certificate is valid
          Check API logs: docker-compose logs backend
```

---

## 📈 Performance Optimization

### Database Optimization

```sql
-- Add indexes for common queries
CREATE INDEX idx_drug_name ON drug(name);
CREATE INDEX idx_target_uniprot ON target(uniprot_id);
CREATE INDEX idx_pathway_kegg ON pathway(kegg_id);
CREATE INDEX idx_disease_state_patient ON disease_state(patient_id);

-- Analyze query performance
EXPLAIN ANALYZE SELECT * FROM drug WHERE name = 'Aspirin';

-- Vacuum and analyze
VACUUM ANALYZE;
```

### Redis Caching

```bash
# Monitor cache
docker-compose exec redis redis-cli

redis-cli> INFO stats
redis-cli> KEYS "*"
redis-cli> TTL <key>
redis-cli> DEL <key>  # Clear specific cache entry
redis-cli> FLUSHDB    # Clear all cache (careful!)
```

### Frontend Optimization

```bash
# Build analysis
npm run build:analyze

# Bundle size reporting
npm run build --report

# Performance audit
npm audit
```

---

## 🔐 Security Hardening

### Firewall Configuration

```bash
# Enable firewall (if on Linux)
sudo ufw enable
sudo ufw allow 22/tcp   # SSH
sudo ufw allow 80/tcp   # HTTP
sudo ufw allow 443/tcp  # HTTPS
sudo ufw deny 5432/tcp  # PostgreSQL (only allow from app server)

# macOS equivalent
sudo pfctl -e
```

### HTTPS/SSL Setup

```bash
# Generate self-signed certificate (development only)
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Configure NGINX or reverse proxy with certificate
# Then update django settings:
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Rate Limiting

```python
# In Django settings
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon': '100/hour',
        'user': '1000/hour'
    }
}
```

---

## 📚 Useful Resources

### Official Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev/)
- [Kotlin Documentation](https://kotlinlang.org/docs/)
- [PyTorch Documentation](https://pytorch.org/docs/)
- [Docker Documentation](https://docs.docker.com/)

### Medical AI Resources
- [MedGemma Model Card](https://ai.google.dev/site/medialab/medical-research)
- [HIPAA Compliance Guide](https://www.hhs.gov/hipaa/)
- [FDA Software Validation](https://www.fda.gov/media/161644)
- [CE MDR Requirements](https://ec.europa.eu/health/md_new_rules_en)

### Machine Learning References
- Schütt et al. (2018) - SchNet: A continuous-filter convolutional neural network for modeling quantum interactions
- Öztürk et al. (2020) - GraphDTA: deep learning approach for drug-target binding affinity prediction
- Chen et al. (2018) - Neural Ordinary Differential Equations
- Lewis et al. (2020) - Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

---

## ⚡ Common Commands Reference

```bash
# Development
npm run dev              # Frontend dev server
python manage.py runserver  # Django dev server
celery worker -l info   # Celery worker

# Testing
npm run test            # Frontend tests
pytest                  # Backend tests
./gradlew test          # Android tests

# Deployment
docker-compose up -d    # Start services
docker-compose down     # Stop services
kubernetes apply        # Deploy to Kubernetes

# Database
python manage.py migrate           # Apply migrations
python manage.py makemigrations    # Create migrations
python manage.py shell             # Django shell

# Utilities
python manage.py collectstatic     # Gather static files
npm run build                      # Build frontend
./gradlew assembleRelease          # Build Android APK
```

---

## 🆘 Support

### Getting Help

1. **Check Documentation**: Start with [TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)
2. **Review Logs**: `docker-compose logs <service>`
3. **Test Connections**: Use provided health check endpoints
4. **Check References**: See [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md) for citations
5. **Community**: Check GitHub issues for similar problems

### Reporting Issues

When reporting issues, include:
- System information (OS, Docker version, Python version)
- Error logs (from `docker-compose logs`)
- Steps to reproduce
- Expected vs. actual behavior
- Relevant configuration (without secrets)

---

## ✅ Verification Checklist

After deployment, verify:

```bash
# API Availability
curl http://localhost:8000/api/v1/health/

# Database Connection
docker-compose exec backend python manage.py dbshell <<< "SELECT 1"

# Redis Cache
docker-compose exec redis redis-cli ping

# Frontend Access
curl http://localhost:5173/

# Celery Workers
docker-compose exec celery celery -A neurodegenrx_backend inspect active

# MedGemma Integration
docker-compose exec backend python manage.py shell <<< "from core.ml.medgemma_service import MedGemmaService; print('Loaded')"

# File Permissions
ls -la backend/media/
ls -la frontend/dist/
```

---

**Status**: ✅ Ready for deployment  
**Last Updated**: 2024  
**Support**: See TECHNICAL_DOCUMENTATION.md for detailed information
