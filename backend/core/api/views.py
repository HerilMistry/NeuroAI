"""
DRF ViewSets and Views for NeuroDegenRx API.
"""
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django_filters.rest_framework import DjangoFilterBackend

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
            'platform': 'NeuroDegenRx',
            'version': '1.0.0',
            'description': (
                'A mechanism-aware decision support platform for '
                'neurodegenerative drug discovery. NOT a clinical decision system.'
            ),
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
                'This platform does NOT provide clinical predictions.',
                'All simulations are for mechanistic exploration only.',
                'Results should be reviewed by domain experts.',
                'No diagnostic or treatment recommendations are made.',
            ],
        })
