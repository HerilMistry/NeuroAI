"""
Simulation module for disease progression modeling.

Provides functions for running pathway-based simulations of drug effects
on disease states using pre-trained ML models for predictions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


@dataclass
class TimePoint:
    """Single timepoint in a simulation trajectory."""
    time_step: int
    parameters: Dict[str, float]
    uncertainty: float = 0.05


@dataclass
class Trajectory:
    """Simulation trajectory with multiple timepoints."""
    label: str
    time_steps: int
    trajectory: List[TimePoint] = field(default_factory=list)
    final_state: Dict[str, float] = field(default_factory=dict)
    key_changes: List[str] = field(default_factory=list)
    explanation: str = ""


@dataclass
class SimulationResult:
    """Results from a single disease progression simulation."""
    baseline: Trajectory
    intervention: Optional[Trajectory]
    comparison: Dict[str, Any]
    overall_assessment: str
    caveats: List[str]


def run_simulation(
    initial_state: Optional[Dict[str, float]] = None,
    pathway_effects: Optional[List[Dict[str, Any]]] = None,
    time_steps: int = 10,
    drug_name: str = "Unknown",
) -> SimulationResult:
    """
    Run a disease progression simulation with pathway effects.
    
    This function models how drug effects on pathways influence disease progression
    over time. Currently uses a simplified model — in production, this would use
    neural ODE models or other sophisticated differential equation solvers.
    
    Args:
        initial_state: Initial disease state parameters (optional)
        pathway_effects: List of pathway effect predictions from drug model
        time_steps: Number of time steps to simulate (default: 10)
        drug_name: Name of drug being simulated
        
    Returns:
        SimulationResult containing baseline and intervention trajectories
    """
    
    # Default disease parameters if not provided
    if initial_state is None:
        initial_state = {
            'neurodegeneration_score': 0.5,
            'amyloid_beta': 0.6,
            'tau_pathology': 0.55,
            'neuroinflammation': 0.5,
            'cognitive_decline': 0.3,
        }
    
    # Simulate trajectory progression
    baseline_params = initial_state.copy()
    treatment_params = initial_state.copy()
    
    baseline_points: List[TimePoint] = []
    intervention_points: List[TimePoint] = []
    
    for t in range(time_steps):
        # Baseline: disease progression (exponential growth)
        baseline_params = {
            k: min(1.0, v * 1.05) for k, v in baseline_params.items()
        }
        uncertainty = 0.02 + 0.005 * t  # grows with time
        baseline_points.append(
            TimePoint(time_step=t, parameters=baseline_params.copy(), uncertainty=round(uncertainty, 4))
        )
        
        # Treatment: slower progression with drug effects
        treatment_params = treatment_params.copy()
        
        # Apply pathway effects if provided
        if pathway_effects:
            for effect in pathway_effects:
                effect_magnitude = effect.get('perturbation_score', effect.get('effect_magnitude', 0.1))
                direction = effect.get('direction', 'inhibition')
                
                for param in treatment_params:
                    if direction == 'inhibition':
                        treatment_params[param] = max(
                            0.0,
                            treatment_params[param] * 1.02 - abs(effect_magnitude) * 0.005
                        )
                    else:
                        treatment_params[param] = min(
                            1.0,
                            treatment_params[param] * 1.03
                        )
        else:
            # No specific pathway effects — use default drug effect
            treatment_params = {
                k: min(1.0, v * 1.03) for k, v in treatment_params.items()
            }
        
        intervention_points.append(
            TimePoint(time_step=t, parameters=treatment_params.copy(), uncertainty=round(uncertainty * 1.1, 4))
        )
    
    # Compute final states and key changes
    baseline_final = baseline_points[-1].parameters if baseline_points else initial_state
    treatment_final = intervention_points[-1].parameters if intervention_points else initial_state
    
    baseline_avg = sum(baseline_final.values()) / len(baseline_final)
    treatment_avg = sum(treatment_final.values()) / len(treatment_final)
    improvement_pct = ((baseline_avg - treatment_avg) / baseline_avg * 100) if baseline_avg > 0 else 0
    
    baseline_key_changes = []
    intervention_key_changes = []
    pathway_impact_list = []
    
    for key in initial_state:
        bchange = baseline_final[key] - initial_state[key]
        tchange = treatment_final[key] - initial_state[key]
        direction_b = "increased" if bchange > 0 else "decreased"
        direction_t = "increased" if tchange > 0 else "decreased"
        baseline_key_changes.append(f"{key.replace('_', ' ').title()} {direction_b} by {abs(bchange):.3f}")
        intervention_key_changes.append(f"{key.replace('_', ' ').title()} {direction_t} by {abs(tchange):.3f}")
        if abs(bchange - tchange) > 0.01:
            pathway_impact_list.append(f"{key.replace('_', ' ').title()}: {abs(bchange - tchange):.3f} improvement")
    
    # Build trajectories
    baseline_trajectory = Trajectory(
        label="Baseline (No Treatment)",
        time_steps=time_steps,
        trajectory=baseline_points,
        final_state=baseline_final,
        key_changes=baseline_key_changes,
        explanation="Natural disease progression without any drug intervention. Parameters trend toward worse states over time.",
    )
    
    intervention_trajectory = Trajectory(
        label=f"Treatment with {drug_name}",
        time_steps=time_steps,
        trajectory=intervention_points,
        final_state=treatment_final,
        key_changes=intervention_key_changes,
        explanation=f"Disease progression modulated by {drug_name}. Drug pathway effects slow deterioration across key parameters.",
    ) if drug_name != "Intervention" or pathway_effects else None
    
    # Always provide intervention for the frontend
    if intervention_trajectory is None:
        intervention_trajectory = Trajectory(
            label=f"Treatment with {drug_name}",
            time_steps=time_steps,
            trajectory=intervention_points,
            final_state=treatment_final,
            key_changes=intervention_key_changes,
            explanation=f"Disease progression modulated by {drug_name}.",
        )
    
    comparison = {
        'improvement': f"{improvement_pct:.1f}% overall improvement",
        'time_benefit': f"~{max(1, int(improvement_pct / 5))} additional time steps before critical threshold",
        'pathway_impact': pathway_impact_list[:5],
    }
    
    overall_assessment = (
        f"Simulation of {drug_name} over {time_steps} steps shows "
        f"{improvement_pct:.1f}% improvement vs. baseline. "
        f"This is a mechanistic exploration, NOT a clinical prediction."
    )
    
    caveats = [
        "This is a simplified mechanistic simulation for exploratory purposes only.",
        "Results do NOT predict clinical efficacy or patient outcomes.",
        "Disease progression models use abstract parameters, not validated biomarkers.",
        "All predictions should be reviewed by domain experts before any decision-making.",
        "Production systems would use neural ODE solvers with uncertainty quantification.",
    ]
    
    return SimulationResult(
        baseline=baseline_trajectory,
        intervention=intervention_trajectory,
        comparison=comparison,
        overall_assessment=overall_assessment,
        caveats=caveats,
    )
