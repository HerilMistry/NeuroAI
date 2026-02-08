
def toxicity_flags(drug):
    flags = []

    if drug.logp and drug.logp > 6:
        flags.append("high_lipophilicity")

    if drug.molecular_weight and drug.molecular_weight > 600:
        flags.append("poor_brain_penetration")

    return flags
