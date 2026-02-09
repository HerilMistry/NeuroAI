"""
DrugTarget model - represents drug-target binding relationships.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class DrugTarget(models.Model):
    """
    Represents a binding relationship between a drug and a target.
    
    Affinity values are in nM (nanomolar). Lower values = stronger binding.
    Confidence scores reflect data quality and source reliability.
    """
    
    drug = models.ForeignKey(
        'Drug',
        on_delete=models.CASCADE,
        related_name='target_interactions'
    )
    target = models.ForeignKey(
        'Target',
        on_delete=models.CASCADE,
        related_name='drug_interactions'
    )
    
    # Binding data
    affinity_nm = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Binding affinity in nM (Ki, Kd, or IC50)"
    )
    affinity_type = models.CharField(
        max_length=10,
        choices=[
            ('Ki', 'Ki'),
            ('Kd', 'Kd'),
            ('IC50', 'IC50'),
            ('EC50', 'EC50'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
    activity_type = models.CharField(
        max_length=50,
        choices=[
            ('inhibitor', 'Inhibitor'),
            ('agonist', 'Agonist'),
            ('antagonist', 'Antagonist'),
            ('modulator', 'Modulator'),
            ('binder', 'Binder'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
    
    # Confidence
    confidence_score = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Data confidence (0-1 scale)"
    )
    evidence_level = models.CharField(
        max_length=20,
        choices=[
            ('high', 'High - Direct experimental'),
            ('medium', 'Medium - Literature/curated'),
            ('low', 'Low - Inferred/predicted'),
        ],
        default='medium'
    )
    
    # Source tracking
    source = models.CharField(
        max_length=50,
        choices=[
            ('drugbank', 'DrugBank'),
            ('chembl', 'ChEMBL'),
            ('bindingdb', 'BindingDB'),
            ('curated', 'Manually Curated'),
        ],
        default='drugbank'
    )
    source_id = models.CharField(max_length=50, null=True, blank=True)
    pubmed_ids = models.JSONField(default=list, blank=True)
    
    # Off-target flag
    is_off_target = models.BooleanField(
        default=False,
        help_text="Flag: True if this is an off-target interaction"
    )
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['drug', 'target', 'source']
        ordering = ['affinity_nm']
        indexes = [
            models.Index(fields=['affinity_nm']),
            models.Index(fields=['confidence_score']),
        ]
    
    def __str__(self):
        affinity = f"{self.affinity_nm} nM" if self.affinity_nm else "unknown affinity"
        return f"{self.drug.name} → {self.target.gene_symbol} ({affinity})"
    
    @property
    def is_potent(self) -> bool:
        """Heuristic: affinity < 100 nM is considered potent."""
        return self.affinity_nm is not None and self.affinity_nm < 100
