from django.db import models


class Drug(models.Model):
    name = models.CharField(max_length=255)
    drugbank_id = models.CharField(max_length=50, null=True, blank=True)
    approved = models.BooleanField(default=False)

    molecular_weight = models.FloatField(null=True)
    logp = models.FloatField(null=True)
    polar_surface_area = models.FloatField(null=True)

    bbb_score = models.FloatField(null=True)
    cns_viable = models.BooleanField(default=False)

    toxicity_flags = models.JSONField(default=list)

    disease_relevance_score = models.FloatField(default=0.0)

    def __str__(self):
        return self.name



class Target(models.Model):
    gene_symbol = models.CharField(max_length=50)
    uniprot_id = models.CharField(max_length=20, null=True, blank=True)

    neurodegeneration_score = models.FloatField(default=0.0)

    def __str__(self):
        return self.gene_symbol


class DrugTarget(models.Model):
    drug = models.ForeignKey(Drug, on_delete=models.CASCADE)
    target = models.ForeignKey(Target, on_delete=models.CASCADE)

    affinity = models.FloatField(null=True, blank=True)  
    confidence = models.FloatField(default=0.5)
    source = models.CharField(max_length=50)