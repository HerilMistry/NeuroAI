"""
Disease progression simulation module.

Simulates baseline vs. drug-modified disease trajectories.

IMPORTANT: This is a mechanistic reasoning tool, NOT a clinical prediction.
- No outcome prediction or efficacy claims.
- All results are hypothetical and for research exploration only.
- Uncertainty is explicitly modeled and displayed.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import random


@dataclass
class SimulationPoint:
    """A single timepoint in the simulation."""
    time_step: int
    parameters: Dict[str, float]
    uncertainty: Dict[str, float]


@dataclass
class TrajectoryResult:
    """Result of a disease trajectory simulation."""
    label: str  # 'baseline' or drug name
    time_steps: int
    trajectory: List[SimulationPoint]
    final_state: Dict[str, float]
    key_changes: Dict[str, float]  # Change from initial to final
    explanation: str


@dataclass
class SimulationResult:
    """Full simulation result comparing baseline to intervention."""
    baseline: TrajectoryResult
    intervention: Optional[TrajectoryResult]
    comparison: Dict[str, float]  # Difference between final states
    overall_assessment: str
    caveats: List[str]


# Default disease parameters and their meanings
DEFAULT_PARAMETERS = {
    'amyloid_load': {'initial': 0.5, 'direction': 'worse_is_higher', 'delta': 0.03},
    'tau_pathology': {'initial': 0.3, 'direction': 'worse_is_higher', 'delta': 0.02},
    'synaptic_health': {'initial': 0.6, 'direction': 'worse_is_lower', 'delta': -0.02},
    'neuroinflammation': {'initial': 0.4, 'direction': 'worse_is_higher', 'delta': 0.02},
    'mitochondrial_function': {'initial': 0.6, 'direction': 'worse_is_lower', 'delta': -0.015},
    'oxidative_stress': {'initial': 0.4, 'direction': 'worse_is_higher', 'delta': 0.015},
    'autophagy_efficiency': {'initial': 0.5, 'direction': 'worse_is_lower', 'delta': -0.01},
}


def _clamp(value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
    """Clamp value to range."""
    return max(min_val, min(max_val, value))


def _add_noise(value: float, noise_level: float = 0.02) -> float:
    """Add small Gaussian noise to simulate uncertainty."""
    noise = random.gauss(0, noise_level)
    return _clamp(value + noise)


def simulate_baseline_trajectory(
    initial_state: Optional[Dict[str, float]] = None,
    time_steps: int = 10,
    noise_level: float = 0.02,
) -> TrajectoryResult:
    """
    Simulate baseline disease progression without intervention.
    
    Args:
        initial_state: Starting parameter values (uses defaults if None)
        time_steps: Number of simulation steps
        noise_level: Stochastic noise level
    
    Returns:
        TrajectoryResult for baseline progression.
    """
    # Use defaults for missing parameters
    state = {}
    for param, config in DEFAULT_PARAMETERS.items():
        if initial_state and param in initial_state:
            state[param] = initial_state[param]
        else:
            state[param] = config['initial']
    
    trajectory = [SimulationPoint(
        time_step=0,
        parameters=dict(state),
        uncertainty={p: 0.0 for p in state},
    )]
    
    for t in range(1, time_steps + 1):
        new_state = {}
        uncertainties = {}
        
        for param, config in DEFAULT_PARAMETERS.items():
            delta = config['delta']
            new_val = _add_noise(state[param] + delta, noise_level)
            new_val = _clamp(new_val)
            new_state[param] = new_val
            # Uncertainty grows with time
            uncertainties[param] = min(0.2, t * noise_level)
        
        state = new_state
        trajectory.append(SimulationPoint(
            time_step=t,
            parameters=dict(state),
            uncertainty=uncertainties,
        ))
    
    # Calculate changes
    initial = trajectory[0].parameters
    final = trajectory[-1].parameters
    changes = {p: round(final[p] - initial[p], 3) for p in initial}
    
    explanation = (
        f"Baseline progression over {time_steps} time units shows typical "
        f"disease trajectory with increasing pathology markers and declining "
        f"protective factors."
    )
    
    return TrajectoryResult(
        label='baseline',
        time_steps=time_steps,
        trajectory=trajectory,
        final_state=final,
        key_changes=changes,
        explanation=explanation,
    )


def simulate_intervention_trajectory(
    initial_state: Dict[str, float],
    pathway_effects: List[Dict],
    time_steps: int = 10,
    noise_level: float = 0.02,
) -> TrajectoryResult:
    """
    Simulate disease progression with drug intervention.
    
    The drug modifies disease parameters based on pathway effects.
    
    Args:
        initial_state: Starting parameter values
        pathway_effects: List of {
            'pathway_category': str,
            'perturbation_score': float (-1 to +1),
            'direction': str,
        }
        time_steps: Number of simulation steps
        noise_level: Stochastic noise level
    
    Returns:
        TrajectoryResult for intervention.
    """
    # Map pathway categories to disease parameters
    pathway_to_params = {
        'neuroinflammation': 'neuroinflammation',
        'mitochondrial': 'mitochondrial_function',
        'protein_aggregation': 'amyloid_load',
        'synaptic': 'synaptic_health',
        'autophagy': 'autophagy_efficiency',
        'oxidative_stress': 'oxidative_stress',
    }
    
    # Calculate drug modifications to deltas
    drug_mods = {p: 0.0 for p in DEFAULT_PARAMETERS}
    
    for effect in pathway_effects:
        category = effect.get('pathway_category', '')
        score = effect.get('perturbation_score', 0)
        
        if category in pathway_to_params:
            param = pathway_to_params[category]
            config = DEFAULT_PARAMETERS[param]
            
            # Drug effect modifies the disease trajectory
            # Positive perturbation on beneficial pathways = good
            if config['direction'] == 'worse_is_higher':
                # Reducing this is good; inhibition (negative score) helps
                drug_mods[param] -= score * 0.02
            else:
                # Increasing this is good; activation (positive score) helps
                drug_mods[param] += score * 0.02
    
    state = dict(initial_state)
    trajectory = [SimulationPoint(
        time_step=0,
        parameters=dict(state),
        uncertainty={p: 0.0 for p in state},
    )]
    
    for t in range(1, time_steps + 1):
        new_state = {}
        uncertainties = {}
        
        for param, config in DEFAULT_PARAMETERS.items():
            # Base delta modified by drug effect
            delta = config['delta'] + drug_mods.get(param, 0)
            new_val = _add_noise(state[param] + delta, noise_level)
            new_val = _clamp(new_val)
            new_state[param] = new_val
            uncertainties[param] = min(0.2, t * noise_level)
        
        state = new_state
        trajectory.append(SimulationPoint(
            time_step=t,
            parameters=dict(state),
            uncertainty=uncertainties,
        ))
    
    # Calculate changes
    initial = trajectory[0].parameters
    final = trajectory[-1].parameters
    changes = {p: round(final[p] - initial[p], 3) for p in initial}
    
    explanation = (
        f"Intervention trajectory shows modified progression based on "
        f"{len(pathway_effects)} pathway effects."
    )
    
    return TrajectoryResult(
        label='intervention',
        time_steps=time_steps,
        trajectory=trajectory,
        final_state=final,
        key_changes=changes,
        explanation=explanation,
    )


def run_simulation(
    initial_state: Optional[Dict[str, float]] = None,
    pathway_effects: Optional[List[Dict]] = None,
    time_steps: int = 10,
    drug_name: str = 'Intervention',
) -> SimulationResult:
    """
    Run complete simulation comparing baseline to intervention.
    
    Args:
        initial_state: Starting state (uses defaults if None)
        pathway_effects: Drug's pathway effects (no intervention if None)
        time_steps: Simulation duration
        drug_name: Name of drug for labeling
    
    Returns:
        SimulationResult with both trajectories and comparison.
    """
    # Get initial state
    state = {}
    for param, config in DEFAULT_PARAMETERS.items():
        if initial_state and param in initial_state:
            state[param] = initial_state[param]
        else:
            state[param] = config['initial']
    
    # Simulate baseline
    baseline = simulate_baseline_trajectory(state, time_steps)
    
    # Simulate intervention if effects provided
    intervention = None
    comparison = {}
    
    if pathway_effects:
        intervention = simulate_intervention_trajectory(state, pathway_effects, time_steps)
        intervention.label = drug_name
        
        # Compare final states
        for param in state:
            baseline_final = baseline.final_state.get(param, 0)
            interv_final = intervention.final_state.get(param, 0)
            comparison[param] = round(interv_final - baseline_final, 3)
    
    # Generate assessment
    if not intervention:
        assessment = "Baseline-only simulation. No intervention compared."
    else:
        # Count improved parameters
        improved = 0
        worsened = 0
        for param, diff in comparison.items():
            config = DEFAULT_PARAMETERS[param]
            if config['direction'] == 'worse_is_higher':
                if diff < -0.01:
                    improved += 1
                elif diff > 0.01:
                    worsened += 1
            else:
                if diff > 0.01:
                    improved += 1
                elif diff < -0.01:
                    worsened += 1
        
        if improved > worsened:
            assessment = f"Intervention shows improvement in {improved}/{len(comparison)} parameters."
        elif worsened > improved:
            assessment = f"Intervention shows worsening in {worsened}/{len(comparison)} parameters."
        else:
            assessment = "Intervention shows mixed or neutral effects."
    
    caveats = [
        "This simulation is for mechanistic exploration only.",
        "Results do NOT predict clinical efficacy or patient outcomes.",
        "Uncertainty increases over simulation time.",
        "Real disease progression is far more complex than this model.",
    ]
    
    return SimulationResult(
        baseline=baseline,
        intervention=intervention,
        comparison=comparison,
        overall_assessment=assessment,
        caveats=caveats,
    )
