def atom_features(atom):
    """
    Extract atom-level features.
    """
    return [
        atom.GetAtomicNum(),
        atom.GetDegree(),
        int(atom.GetIsAromatic())
    ]
