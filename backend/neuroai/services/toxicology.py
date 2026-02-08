from neuroai.models import DrugTarget


def off_target_burden(drug):
    
    targets = DrugTarget.objects.filter(drug=drug).values_list(
        "target_id", flat=True
    ).distinct()

    return len(targets)


TOXICITY_TARGETS = {
    "KCNH2",   # (cardiac arrhythmia)
    "SCN5A",   # (seizure/cardiac risk)
    "CACNA1C"  # Calcium channel
}

def toxicity_target_hit(drug):
    """
    Flags drugs hitting known toxicity-associated targets.
    """
    for dt in DrugTarget.objects.filter(drug=drug).select_related("target"):
        if dt.target.gene_symbol in TOXICITY_TARGETS:
            return True
    return False

def chemistry_risk_flags(drug):
    flags = []

    if drug.logp and drug.logp > 6:
        flags.append("high_lipophilicity")

    if drug.molecular_weight and drug.molecular_weight > 600:
        flags.append("high_molecular_weight")

    if drug.polar_surface_area and drug.polar_surface_area < 40:
        flags.append("nonspecific_brain_accumulation")

    return flags

TOX21_POSITIVE_DRUGS = set([
    # e.g. "chlorpromazine", "haloperidol"
])

def tox21_flags(drug):
    if drug.name.lower() in TOX21_POSITIVE_DRUGS:
        return ["in_vitro_toxicity_signal"]
    return []


def compute_toxicity_flags(drug):
    flags = []

    if off_target_burden(drug) > 15:
        flags.append("high_target_promiscuity")

    if toxicity_target_hit(drug):
        flags.append("toxicity_target_hit")

    flags.extend(chemistry_risk_flags(drug))
    flags.extend(tox21_flags(drug))

    return list(set(flags))
