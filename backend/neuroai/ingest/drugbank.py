from neuroai.models import Drug
import xml.etree.ElementTree as ET

def ingest_drugbank(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    ns = {"db": "http://www.drugbank.ca"}

    for drug in root.findall("db:drug", ns):
        name = drug.findtext("db:name", namespaces=ns)
        drugbank_id = drug.findtext("db:drugbank-id", namespaces=ns)

        approved = drug.find("db:groups/db:group", ns) is not None

        Drug.objects.get_or_create(
            drugbank_id=drugbank_id,
            defaults={
                "name": name,
                "approved": approved,
            }
        )
