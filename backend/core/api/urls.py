"""
REST API URL configuration.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    DrugViewSet,
    TargetViewSet,
    PathwayViewSet,
    DrugPathwayEffectViewSet,
    DiseaseStateViewSet,
    SimulationView,
    SystemInfoView,
    BindingAffinityPredictionView,
    ToxicityAssessmentView,
    DrugResponsePredictionView,
    DemoMoleculeAnalysisView,
)

router = DefaultRouter()
router.register(r'drugs', DrugViewSet, basename='drug')
router.register(r'targets', TargetViewSet, basename='target')
router.register(r'pathways', PathwayViewSet, basename='pathway')
router.register(r'pathway-effects', DrugPathwayEffectViewSet, basename='pathway-effect')
router.register(r'disease-states', DiseaseStateViewSet, basename='disease-state')

urlpatterns = [
    path('', include(router.urls)),
    path('simulate/', SimulationView.as_view(), name='simulate'),
    path('system/', SystemInfoView.as_view(), name='system-info'),
    # Pre-trained model predictions
    path('predictions/binding-affinity/', BindingAffinityPredictionView.as_view(), name='binding-affinity'),
    path('predictions/toxicity/', ToxicityAssessmentView.as_view(), name='toxicity'),
    path('predictions/drug-response/', DrugResponsePredictionView.as_view(), name='drug-response'),
    path('predictions/molecule-analysis/', DemoMoleculeAnalysisView.as_view(), name='molecule-analysis'),
]
