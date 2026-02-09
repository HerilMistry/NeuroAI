"""
Management command to seed sample data for development.

Usage:
    python manage.py seed_sample_data
"""
from django.core.management.base import BaseCommand
from core.models import (
    Drug, Target, DrugTarget, Pathway, PathwayTarget,
    DrugPathwayEffect, DiseaseState
)
from core.logic import calculate_cns_mpo_score


class Command(BaseCommand):
    help = 'Seed database with sample data for development'
    
    def handle(self, *args, **options):
        self.stdout.write("Seeding sample data...")
        
        # Create sample drugs
        drugs_data = [
            {
                'drugbank_id': 'DB00001',
                'name': 'Donepezil',
                'smiles': 'COC1=CC=C(CC(=O)N2CCC3=CC(OC)=C(OC)C=C3C2)C=C1',
                'molecular_weight': 379.5,
                'logp': 4.28,
                'hbd': 0,
                'hba': 5,
                'tpsa': 38.8,
                'pka': 8.9,
                'is_approved': True,
            },
            {
                'drugbank_id': 'DB00002',
                'name': 'Memantine',
                'smiles': 'CC12CC3CC(C)(C1)CC(N)(C3)C2',
                'molecular_weight': 179.3,
                'logp': 2.07,
                'hbd': 2,
                'hba': 1,
                'tpsa': 26.0,
                'pka': 10.7,
                'is_approved': True,
            },
            {
                'drugbank_id': 'DB00003',
                'name': 'Rivastigmine',
                'smiles': 'CCN(C)C(=O)OC1=CC=CC(C(C)N(C)C)=C1',
                'molecular_weight': 250.3,
                'logp': 2.3,
                'hbd': 0,
                'hba': 3,
                'tpsa': 32.7,
                'pka': 8.9,
                'is_approved': True,
            },
        ]
        
        for drug_data in drugs_data:
            mpo = calculate_cns_mpo_score(
                molecular_weight=drug_data['molecular_weight'],
                logp=drug_data['logp'],
                hbd=drug_data['hbd'],
                tpsa=drug_data['tpsa'],
                pka=drug_data['pka'],
            )
            
            drug, created = Drug.objects.update_or_create(
                drugbank_id=drug_data['drugbank_id'],
                defaults={
                    **drug_data,
                    'cns_mpo_score': mpo.total_score,
                    'cns_viable': mpo.is_viable,
                    'cns_score_explanation': mpo.component_scores,
                }
            )
            self.stdout.write(f"  Drug: {drug.name} (MPO: {mpo.total_score})")
        
        # Create sample targets
        targets_data = [
            {'gene_symbol': 'ACHE', 'gene_name': 'Acetylcholinesterase', 'protein_name': 'Acetylcholinesterase', 'disease_relevance_score': 0.8},
            {'gene_symbol': 'GRIN2B', 'gene_name': 'Glutamate receptor NMDA 2B', 'protein_name': 'NMDA receptor subunit 2B', 'disease_relevance_score': 0.7},
            {'gene_symbol': 'BCHE', 'gene_name': 'Butyrylcholinesterase', 'protein_name': 'Butyrylcholinesterase', 'disease_relevance_score': 0.5},
            {'gene_symbol': 'KCNH2', 'gene_name': 'hERG', 'protein_name': 'hERG potassium channel', 'is_toxicity_associated': True, 'toxicity_categories': ['cardiac']},
        ]
        
        for target_data in targets_data:
            target, created = Target.objects.update_or_create(
                gene_symbol=target_data['gene_symbol'],
                defaults=target_data
            )
            self.stdout.write(f"  Target: {target.gene_symbol}")
        
        # Create sample pathways
        pathways_data = [
            {'pathway_id': 'PW001', 'name': 'Cholinergic Signaling', 'category': 'neurotransmission', 'disease_relevance': 'high', 'activation_effect': 'beneficial'},
            {'pathway_id': 'PW002', 'name': 'Glutamatergic Signaling', 'category': 'neurotransmission', 'disease_relevance': 'high', 'activation_effect': 'complex'},
            {'pathway_id': 'PW003', 'name': 'Neuroinflammation', 'category': 'neuroinflammation', 'disease_relevance': 'high', 'activation_effect': 'detrimental'},
        ]
        
        for pathway_data in pathways_data:
            pathway, created = Pathway.objects.update_or_create(
                pathway_id=pathway_data['pathway_id'],
                defaults=pathway_data
            )
            self.stdout.write(f"  Pathway: {pathway.name}")
        
        # Create sample disease state
        DiseaseState.objects.update_or_create(
            name='Early Alzheimer\'s',
            defaults={
                'disease_type': 'alzheimers',
                'parameters': DiseaseState.get_default_parameters(),
                'is_default': True,
            }
        )
        self.stdout.write("  Disease State: Early Alzheimer's")
        
        self.stdout.write(self.style.SUCCESS("Sample data seeded successfully!"))
