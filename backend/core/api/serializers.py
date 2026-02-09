"""
DRF Serializers for NeuroDegenRx API.
"""
from rest_framework import serializers
from core.models import (
    Drug, Target, DrugTarget, Pathway, PathwayTarget,
    DrugPathwayEffect, DiseaseState, DatasetProvenance
)


class DrugSerializer(serializers.ModelSerializer):
    """Basic drug serializer for list views."""
    
    class Meta:
        model = Drug
        fields = [
            'id', 'drugbank_id', 'chembl_id', 'name',
            'is_approved', 'molecular_weight', 'logp',
            'cns_mpo_score', 'cns_viable', 'pains_alerts',
        ]


class TargetSerializer(serializers.ModelSerializer):
    """Target serializer."""
    
    class Meta:
        model = Target
        fields = [
            'id', 'gene_symbol', 'gene_name', 'uniprot_id',
            'protein_name', 'protein_class', 'disease_relevance_score',
            'is_toxicity_associated', 'toxicity_categories',
            'brain_expression_level',
        ]


class DrugTargetSerializer(serializers.ModelSerializer):
    """Drug-Target interaction serializer."""
    target_gene_symbol = serializers.CharField(source='target.gene_symbol', read_only=True)
    target_name = serializers.CharField(source='target.protein_name', read_only=True)
    is_toxicity_associated = serializers.BooleanField(
        source='target.is_toxicity_associated', read_only=True
    )
    
    class Meta:
        model = DrugTarget
        fields = [
            'id', 'target', 'target_gene_symbol', 'target_name',
            'affinity_nm', 'affinity_type', 'activity_type',
            'confidence_score', 'evidence_level', 'source',
            'is_off_target', 'is_toxicity_associated',
        ]


class DrugDetailSerializer(serializers.ModelSerializer):
    """Detailed drug serializer with nested relationships."""
    target_interactions = DrugTargetSerializer(many=True, read_only=True)
    pathway_effects = serializers.SerializerMethodField()
    safety_summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Drug
        fields = [
            'id', 'drugbank_id', 'chembl_id', 'name', 'synonyms',
            'is_approved', 'approval_status', 'smiles',
            'molecular_weight', 'logp', 'hbd', 'hba', 'tpsa', 'pka',
            'rotatable_bonds', 'cns_mpo_score', 'cns_viable',
            'cns_score_explanation', 'pains_alerts', 'structural_alerts',
            'description', 'categories',
            'target_interactions', 'pathway_effects', 'safety_summary',
            'created_at', 'updated_at',
        ]
    
    def get_pathway_effects(self, obj):
        effects = obj.pathway_effects.select_related('pathway').all()[:10]
        return DrugPathwayEffectSerializer(effects, many=True).data
    
    def get_safety_summary(self, obj):
        """Generate safety summary from drug data."""
        warnings = []
        
        if not obj.cns_viable:
            warnings.append({
                'level': 'warning',
                'message': f'Limited CNS viability (MPO score: {obj.cns_mpo_score or "N/A"})',
            })
        
        if obj.pains_alerts > 0:
            warnings.append({
                'level': 'caution',
                'message': f'{obj.pains_alerts} PAINS alert(s) detected',
            })
        
        # Check off-target toxicity flags
        tox_targets = obj.target_interactions.filter(
            target__is_toxicity_associated=True
        ).count()
        if tox_targets > 0:
            warnings.append({
                'level': 'warning',
                'message': f'{tox_targets} interaction(s) with toxicity-associated targets',
            })
        
        return {
            'has_warnings': len(warnings) > 0,
            'warning_count': len(warnings),
            'warnings': warnings,
        }


class PathwaySerializer(serializers.ModelSerializer):
    """Pathway serializer."""
    target_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Pathway
        fields = [
            'id', 'pathway_id', 'name', 'description',
            'category', 'disease_relevance', 'activation_effect',
            'source', 'target_count',
        ]


class PathwayTargetSerializer(serializers.ModelSerializer):
    """Pathway-Target mapping serializer."""
    target_gene_symbol = serializers.CharField(source='target.gene_symbol', read_only=True)
    
    class Meta:
        model = PathwayTarget
        fields = [
            'id', 'target', 'target_gene_symbol', 'role',
            'influence_weight', 'evidence_level',
        ]


class DrugPathwayEffectSerializer(serializers.ModelSerializer):
    """Drug pathway effect serializer."""
    drug_name = serializers.CharField(source='drug.name', read_only=True)
    pathway_name = serializers.CharField(source='pathway.name', read_only=True)
    pathway_category = serializers.CharField(source='pathway.category', read_only=True)
    
    class Meta:
        model = DrugPathwayEffect
        fields = [
            'id', 'drug', 'drug_name', 'pathway', 'pathway_name',
            'pathway_category', 'perturbation_score', 'direction',
            'disease_impact', 'confidence', 'contributing_targets',
            'explanation', 'has_safety_concern', 'computed_at',
        ]


class DiseaseStateSerializer(serializers.ModelSerializer):
    """Disease state serializer."""
    
    class Meta:
        model = DiseaseState
        fields = [
            'id', 'name', 'description', 'disease_type',
            'parameters', 'baseline_trajectory', 'uncertainty_bounds',
            'simulation_config', 'is_default',
            'created_at', 'updated_at',
        ]


class SimulationRequestSerializer(serializers.Serializer):
    """Request body for simulation endpoint."""
    drug_id = serializers.IntegerField(required=False, allow_null=True)
    disease_state_id = serializers.IntegerField(required=False, allow_null=True)
    initial_parameters = serializers.DictField(
        child=serializers.FloatField(),
        required=False,
        default=dict,
    )
    time_steps = serializers.IntegerField(default=10, min_value=1, max_value=50)


class SimulationResponseSerializer(serializers.Serializer):
    """Response format for simulation endpoint."""
    baseline = serializers.DictField()
    intervention = serializers.DictField(allow_null=True)
    comparison = serializers.DictField()
    overall_assessment = serializers.CharField()
    caveats = serializers.ListField(child=serializers.CharField())


class DatasetProvenanceSerializer(serializers.ModelSerializer):
    """Dataset provenance serializer."""
    
    class Meta:
        model = DatasetProvenance
        fields = [
            'id', 'dataset_name', 'version', 'file_path',
            'ingested_at', 'record_count', 'error_count', 'notes',
        ]
