# Data Files Directory

This directory is for storing local data files for ingestion.

**DO NOT version control large datasets.**

## Expected Files

Place the following files here for ingestion:

- `drugbank.xml` or `drugbank.csv` - DrugBank export
- `chembl_compounds.csv` - ChEMBL compound data
- `disgenet_gene_disease.csv` - DisGeNET associations

## Ingestion Commands

```bash
python manage.py ingest_drugbank --file data_files/drugbank.csv --version 5.1.10
python manage.py seed_sample_data  # For development only
```
