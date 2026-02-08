import csv

from neuroai.models import Drug, Target, DrugTarget
def ingest_chembl(csv_path):
    with open(csv_path) as f:
        reader = csv.DictReader(f)
        for row in reader:
            drug, _ = Drug.objects.get_or_create(name=row["drug_name"])
            target, _ = Target.objects.get_or_create(
                gene_symbol=row["target_gene"]
            )

            DrugTarget.objects.create(
                drug=drug,
                target=target,
                affinity=float(row["standard_value"]) if row["standard_value"] else None,
                confidence=0.7,
                source="ChEMBL"
            )