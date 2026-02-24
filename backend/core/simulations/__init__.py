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


@dataclass
class Trajectory:
    """Simulation trajectory with multiple timepoints."""
    label: str
    time_steps: int
    trajectory: List[TimePoint] = field(default_factory=list)


@dataclass
class SimulationResult:
    """Results from a single disease progression simulation."""
    baseline: Trajectory
    treatment: Trajectory
    summary: Dict[str, Any]


def run_simulation(
    initial_state: Optional[Dict[str, float]] = None,
    pathway_effects: Optional[List[Dict[str, Any]]] = None,
    time_steps: int = 10,
    drug_name: str = "Unknown",
) -> SimulationResult:
    """
    Run a disease progression simulation with pathway effects.
    
    This function models how drug effects on pathways influence disease progression
    over time. Currently uses a simplified model - in production, this would use
    neural ODE models or other sophisticated differential equation solvers.
    
    Args:
        initial_state: Initial disease state parameters (optional)
        pathway_effects: List of pathway effect predictions from drug model
        time_steps: Number of time steps to simulate (default: 10)
        drug_name: Name of drug being simulated
        
    Returns:
        SimulationResult containing baseline and treatment trajectories
    """
    
    # Initialize baseline disease progression (no drug)
    baseline_trajectory = Trajectory(
        label="Baseline (No Treatment)",
        time_steps=time_steps,
        trajectory=[]
    )
    
    # Initialize treatment trajectory (with drug)
    treatment_trajectory = Trajectory(
        label=f"Treatment with {drug_name}",
        time_steps=time_steps,
        trajectory=[]
    )
    
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
    
    for t in range(time_steps):
        # Baseline: disease progression (exponential growth)
        baseline_params = {
            k: min(1.0, v * 1.05) for k, v in baseline_params.items()
        }
        baseline_trajectory.trajectory.append(
            TimePoint(time_step=t, parameters=baseline_params.copy())
        )
        
        # Treatment: slower progression with drug effects
        treatment_params = treatment_params.copy()
        
        # Apply pathway effects if provided
        if pathway_effects:
            for effect in pathway_effects:
                # Pathway effects reduce disease progression
                pathway_name = effect.get('pathway_name', 'unknown')
                effect_magnitude = effect.get('effect_magnitude', 0.1)
                
                # Reduce disease progression based on pathway effect
                for param in treatment_params:
                    if 'decline' in param.lower() or 'score' in param.lower():
                        treatment_params[param] = max(
                            0.0, 
                            treatment_params[param] - effect_magnitude * 0.01
                        )
                    else:
                        treatment_params[param] = min(
                            1.0,
                            treatment_params[param] * 1.03  # Slower growth
                        )
        else:
            # No specific pathway effects - use default drug effect
            treatment_params = {
                k: min(1.0, v * 1.03) for k, v in treatment_params.items()
            }
        
        treatment_trajectory.trajectory.append(
            TimePoint(time_step=t, parameters=treatment_params.copy())
        )
    
    # Calculate summary statistics
    baseline_final = baseline_trajectory.trajectory[-1].parameters if baseline_trajectory.trajectory else initial_state
    treatment_final = treatment_trajectory.trajectory[-1].parameters if treatment_trajectory.trajectory else initial_state
    
    baseline_avg = sum(baseline_final.values()) / len(baseline_final)
    treatment_avg = sum(treatment_final.values()) / len(treatment_final)
    improvement_pct = ((baseline_avg - treatment_avg) / baseline_avg * 100) if baseline_avg > 0 else 0
    
    summary = {
        'drug_name': drug_name,
        'time_steps_simulated': time_steps,
        'baseline_final_score': round(baseline_avg, 4),
        'treatment_final_score': round(treatment_avg, 4),
        'estimated_improvement_percent': round(improvement_pct, 2),
        'note': 'Simplified simulation for demonstration. Production uses neural ODE solvers.',
    }
    
    return SimulationResult(
        baseline=baseline_trajectory,
        treatment=treatment_trajectory,
        summary=summary,
    )
