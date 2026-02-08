from neuroai.models import DrugTarget

def compute_disease_relevance(drug):
    score = 0.0
    for dt in DrugTarget.objects.filter(drug=drug):
        score += dt.target.neurodegeneration_score * dt.confidence
    return round(score, 3)
