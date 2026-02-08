import csv
from neuroai.models import Target

def ingest_disgenet(tsv_path):
    with open(tsv_path) as f:
        reader = csv.DictReader(f, delimiter="\t")
        for row in reader:
            if "Alzheimer" in row["diseaseName"]:
                target, _ = Target.objects.get_or_create(
                    gene_symbol=row["geneSymbol"]
                )
                target.neurodegeneration_score = max(
                    target.neurodegeneration_score,
                    float(row["score"])
                )
                target.save()