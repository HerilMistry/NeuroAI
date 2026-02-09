"""
DiseaseState model - represents disease progression parameters for simulation.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class DiseaseState(models.Model):
    """
    Represents a disease state configuration for progression simulation.
    
    This is NOT a patient-level model. It represents abstract disease states
    for mechanism-based simulation and exploration.
    
    WARNING: Simulations are for mechanistic reasoning only.
    They do NOT predict clinical outcomes or efficacy.
    """
    
    name = models.CharField(max_length=200, unique=True)
    description = models.TextField(null=True, blank=True)
    
    disease_type = models.CharField(
        max_length=50,
        choices=[
            ('alzheimers', "Alzheimer's Disease"),
            ('parkinsons', "Parkinson's Disease"),
            ('als', 'ALS'),
            ('huntingtons', "Huntington's Disease"),
            ('ms', 'Multiple Sclerosis'),
            ('generic', 'Generic Neurodegeneration'),
        ],
        default='generic'
    )
    
    # Baseline state parameters (normalized 0-1 scale)
    # These are abstract representations, NOT clinical biomarkers
    parameters = models.JSONField(
        default=dict,
        help_text="State parameters (e.g., amyloid_load, synaptic_health, inflammation)"
    )
    
    # Example default parameters:
    # {
    #   "amyloid_load": 0.7,          # Higher = worse
    #   "tau_pathology": 0.5,         # Higher = worse  
    #   "synaptic_health": 0.4,       # Higher = better
    #   "neuroinflammation": 0.6,     # Higher = worse
    #   "mitochondrial_function": 0.5, # Higher = better
    #   "oxidative_stress": 0.5,      # Higher = worse
    # }
    
    # Baseline trajectory (without intervention)
    baseline_trajectory = models.JSONField(
        default=dict,
        help_text="Expected parameter changes over time without intervention"
    )
    
    # Example trajectory:
    # {
    #   "time_steps": 10,
    #   "parameter_deltas": {
    #     "amyloid_load": 0.03,        # Increases over time
    #     "synaptic_health": -0.02,    # Decreases over time
    #   }
    # }
    
    # Uncertainty bounds
    uncertainty_bounds = models.JSONField(
        default=dict,
        help_text="Min/max uncertainty ranges for each parameter"
    )
    
    # Configuration for simulation
    simulation_config = models.JSONField(
        default=dict,
        help_text="Simulation parameters (time horizon, step size, etc.)"
    )
    
    # Metadata
    is_default = models.BooleanField(default=False)
    
    # Audit
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.CharField(max_length=100, null=True, blank=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Disease States'
    
    def __str__(self):
        return f"{self.name} ({self.disease_type})"
    
    @classmethod
    def get_default_parameters(cls) -> dict:
        """Return default disease state parameters."""
        return {
            "amyloid_load": 0.5,
            "tau_pathology": 0.3,
            "synaptic_health": 0.6,
            "neuroinflammation": 0.4,
            "mitochondrial_function": 0.6,
            "oxidative_stress": 0.4,
            "autophagy_efficiency": 0.5,
        }
