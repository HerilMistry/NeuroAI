"""
Target model - represents biological targets (genes/proteins).
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Target(models.Model):
    """
    Represents a biological target (gene/protein) with disease relevance scoring.
    
    Disease relevance is computed from gene-disease association databases (DisGeNET).
    Toxicity flags are curated from known safety liabilities.
    """
    
    # Identifiers
    gene_symbol = models.CharField(max_length=50, unique=True, db_index=True)
    gene_name = models.CharField(max_length=500, null=True, blank=True)
    uniprot_id = models.CharField(max_length=20, null=True, blank=True, db_index=True)
    ensembl_id = models.CharField(max_length=30, null=True, blank=True)
    entrez_id = models.CharField(max_length=20, null=True, blank=True)
    
    # Protein info
    protein_name = models.CharField(max_length=500, null=True, blank=True)
    protein_class = models.CharField(max_length=200, null=True, blank=True)
    subcellular_location = models.JSONField(default=list, blank=True)
    
    # Disease association (from DisGeNET or curated)
    disease_associations = models.JSONField(
        default=list, blank=True,
        help_text="List of disease associations with scores"
    )
    disease_relevance_score = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Aggregated disease relevance (0-1 scale)"
    )
    
    # Safety/Toxicity flags (curated, NOT predicted)
    is_toxicity_associated = models.BooleanField(
        default=False,
        help_text="Known association with toxicity (e.g., hERG, hepatotoxicity)"
    )
    toxicity_categories = models.JSONField(
        default=list, blank=True,
        help_text="List of toxicity categories (e.g., 'cardiac', 'hepatic')"
    )
    toxicity_evidence = models.TextField(
        null=True, blank=True,
        help_text="Evidence/references for toxicity association"
    )
    
    # Promiscuity (for off-target detection)
    known_drug_count = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of known drugs targeting this protein"
    )
    is_promiscuous_target = models.BooleanField(
        default=False,
        help_text="Flag: True if target is bound by many chemically diverse drugs"
    )
    
    # Expression
    brain_expression_level = models.CharField(
        max_length=20,
        choices=[
            ('high', 'High'),
            ('medium', 'Medium'),
            ('low', 'Low'),
            ('not_detected', 'Not Detected'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
    
    # Metadata
    description = models.TextField(null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data_source = models.CharField(max_length=50, default='uniprot')
    
    class Meta:
        ordering = ['gene_symbol']
        indexes = [
            models.Index(fields=['disease_relevance_score']),
            models.Index(fields=['is_toxicity_associated']),
        ]
    
    def __str__(self):
        return f"{self.gene_symbol} ({self.protein_name or 'Unknown protein'})"
