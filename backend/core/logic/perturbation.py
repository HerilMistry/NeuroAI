"""
Pathway perturbation modeling.

This module computes how drugs perturb disease-relevant pathways based on:
1. Drug-target interactions (affinity, activity type)
2. Target-pathway mappings (role, influence weight)
3. Pathway characteristics (activation effect on disease)

IMPORTANT: These are mechanistic hypotheses, NOT predictions.
Results should be interpreted with domain expertise.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
import math


@dataclass
class TargetContribution:
    """Contribution of a single target to pathway perturbation."""
    target_id: int
    gene_symbol: str
    affinity_nm: Optional[float]
    activity_type: str
    role_in_pathway: str
    influence_weight: float
    contribution_score: float
    has_toxicity_flag: bool


@dataclass
class PathwayPerturbationResult:
    """Result of pathway perturbation calculation."""
    pathway_id: str
    pathway_name: str
    perturbation_score: float  # -1 to +1
    direction: str  # 'activation', 'inhibition', 'mixed', 'neutral'
    disease_impact: str  # 'beneficial', 'detrimental', 'uncertain', 'neutral'
    confidence: float  # 0 to 1
    contributing_targets: List[TargetContribution]
    has_safety_concern: bool
    explanation: str


def _normalize_affinity(affinity_nm: Optional[float]) -> float:
    """
    Normalize affinity to 0-1 scale.
    Uses log transformation: tighter binding = higher score.
    
    - 1 nM = 1.0
    - 10 nM = 0.8
    - 100 nM = 0.6
    - 1000 nM = 0.4
    - 10000 nM = 0.2
    - >10000 nM = 0.1
    """
    if affinity_nm is None or affinity_nm <= 0:
        return 0.3  # Conservative default for unknown affinity
    
    if affinity_nm <= 1:
        return 1.0
    elif affinity_nm >= 10000:
        return 0.1
    
    # Log scale: log10(1) = 0, log10(10000) = 4
    log_affinity = math.log10(affinity_nm)
    # Map 0-4 to 1.0-0.1
    return max(0.1, 1.0 - (log_affinity / 4) * 0.9)


def _compute_target_effect(
    activity_type: str,
    role_in_pathway: str,
) -> float:
    """
    Compute the directional effect of a drug-target interaction on pathway.
    
    Returns:
        +1 for pathway activation
        -1 for pathway inhibition
        0 for neutral/unknown
    """
    # Activity type effect
    if activity_type in ('inhibitor', 'antagonist'):
        drug_effect = -1
    elif activity_type in ('agonist', 'activator'):
        drug_effect = +1
    else:
        drug_effect = 0
    
    # Role in pathway
    if role_in_pathway in ('inhibitor',):
        # Inhibiting an inhibitor = activation
        return -drug_effect
    elif role_in_pathway in ('activator', 'enzyme'):
        return drug_effect
    else:
        return drug_effect * 0.5  # Reduced effect for unknown roles


def _determine_direction(score: float) -> str:
    """Determine perturbation direction from score."""
    if score > 0.1:
        return 'activation'
    elif score < -0.1:
        return 'inhibition'
    elif abs(score) > 0.01:
        return 'mixed'
    else:
        return 'neutral'


def _determine_disease_impact(
    direction: str,
    pathway_activation_effect: str,
) -> str:
    """
    Determine hypothetical disease impact based on pathway biology.
    
    This is a simplistic mapping:
    - If pathway activation is beneficial and we're activating → beneficial
    - If pathway activation is detrimental and we're inhibiting → beneficial
    - Otherwise → uncertain
    """
    if pathway_activation_effect == 'unknown' or direction == 'neutral':
        return 'neutral'
    
    if direction == 'mixed':
        return 'uncertain'
    
    if pathway_activation_effect == 'beneficial':
        if direction == 'activation':
            return 'beneficial'
        else:
            return 'detrimental'
    elif pathway_activation_effect == 'detrimental':
        if direction == 'inhibition':
            return 'beneficial'
        else:
            return 'detrimental'
    else:
        return 'uncertain'


def calculate_drug_pathway_effect(
    drug_target_interactions: List[Dict],
    pathway_info: Dict,
    pathway_targets: List[Dict],
) -> PathwayPerturbationResult:
    """
    Calculate the perturbation effect of a drug on a pathway.
    
    Args:
        drug_target_interactions: List of {
            'target_id': int,
            'gene_symbol': str,
            'affinity_nm': float,
            'activity_type': str,
            'confidence_score': float,
            'is_toxicity_associated': bool,
        }
        pathway_info: {
            'pathway_id': str,
            'name': str,
            'activation_effect': str,  # 'beneficial', 'detrimental', 'complex', 'unknown'
        }
        pathway_targets: List of {
            'gene_symbol': str,
            'role': str,
            'influence_weight': float,
        }
    
    Returns:
        PathwayPerturbationResult with computed perturbation.
    """
    # Map pathway targets for quick lookup
    pathway_target_map = {
        pt['gene_symbol']: pt for pt in pathway_targets
    }
    
    contributions = []
    total_weighted_effect = 0.0
    total_weight = 0.0
    has_safety_concern = False
    confidence_sum = 0.0
    
    for interaction in drug_target_interactions:
        gene = interaction['gene_symbol']
        
        # Check if this target is in the pathway
        if gene not in pathway_target_map:
            continue
        
        pt = pathway_target_map[gene]
        
        # Compute effect
        affinity_strength = _normalize_affinity(interaction.get('affinity_nm'))
        directional_effect = _compute_target_effect(
            interaction.get('activity_type', 'unknown'),
            pt.get('role', 'unknown'),
        )
        influence = pt.get('influence_weight', 1.0)
        
        contribution = affinity_strength * directional_effect * influence
        weight = affinity_strength * influence
        
        total_weighted_effect += contribution
        total_weight += weight
        confidence_sum += interaction.get('confidence_score', 0.5)
        
        if interaction.get('is_toxicity_associated', False):
            has_safety_concern = True
        
        contributions.append(TargetContribution(
            target_id=interaction.get('target_id', 0),
            gene_symbol=gene,
            affinity_nm=interaction.get('affinity_nm'),
            activity_type=interaction.get('activity_type', 'unknown'),
            role_in_pathway=pt.get('role', 'unknown'),
            influence_weight=influence,
            contribution_score=round(contribution, 3),
            has_toxicity_flag=interaction.get('is_toxicity_associated', False),
        ))
    
    # Compute final score
    if total_weight > 0:
        perturbation_score = total_weighted_effect / total_weight
        # Clamp to -1 to +1
        perturbation_score = max(-1.0, min(1.0, perturbation_score))
    else:
        perturbation_score = 0.0
    
    # Compute confidence
    if contributions:
        avg_confidence = confidence_sum / len(contributions)
        # Penalize for few targets
        coverage_factor = min(1.0, len(contributions) / 3)
        confidence = avg_confidence * coverage_factor
    else:
        confidence = 0.0
    
    direction = _determine_direction(perturbation_score)
    disease_impact = _determine_disease_impact(
        direction,
        pathway_info.get('activation_effect', 'unknown'),
    )
    
    # Generate explanation
    if not contributions:
        explanation = f"No drug targets found in the {pathway_info['name']} pathway."
    else:
        target_list = ', '.join([c.gene_symbol for c in contributions[:3]])
        if len(contributions) > 3:
            target_list += f" (+{len(contributions)-3} more)"
        explanation = (
            f"Drug affects {len(contributions)} target(s) in pathway: {target_list}. "
            f"Net effect: {direction}. "
            f"Confidence: {confidence:.0%}."
        )
        if has_safety_concern:
            explanation += " ⚠️ Contains toxicity-associated target(s)."
    
    return PathwayPerturbationResult(
        pathway_id=pathway_info['pathway_id'],
        pathway_name=pathway_info['name'],
        perturbation_score=round(perturbation_score, 3),
        direction=direction,
        disease_impact=disease_impact,
        confidence=round(confidence, 2),
        contributing_targets=contributions,
        has_safety_concern=has_safety_concern,
        explanation=explanation,
    )


def aggregate_pathway_perturbation(
    effects: List[PathwayPerturbationResult],
) -> Dict:
    """
    Aggregate multiple pathway effects into a summary.
    
    Returns:
        Dict with summary statistics and categorization.
    """
    if not effects:
        return {
            'total_pathways': 0,
            'beneficial_count': 0,
            'detrimental_count': 0,
            'uncertain_count': 0,
            'neutral_count': 0,
            'avg_confidence': 0.0,
            'has_any_safety_concern': False,
            'summary': 'No pathway effects computed.',
        }
    
    beneficial = sum(1 for e in effects if e.disease_impact == 'beneficial')
    detrimental = sum(1 for e in effects if e.disease_impact == 'detrimental')
    uncertain = sum(1 for e in effects if e.disease_impact == 'uncertain')
    neutral = sum(1 for e in effects if e.disease_impact == 'neutral')
    
    avg_confidence = sum(e.confidence for e in effects) / len(effects)
    has_safety = any(e.has_safety_concern for e in effects)
    
    # Generate summary
    if detrimental > beneficial:
        summary = f"Net detrimental profile ({detrimental}/{len(effects)} pathways)."
    elif beneficial > detrimental:
        summary = f"Net beneficial profile ({beneficial}/{len(effects)} pathways)."
    else:
        summary = "Mixed or neutral pathway profile."
    
    if has_safety:
        summary += " Safety concerns flagged."
    
    return {
        'total_pathways': len(effects),
        'beneficial_count': beneficial,
        'detrimental_count': detrimental,
        'uncertain_count': uncertain,
        'neutral_count': neutral,
        'avg_confidence': round(avg_confidence, 2),
        'has_any_safety_concern': has_safety,
        'summary': summary,
    }
