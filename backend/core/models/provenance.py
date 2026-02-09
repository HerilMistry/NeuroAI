"""
DatasetProvenance model - tracks data source versions and ingestion.
"""
from django.db import models


class DatasetProvenance(models.Model):
    """
    Tracks the provenance of ingested datasets.
    
    Every data ingestion creates a provenance record for:
    - Reproducibility
    - Auditability
    - Version tracking
    """
    
    dataset_name = models.CharField(
        max_length=100,
        choices=[
            ('drugbank', 'DrugBank'),
            ('chembl', 'ChEMBL'),
            ('disgenet', 'DisGeNET'),
            ('uniprot', 'UniProt'),
            ('kegg', 'KEGG'),
            ('reactome', 'Reactome'),
            ('curated', 'Manually Curated'),
        ]
    )
    
    version = models.CharField(max_length=50)
    file_path = models.CharField(max_length=500, null=True, blank=True)
    file_hash = models.CharField(
        max_length=64, null=True, blank=True,
        help_text="SHA-256 hash of source file"
    )
    
    ingested_at = models.DateTimeField(auto_now_add=True)
    ingested_by = models.CharField(max_length=100, null=True, blank=True)
    
    record_count = models.IntegerField(
        default=0,
        help_text="Number of records ingested"
    )
    error_count = models.IntegerField(
        default=0,
        help_text="Number of records that failed to import"
    )
    
    notes = models.TextField(null=True, blank=True)
    
    class Meta:
        ordering = ['-ingested_at']
        verbose_name_plural = 'Dataset Provenance Records'
    
    def __str__(self):
        return f"{self.dataset_name} v{self.version} ({self.ingested_at.date()})"
