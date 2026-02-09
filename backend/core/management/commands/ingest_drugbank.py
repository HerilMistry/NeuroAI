"""
Management command to ingest drug data from DrugBank XML/CSV exports.

Usage:
    python manage.py ingest_drugbank --file data_files/drugbank.xml --version 5.1.10

This is a skeleton implementation. Actual parsing depends on the file format obtained.
"""
import hashlib
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from core.models import Drug, DatasetProvenance
from core.logic import calculate_cns_mpo_score


class Command(BaseCommand):
    help = 'Ingest drug data from DrugBank export file'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            required=True,
            help='Path to DrugBank data file (XML or processed CSV)',
        )
        parser.add_argument(
            '--version',
            type=str,
            default='unknown',
            help='DrugBank version string',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Parse file but do not save to database',
        )
    
    def handle(self, *args, **options):
        file_path = Path(options['file'])
        
        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")
        
        self.stdout.write(f"Starting DrugBank ingestion from {file_path}")
        
        # Compute file hash for provenance
        file_hash = self._compute_hash(file_path)
        
        # Track statistics
        stats = {
            'created': 0,
            'updated': 0,
            'skipped': 0,
            'errors': 0,
        }
        
        # Parse file based on extension
        if file_path.suffix == '.csv':
            stats = self._parse_csv(file_path, options['dry_run'])
        elif file_path.suffix == '.xml':
            stats = self._parse_xml(file_path, options['dry_run'])
        else:
            raise CommandError(f"Unsupported file format: {file_path.suffix}")
        
        # Record provenance
        if not options['dry_run']:
            DatasetProvenance.objects.create(
                dataset_name='drugbank',
                version=options['version'],
                file_path=str(file_path),
                file_hash=file_hash,
                record_count=stats['created'] + stats['updated'],
                error_count=stats['errors'],
                notes=f"Ingested via management command",
            )
        
        self.stdout.write(self.style.SUCCESS(
            f"Ingestion complete: {stats['created']} created, "
            f"{stats['updated']} updated, {stats['errors']} errors"
        ))
    
    def _compute_hash(self, path: Path) -> str:
        """Compute SHA-256 hash of file."""
        hasher = hashlib.sha256()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _parse_csv(self, path: Path, dry_run: bool) -> dict:
        """
        Parse DrugBank CSV export.
        
        Expected columns:
        - drugbank_id, name, smiles, molecular_weight, logp, hbd, hba, tpsa, pka
        """
        import csv
        
        stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
        
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                try:
                    drugbank_id = row.get('drugbank_id', '').strip()
                    if not drugbank_id:
                        stats['skipped'] += 1
                        continue
                    
                    # Parse numeric fields safely
                    mw = self._parse_float(row.get('molecular_weight'))
                    logp = self._parse_float(row.get('logp'))
                    hbd = self._parse_int(row.get('hbd'))
                    hba = self._parse_int(row.get('hba'))
                    tpsa = self._parse_float(row.get('tpsa'))
                    pka = self._parse_float(row.get('pka'))
                    
                    # Calculate CNS MPO score
                    mpo_result = calculate_cns_mpo_score(
                        molecular_weight=mw,
                        logp=logp,
                        hbd=hbd,
                        tpsa=tpsa,
                        pka=pka,
                    )
                    
                    if not dry_run:
                        drug, created = Drug.objects.update_or_create(
                            drugbank_id=drugbank_id,
                            defaults={
                                'name': row.get('name', drugbank_id),
                                'smiles': row.get('smiles'),
                                'molecular_weight': mw,
                                'logp': logp,
                                'hbd': hbd,
                                'hba': hba,
                                'tpsa': tpsa,
                                'pka': pka,
                                'cns_mpo_score': mpo_result.total_score,
                                'cns_viable': mpo_result.is_viable,
                                'cns_score_explanation': mpo_result.component_scores,
                                'data_source': 'drugbank',
                            }
                        )
                        if created:
                            stats['created'] += 1
                        else:
                            stats['updated'] += 1
                    else:
                        stats['created'] += 1
                    
                except Exception as e:
                    stats['errors'] += 1
                    self.stderr.write(f"Error processing row: {e}")
        
        return stats
    
    def _parse_xml(self, path: Path, dry_run: bool) -> dict:
        """
        Parse DrugBank XML export.
        This is a placeholder - full XML parsing requires xml.etree or lxml.
        """
        self.stdout.write(self.style.WARNING(
            "XML parsing is a placeholder. Implement based on actual DrugBank XML schema."
        ))
        return {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
    
    def _parse_float(self, value) -> float | None:
        if value is None or value == '':
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _parse_int(self, value) -> int | None:
        if value is None or value == '':
            return None
        try:
            return int(float(value))
        except (ValueError, TypeError):
            return None
