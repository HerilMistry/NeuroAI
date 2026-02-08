def compute_bbb_score(drug):
    score = 0.0

    if drug.molecular_weight and drug.molecular_weight < 450:
        score += 0.3
    if drug.logp and 2.0 <= drug.logp <= 5.0:
        score += 0.3
    if drug.polar_surface_area and drug.polar_surface_area < 90:
        score += 0.4

    return round(score, 2)
