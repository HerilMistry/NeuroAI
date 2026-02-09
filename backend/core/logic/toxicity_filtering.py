"""
Toxicity filtering and off-target risk assessment.

This module provides rule-based filtering based on:
- Known toxicity-associated targets (e.g., hERG, CYP450)
- Structural alerts (PAINS, etc.)
- Target promiscuity

IMPORTANT: This is NOT toxicity prediction.
It flags known liabilities for human review.
"""
from dataclasses import dataclass
from typing import List, Optional

# Known toxicity-associated targets (curated list)
# These are targets where modulation is associated with known safety issues
TOXICITY_TARGETS = {
    'KCNH2': {
        'name': 'hERG (Kv11.1)',
        'category': 'cardiac',
        'concern': 'QT prolongation, cardiac arrhythmia',
        'severity': 'high',
    },
    'SCN5A': {
        'name': 'Nav1.5',
        'category': 'cardiac',
        'concern': 'Cardiac sodium channel effects',
        'severity': 'high',
    },
    'CACNA1C': {
        'name': 'Cav1.2',
        'category': 'cardiac',
        'concern': 'Calcium channel effects on heart',
        'severity': 'medium',
    },
    'SLC6A4': {
        'name': 'SERT',
        'category': 'cns',
        'concern': 'Serotonin syndrome risk with polypharmacy',
        'severity': 'medium',
    },
    'HTR2B': {
        'name': '5-HT2B receptor',
        'category': 'cardiac',
        'concern': 'Valvulopathy risk',
        'severity': 'high',
    },
    'ADRA1A': {
        'name': 'Alpha-1A adrenergic receptor',
        'category': 'cardiovascular',
        'concern': 'Hypotension',
        'severity': 'medium',
    },
    'DRD2': {
        'name': 'Dopamine D2 receptor',
        'category': 'cns',
        'concern': 'Extrapyramidal symptoms',
        'severity': 'medium',
    },
    'CHRM1': {
        'name': 'Muscarinic M1 receptor',
        'category': 'cns',
        'concern': 'Cognitive impairment (anticholinergic)',
        'severity': 'medium',
    },
    'HRH1': {
        'name': 'Histamine H1 receptor',
        'category': 'cns',
        'concern': 'Sedation, weight gain',
        'severity': 'low',
    },
}

# Hepatotoxicity-associated targets
HEPATOTOX_TARGETS = ['CYP2D6', 'CYP3A4', 'CYP2C9', 'UGT1A1', 'ABCB1', 'SLCO1B1']


@dataclass
class ToxicityFlag:
    """Represents a toxicity concern for a target."""
    gene_symbol: str
    target_name: str
    category: str
    concern: str
    severity: str  # 'high', 'medium', 'low'


@dataclass 
class StructuralAlertResult:
    """Result of structural alert screening."""
    has_alerts: bool
    alert_count: int
    alerts: List[str]
    explanation: str


@dataclass
class OffTargetRiskResult:
    """Summary of off-target risk assessment."""
    total_off_targets: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    toxicity_flags: List[ToxicityFlag]
    has_critical_liability: bool
    explanation: str


def check_target_toxicity(gene_symbol: str) -> Optional[ToxicityFlag]:
    """
    Check if a target is associated with known toxicity.
    
    Args:
        gene_symbol: Gene symbol to check (e.g., 'KCNH2')
    
    Returns:
        ToxicityFlag if target has known liability, None otherwise.
    """
    gene_upper = gene_symbol.upper()
    
    if gene_upper in TOXICITY_TARGETS:
        info = TOXICITY_TARGETS[gene_upper]
        return ToxicityFlag(
            gene_symbol=gene_upper,
            target_name=info['name'],
            category=info['category'],
            concern=info['concern'],
            severity=info['severity'],
        )
    
    # Check hepatotox targets
    if gene_upper in HEPATOTOX_TARGETS:
        return ToxicityFlag(
            gene_symbol=gene_upper,
            target_name=gene_upper,
            category='hepatic',
            concern='Drug metabolism enzyme - potential drug-drug interactions',
            severity='medium',
        )
    
    return None


# Common structural alerts (simplified PAINS-like patterns)
STRUCTURAL_ALERTS = [
    ('michael_acceptor', 'Michael acceptor - reactive electrophile'),
    ('quinone', 'Quinone - redox cycling, oxidative stress'),
    ('nitro_aromatic', 'Aromatic nitro - genotoxicity concern'),
    ('aniline', 'Aniline - metabolic activation'),
    ('hydrazone', 'Hydrazone - instability, toxicity'),
    ('thiourea', 'Thiourea - thyroid toxicity'),
    ('rhodanine', 'Rhodanine - PAINS alert'),
    ('catechol', 'Catechol - COMT inhibition, reactivity'),
]


def check_drug_structural_alerts(
    structural_alerts: Optional[List[str]] = None,
    pains_count: int = 0,
) -> StructuralAlertResult:
    """
    Evaluate structural alerts for a drug.
    
    Args:
        structural_alerts: List of alert names detected in the drug
        pains_count: Number of PAINS alerts
    
    Returns:
        StructuralAlertResult with assessment.
    """
    alerts = structural_alerts or []
    total_alerts = len(alerts) + pains_count
    
    has_alerts = total_alerts > 0
    
    if total_alerts == 0:
        explanation = "No structural alerts detected."
    elif total_alerts <= 2:
        explanation = "Minor structural alerts present. Manual review recommended."
    else:
        explanation = "Multiple structural alerts. Significant medicinal chemistry concerns."
    
    return StructuralAlertResult(
        has_alerts=has_alerts,
        alert_count=total_alerts,
        alerts=alerts,
        explanation=explanation,
    )


def get_off_target_risks(
    target_gene_symbols: List[str],
    primary_target: Optional[str] = None,
) -> OffTargetRiskResult:
    """
    Assess off-target risks for a set of targets.
    
    Args:
        target_gene_symbols: List of all targets the drug binds
        primary_target: The intended therapeutic target (excluded from off-target count)
    
    Returns:
        OffTargetRiskResult with risk summary.
    """
    flags = []
    high_count = 0
    medium_count = 0
    low_count = 0
    
    off_targets = [t for t in target_gene_symbols if t != primary_target]
    
    for gene in off_targets:
        flag = check_target_toxicity(gene)
        if flag:
            flags.append(flag)
            if flag.severity == 'high':
                high_count += 1
            elif flag.severity == 'medium':
                medium_count += 1
            else:
                low_count += 1
    
    has_critical = high_count > 0
    
    # Generate explanation
    if not flags:
        explanation = f"{len(off_targets)} off-targets identified, none with known toxicity associations."
    elif has_critical:
        explanation = f"CAUTION: {high_count} high-severity off-target liability(s) detected."
    else:
        explanation = f"{len(flags)} off-target(s) with known liabilities (no critical concerns)."
    
    return OffTargetRiskResult(
        total_off_targets=len(off_targets),
        high_risk_count=high_count,
        medium_risk_count=medium_count,
        low_risk_count=low_count,
        toxicity_flags=flags,
        has_critical_liability=has_critical,
        explanation=explanation,
    )


def is_promiscuous_target(
    drug_count: int,
    threshold: int = 50,
) -> bool:
    """
    Check if a target is promiscuous (bound by many drugs).
    
    Promiscuous targets may indicate non-specific binding or
    that the target is a common off-target.
    
    Args:
        drug_count: Number of drugs known to bind this target
        threshold: Threshold for promiscuity (default 50)
    
    Returns:
        True if target is considered promiscuous.
    """
    return drug_count >= threshold
