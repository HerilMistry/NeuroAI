"""
Pathway and PathwayTarget models - represent disease-relevant biological pathways.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Pathway(models.Model):
    """
    Represents a curated biological pathway relevant to neurodegeneration.
    
    Pathways are sourced from KEGG, Reactome, or manually curated.
    Disease relevance is assigned based on literature evidence.
    """
    
    pathway_id = models.CharField(max_length=50, unique=True, db_index=True)
    name = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    
    category = models.CharField(
        max_length=100,
        choices=[
            ('neuroinflammation', 'Neuroinflammation'),
            ('mitochondrial', 'Mitochondrial Dysfunction'),
            ('protein_aggregation', 'Protein Aggregation'),
            ('synaptic', 'Synaptic Function'),
            ('autophagy', 'Autophagy/Proteostasis'),
            ('oxidative_stress', 'Oxidative Stress'),
            ('apoptosis', 'Apoptosis'),
            ('neurotransmission', 'Neurotransmission'),
            ('metabolism', 'Metabolism'),
            ('other', 'Other'),
        ],
        default='other'
    )
    
    disease_relevance = models.CharField(
        max_length=20,
        choices=[
            ('high', 'High - Core disease mechanism'),
            ('medium', 'Medium - Contributory'),
            ('low', 'Low - Peripheral'),
        ],
        default='medium'
    )
    
    # Pathway direction: what does "activation" mean for disease?
    activation_effect = models.CharField(
        max_length=20,
        choices=[
            ('beneficial', 'Beneficial - Activation helps'),
            ('detrimental', 'Detrimental - Activation harms'),
            ('complex', 'Complex - Context-dependent'),
            ('unknown', 'Unknown'),
        ],
        default='unknown',
        help_text="Effect of pathway activation on disease progression"
    )
    
    # Source
    source = models.CharField(
        max_length=50,
        choices=[
            ('kegg', 'KEGG'),
            ('reactome', 'Reactome'),
            ('go', 'Gene Ontology'),
            ('curated', 'Manually Curated'),
        ],
        default='curated'
    )
    source_id = models.CharField(max_length=50, null=True, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Pathways'
    
    def __str__(self):
        return f"{self.name} ({self.category})"


class PathwayTarget(models.Model):
    """
    Maps targets (genes/proteins) to pathways with their functional role.
    """
    
    pathway = models.ForeignKey(
        Pathway,
        on_delete=models.CASCADE,
        related_name='targets'
    )
    target = models.ForeignKey(
        'Target',
        on_delete=models.CASCADE,
        related_name='pathways'
    )
    
    role = models.CharField(
        max_length=50,
        choices=[
            ('activator', 'Activator'),
            ('inhibitor', 'Inhibitor'),
            ('modulator', 'Modulator'),
            ('substrate', 'Substrate'),
            ('receptor', 'Receptor'),
            ('enzyme', 'Enzyme'),
            ('transporter', 'Transporter'),
            ('unknown', 'Unknown'),
        ],
        default='unknown'
    )
    
    # Influence weight: how important is this target in the pathway?
    influence_weight = models.FloatField(
        default=1.0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Relative importance of target in pathway (0-5)"
    )
    
    evidence_level = models.CharField(
        max_length=20,
        choices=[
            ('high', 'High - Direct experimental'),
            ('medium', 'Medium - Literature'),
            ('low', 'Low - Inferred'),
        ],
        default='medium'
    )
    
    # Source reference
    pubmed_ids = models.JSONField(default=list, blank=True)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['pathway', 'target']
        ordering = ['-influence_weight']
    
    def __str__(self):
        return f"{self.target.gene_symbol} in {self.pathway.name} ({self.role})"
