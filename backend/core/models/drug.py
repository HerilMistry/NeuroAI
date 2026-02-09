"""
Drug model - represents pharmaceutical compounds with CNS penetration metrics.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Drug(models.Model):
    """
    Represents a drug/compound with physicochemical properties and CNS viability metrics.
    
    CNS MPO (Multiparameter Optimization) scoring is based on published rules:
    - Molecular Weight (MW): Lower is better for BBB penetration
    - LogP: Optimal range 1-3
    - HBD (Hydrogen Bond Donors): Lower is better
    - pKa: Moderate values preferred
    - TPSA (Topological Polar Surface Area): Lower is better for BBB
    
    All scores are computed via rule-based logic in core.logic.bbb_scoring.
    """
    
    # Identifiers
    drugbank_id = models.CharField(max_length=20, unique=True, db_index=True)
    chembl_id = models.CharField(max_length=30, null=True, blank=True, db_index=True)
    name = models.CharField(max_length=500)
    synonyms = models.JSONField(default=list, blank=True)
    
    # Regulatory status
    is_approved = models.BooleanField(default=False)
    approval_status = models.CharField(max_length=100, null=True, blank=True)
    
    # Chemical structure
    smiles = models.TextField(null=True, blank=True)
    inchi = models.TextField(null=True, blank=True)
    inchi_key = models.CharField(max_length=30, null=True, blank=True, db_index=True)
    
    # Physicochemical properties (for CNS MPO calculation)
    molecular_weight = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Molecular weight in Daltons"
    )
    logp = models.FloatField(
        null=True, blank=True,
        help_text="Calculated LogP (lipophilicity)"
    )
    hbd = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Number of hydrogen bond donors"
    )
    hba = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Number of hydrogen bond acceptors"
    )
    tpsa = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0)],
        help_text="Topological polar surface area (Å²)"
    )
    pka = models.FloatField(
        null=True, blank=True,
        help_text="Strongest basic pKa"
    )
    rotatable_bonds = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(0)]
    )
    
    # CNS scoring (computed)
    cns_mpo_score = models.FloatField(
        null=True, blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(6)],
        help_text="CNS MPO score (0-6 scale, higher is better)"
    )
    cns_viable = models.BooleanField(
        default=False,
        help_text="Flag: True if CNS MPO >= 4.0 (conservative threshold)"
    )
    cns_score_explanation = models.JSONField(
        default=dict, blank=True,
        help_text="Breakdown of individual CNS MPO component scores"
    )
    
    # Medicinal chemistry flags
    pains_alerts = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of PAINS (pan-assay interference) alerts"
    )
    structural_alerts = models.JSONField(
        default=list, blank=True,
        help_text="List of structural alert names detected"
    )
    
    # Metadata
    description = models.TextField(null=True, blank=True)
    categories = models.JSONField(default=list, blank=True)
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data_source = models.CharField(max_length=50, default='drugbank')
    
    class Meta:
        ordering = ['name']
        indexes = [
            models.Index(fields=['cns_mpo_score']),
            models.Index(fields=['cns_viable']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.drugbank_id})"
    
    @property
    def has_complete_physicochemical_data(self) -> bool:
        """Check if all required properties for CNS MPO are present."""
        return all([
            self.molecular_weight is not None,
            self.logp is not None,
            self.hbd is not None,
            self.tpsa is not None,
        ])
