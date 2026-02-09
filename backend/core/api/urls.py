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
]
