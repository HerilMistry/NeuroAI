from rdkit import Chem

def load_smiles(smiles: str):
    """
    Convert SMILES string to RDKit molecule.
    """
    mol = Chem.MolFromSmiles(smiles)
    if mol is None:
        raise ValueError(f"Invalid SMILES: {smiles}")
    return mol
