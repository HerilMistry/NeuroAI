"""
Blood-Brain Barrier (BBB) scoring using CNS MPO (Multiparameter Optimization).

This module implements rule-based scoring inspired by Pfizer's CNS MPO algorithm.
Reference: Wager et al., ACS Chem Neurosci. 2010;1(6):435-449.

IMPORTANT: This is a heuristic tool, NOT a prediction of BBB penetration.
It provides a mechanistic triage signal, not a clinical assessment.
"""
from dataclasses import dataclass
from typing import Optional


# Conservative threshold: drugs below this are flagged as CNS-questionable
CNS_MPO_THRESHOLD = 4.0


@dataclass
class CNSMPOResult:
    """Result of CNS MPO calculation with component breakdown."""
    total_score: float
    is_viable: bool
    component_scores: dict
    missing_properties: list
    explanation: str


def _score_molecular_weight(mw: Optional[float]) -> Optional[float]:
    """
    Score molecular weight (MW).
    Optimal: <360 Da (score 1.0)
    Penalty: 360-500 Da (linear decrease)
    Poor: >500 Da (score 0)
    """
    if mw is None:
        return None
    if mw <= 360:
        return 1.0
    elif mw <= 500:
        return 1.0 - (mw - 360) / 140
    else:
        return 0.0


def _score_logp(logp: Optional[float]) -> Optional[float]:
    """
    Score calculated LogP.
    Optimal: 1-3 (score 1.0)
    Moderate: 0-1 or 3-5 (partial score)
    Poor: <0 or >5 (score 0)
    """
    if logp is None:
        return None
    if 1 <= logp <= 3:
        return 1.0
    elif 0 <= logp < 1:
        return logp
    elif 3 < logp <= 5:
        return 1.0 - (logp - 3) / 2
    else:
        return 0.0


def _score_hbd(hbd: Optional[int]) -> Optional[float]:
    """
    Score hydrogen bond donors (HBD).
    Optimal: 0-1 (score 1.0)
    Moderate: 2-3 (partial)
    Poor: >3 (score 0)
    """
    if hbd is None:
        return None
    if hbd <= 1:
        return 1.0
    elif hbd == 2:
        return 0.75
    elif hbd == 3:
        return 0.25
    else:
        return 0.0


def _score_tpsa(tpsa: Optional[float]) -> Optional[float]:
    """
    Score topological polar surface area (TPSA).
    Optimal: <60 Å² (score 1.0)
    Moderate: 60-90 Å² (linear decrease)
    Poor: >90 Å² (score 0)
    """
    if tpsa is None:
        return None
    if tpsa <= 60:
        return 1.0
    elif tpsa <= 90:
        return 1.0 - (tpsa - 60) / 30
    else:
        return 0.0


def _score_pka(pka: Optional[float]) -> Optional[float]:
    """
    Score strongest basic pKa.
    Optimal: 7.5-10.5 (score 1.0)
    Moderate: 6-7.5 or 10.5-12 (partial)
    Poor: <6 or >12 (score 0)
    
    Note: pKa is often missing; we use a default of 0.5 if absent.
    """
    if pka is None:
        return 0.5  # Neutral default for missing data
    if 7.5 <= pka <= 10.5:
        return 1.0
    elif 6 <= pka < 7.5:
        return (pka - 6) / 1.5
    elif 10.5 < pka <= 12:
        return 1.0 - (pka - 10.5) / 1.5
    else:
        return 0.0


def _score_rotatable_bonds(rot: Optional[int]) -> Optional[float]:
    """
    Score number of rotatable bonds.
    Optimal: 0-5 (score 1.0)
    Moderate: 6-10 (linear decrease)
    Poor: >10 (score 0)
    """
    if rot is None:
        return 0.5  # Neutral default
    if rot <= 5:
        return 1.0
    elif rot <= 10:
        return 1.0 - (rot - 5) / 5
    else:
        return 0.0


def calculate_cns_mpo_score(
    molecular_weight: Optional[float] = None,
    logp: Optional[float] = None,
    hbd: Optional[int] = None,
    tpsa: Optional[float] = None,
    pka: Optional[float] = None,
    rotatable_bonds: Optional[int] = None,
) -> CNSMPOResult:
    """
    Calculate CNS MPO score from physicochemical properties.
    
    Returns a score from 0-6, where:
    - 6 = Optimal CNS drug-like profile
    - ≥4 = Generally favorable (our threshold)
    - <4 = Potentially problematic for CNS penetration
    
    Args:
        molecular_weight: MW in Daltons
        logp: Calculated LogP
        hbd: Number of hydrogen bond donors
        tpsa: Topological polar surface area (Å²)
        pka: Strongest basic pKa
        rotatable_bonds: Number of rotatable bonds
    
    Returns:
        CNSMPOResult with score, viability flag, and component breakdown.
    """
    scores = {}
    missing = []
    
    # Calculate component scores
    mw_score = _score_molecular_weight(molecular_weight)
    if mw_score is None:
        missing.append('molecular_weight')
        mw_score = 0.5  # Penalize missing data conservatively
    scores['molecular_weight'] = {'value': molecular_weight, 'score': mw_score}
    
    logp_score = _score_logp(logp)
    if logp_score is None:
        missing.append('logp')
        logp_score = 0.5
    scores['logp'] = {'value': logp, 'score': logp_score}
    
    hbd_score = _score_hbd(hbd)
    if hbd_score is None:
        missing.append('hbd')
        hbd_score = 0.5
    scores['hbd'] = {'value': hbd, 'score': hbd_score}
    
    tpsa_score = _score_tpsa(tpsa)
    if tpsa_score is None:
        missing.append('tpsa')
        tpsa_score = 0.5
    scores['tpsa'] = {'value': tpsa, 'score': tpsa_score}
    
    pka_score = _score_pka(pka)
    scores['pka'] = {'value': pka, 'score': pka_score}
    
    rot_score = _score_rotatable_bonds(rotatable_bonds)
    scores['rotatable_bonds'] = {'value': rotatable_bonds, 'score': rot_score}
    
    # Sum component scores (max = 6)
    total = mw_score + logp_score + hbd_score + tpsa_score + pka_score + rot_score
    is_viable = total >= CNS_MPO_THRESHOLD and len(missing) <= 1
    
    # Generate explanation
    explanation_parts = []
    if total >= 5:
        explanation_parts.append("Strong CNS drug-like profile.")
    elif total >= 4:
        explanation_parts.append("Acceptable CNS drug-like profile.")
    else:
        explanation_parts.append("Suboptimal CNS drug-like profile.")
    
    if missing:
        explanation_parts.append(f"Missing data for: {', '.join(missing)}.")
    
    # Note specific concerns
    if mw_score < 0.5:
        explanation_parts.append("High molecular weight may limit BBB penetration.")
    if tpsa_score < 0.5:
        explanation_parts.append("High TPSA may reduce membrane permeability.")
    if hbd_score < 0.5:
        explanation_parts.append("High HBD count may reduce passive diffusion.")
    
    return CNSMPOResult(
        total_score=round(total, 2),
        is_viable=is_viable,
        component_scores=scores,
        missing_properties=missing,
        explanation=" ".join(explanation_parts)
    )
