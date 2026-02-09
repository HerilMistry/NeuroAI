from django.contrib import admin
from core.models import (
    Drug, Target, DrugTarget, Pathway, PathwayTarget,
    DrugPathwayEffect, DiseaseState, DatasetProvenance
)


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('drugbank_id', 'name', 'cns_mpo_score', 'cns_viable', 'is_approved')
    list_filter = ('cns_viable', 'is_approved')
    search_fields = ('drugbank_id', 'name', 'chembl_id')


@admin.register(Target)
class TargetAdmin(admin.ModelAdmin):
    list_display = ('gene_symbol', 'uniprot_id', 'is_toxicity_associated', 'disease_relevance_score')
    list_filter = ('is_toxicity_associated',)
    search_fields = ('gene_symbol', 'uniprot_id', 'gene_name')


@admin.register(DrugTarget)
class DrugTargetAdmin(admin.ModelAdmin):
    list_display = ('drug', 'target', 'affinity_nm', 'confidence_score', 'source')
    list_filter = ('source',)
    search_fields = ('drug__name', 'target__gene_symbol')


@admin.register(Pathway)
class PathwayAdmin(admin.ModelAdmin):
    list_display = ('pathway_id', 'name', 'category', 'disease_relevance')
    list_filter = ('category',)
    search_fields = ('pathway_id', 'name')


@admin.register(PathwayTarget)
class PathwayTargetAdmin(admin.ModelAdmin):
    list_display = ('pathway', 'target', 'role', 'evidence_level')
    list_filter = ('role', 'evidence_level')


@admin.register(DrugPathwayEffect)
class DrugPathwayEffectAdmin(admin.ModelAdmin):
    list_display = ('drug', 'pathway', 'perturbation_score', 'direction', 'confidence')
    list_filter = ('direction',)


@admin.register(DiseaseState)
class DiseaseStateAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


@admin.register(DatasetProvenance)
class DatasetProvenanceAdmin(admin.ModelAdmin):
    list_display = ('dataset_name', 'version', 'ingested_at', 'record_count')
    list_filter = ('dataset_name',)
