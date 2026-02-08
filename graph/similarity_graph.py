from rdkit.Chem import AllChem
from rdkit import DataStructs

def compute_fingerprint(mol, radius=2, n_bits=2048):
    """
    Compute Morgan (ECFP) fingerprint.
    """
    return AllChem.GetMorganFingerprintAsBitVect(
        mol, radius, nBits=n_bits
    )

def tanimoto_similarity(fp1, fp2):
    """
    Compute Tanimoto similarity between two fingerprints.
    """
    return DataStructs.TanimotoSimilarity(fp1, fp2)

def build_similarity_edges(mols, threshold=0.4):
    """
    Build edges between molecules using similarity threshold.
    """
    fingerprints = [compute_fingerprint(mol) for mol in mols]
    edges = []

    for i in range(len(mols)):
        for j in range(i + 1, len(mols)):
            sim = tanimoto_similarity(fingerprints[i], fingerprints[j])
            if sim >= threshold:
                edges.append((i, j))
                edges.append((j, i))

    return edges
