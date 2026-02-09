"""
DrugPathwayEffect model - represents computed perturbation effects.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class DrugPathwayEffect(models.Model):
    """
    Stores computed perturbation effects of drugs on pathways.
    
    This is a derived/computed model. Effects are calculated by:
    1. Aggregating drug-target interactions
    2. Mapping targets to pathways
    3. Computing directional (+/-) perturbation scores
    
    All computation logic is in core.logic.perturbation.
    """
    
    drug = models.ForeignKey(
        'Drug',
        on_delete=models.CASCADE,
        related_name='pathway_effects'
    )
    pathway = models.ForeignKey(
        'Pathway',
        on_delete=models.CASCADE,
        related_name='drug_effects'
    )
    
    # Computed perturbation score
    perturbation_score = models.FloatField(
        validators=[MinValueValidator(-1), MaxValueValidator(1)],
        help_text="Normalized perturbation magnitude (-1 to +1)"
    )
    
    direction = models.CharField(
        max_length=20,
        choices=[
            ('activation', 'Activation (+)'),
            ('inhibition', 'Inhibition (-)'),
            ('mixed', 'Mixed Effects'),
            ('neutral', 'Neutral/Minimal'),
        ],
        default='neutral'
    )
    
    # Confidence in the computed effect
    confidence = models.FloatField(
        default=0.5,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text="Confidence in perturbation estimate (0-1)"
    )
    
    # Interpretation relative to disease
    disease_impact = models.CharField(
        max_length=20,
        choices=[
            ('beneficial', 'Potentially Beneficial'),
            ('detrimental', 'Potentially Detrimental'),
            ('uncertain', 'Uncertain'),
            ('neutral', 'Neutral'),
        ],
        default='uncertain',
        help_text="Hypothetical impact on disease (NOT a prediction)"
    )
    
    # Explainability: which targets drive this effect?
    contributing_targets = models.JSONField(
        default=list, blank=True,
        help_text="List of {target_id, gene_symbol, contribution} objects"
    )
    
    explanation = models.TextField(
        null=True, blank=True,
        help_text="Human-readable explanation of the computed effect"
    )
    
    # Computation metadata
    computation_version = models.CharField(max_length=20, default='1.0')
    computed_at = models.DateTimeField(auto_now=True)
    
    # Flags
    has_safety_concern = models.BooleanField(
        default=False,
        help_text="Flag: True if any contributing target has toxicity association"
    )
    
    class Meta:
        unique_together = ['drug', 'pathway']
        ordering = ['-perturbation_score']
        indexes = [
            models.Index(fields=['perturbation_score']),
            models.Index(fields=['disease_impact']),
        ]
    
    def __str__(self):
        return f"{self.drug.name} → {self.pathway.name} ({self.direction})"
