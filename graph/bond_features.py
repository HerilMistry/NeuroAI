def bond_edges(mol):
    """
    Extract bond connections (undirected).
    """
    edges = []
    for bond in mol.GetBonds():
        i = bond.GetBeginAtomIdx()
        j = bond.GetEndAtomIdx()
        edges.append((i, j))
        edges.append((j, i))
    return edges
