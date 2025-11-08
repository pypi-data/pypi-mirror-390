import numpy as np
from rdkit import Chem
from rdkit.Chem import AllChem, rdMolAlign

from spyrmsd.molecule import Molecule
from spyrmsd.rmsd import rmsd, symmrmsd
import spyrmsd
import math

def mol_to_coords(mol, conf_id=0):
    """Extract 3D coordinates from RDKit Mol object"""
    conf = mol.GetConformer(conf_id)
    coords = np.array([list(conf.GetAtomPosition(i)) for i in range(mol.GetNumAtoms())])
    return coords

def mol_to_atomic_nums(mol):
    """Extract atomic numbers from RDKit Mol object"""
    return np.array([atom.GetAtomicNum() for atom in mol.GetAtoms()])


# Create benzene
def test_benzene():
    # Test Case 1: Benzene with 60-degree rotation (perfect symmetry)
    benzene_smiles = "c1ccccc1"
    mol1 = Chem.MolFromSmiles(benzene_smiles)
    mol1 = Chem.AddHs(mol1)
    AllChem.EmbedMolecule(mol1, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol1)

    # Create a copy and rotate 60 degrees around Z-axis
    mol2 = Chem.Mol(mol1)
    conf2 = mol2.GetConformer()

    # 60-degree rotation matrix around Z-axis
    angle = np.pi / 3  # 60 degrees
    rotation_matrix = np.array([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1]
    ])

    for i in range(mol2.GetNumAtoms()):
        pos = conf2.GetAtomPosition(i)
        new_pos = rotation_matrix @ np.array([pos.x, pos.y, pos.z])
        conf2.SetAtomPosition(i, new_pos.tolist())

    # Calculate RMSD
    m1 = Molecule.from_rdkit(mol1)
    m1.strip()
    coords1 = m1.coordinates
    m1_anum = m1.atomicnums
    m1_amat = m1.adjacency_matrix
    m2 = Molecule.from_rdkit(mol2)

    m2.strip()
    coords2 = m2.coordinates
    m2_anum = m2.atomicnums
    m2_amat = m2.adjacency_matrix

    # Without symmetry consideration (standard RMSD)
    rmsd_standard = rmsd(coords1, coords2, m1_anum, m2_anum, minimize=False)

    # With symmetry consideration
    rmsd_symm, mapping = symmrmsd(
        coords1, 
        coords2, 
        m1_anum, 
        m2_anum, 
        m1_amat, 
        m2_amat, 
        minimize=False, 
        return_best_isomorphism=True)

    assert math.isclose(rmsd_standard, 1.394, abs_tol=0.1)
    assert math.isclose(rmsd_symm, 0.017, abs_tol=0.1)
    assert mapping == ([1, 2, 3, 4, 5, 0], [0, 1, 2, 3, 4, 5])

    coords1_reordered = coords1[mapping[0],:]
    manual_rmsd0 = np.sqrt(np.mean(np.sum((coords1 - coords2)**2, axis=1)))
    manual_rmsd1 = np.sqrt(np.mean(np.sum((coords1_reordered - coords2)**2, axis=1)))

    assert math.isclose(manual_rmsd0, 1.394, abs_tol=0.1)
    assert math.isclose(manual_rmsd1, 0.017, abs_tol=0.1)


def test_ethanol():
    # Test Case 2: Ethanol (no symmetry vs with symmetry)
    ethanol_smiles = "CCO"
    mol3 = Chem.MolFromSmiles(ethanol_smiles)
    mol3 = Chem.AddHs(mol3)
    AllChem.EmbedMolecule(mol3, randomSeed=42)
    AllChem.MMFFOptimizeMolecule(mol3)

    # Create rotated copy - rotate methyl group 120 degrees
    mol4 = Chem.Mol(mol3)

    # Get the methyl carbon and its hydrogens
    # Assuming atom order: C-C-O with hydrogens
    # We'll rotate around the C-C bond

    m3 = Molecule.from_rdkit(mol3)
    m4 = Molecule.from_rdkit(mol4)
    coords3 = m3.coordinates
    coords4 = m4.coordinates

    # Find methyl carbon (carbon with 3 hydrogens)
    methyl_h_indices = []
    methyl_c_idx = None
    for atom in mol4.GetAtoms():
        if atom.GetSymbol() == 'C':
            h_count = sum(1 for neighbor in atom.GetNeighbors() if neighbor.GetSymbol() == 'H')
            if h_count == 3:
                methyl_c_idx = atom.GetIdx()
                methyl_h_indices = [n.GetIdx() for n in atom.GetNeighbors() if n.GetSymbol() == 'H']
                break

    # Rotate the three methyl hydrogens by 120 degrees
    # This should give RMSD ~0 with symmetry, but >0 without
    angle = 2 * np.pi / 3  # 120 degrees

    # Get the axis of rotation (C-C bond)
    c_atoms = [atom.GetIdx() for atom in mol4.GetAtoms() if atom.GetSymbol() == 'C']
    axis_start = coords4[c_atoms[0]]
    axis_end = coords4[c_atoms[1]]
    axis = axis_end - axis_start
    axis = axis / np.linalg.norm(axis)

    # Rodrigues rotation formula for points around arbitrary axis
    def rotate_point(point, axis_point, axis, angle):
        point = point - axis_point
        rotated = (point * np.cos(angle) + 
                np.cross(axis, point) * np.sin(angle) + 
                axis * np.dot(axis, point) * (1 - np.cos(angle)))
        return rotated + axis_point

    # Rotate only the methyl hydrogens
    for h_idx in methyl_h_indices:
        coords4[h_idx] = rotate_point(coords4[h_idx], coords4[methyl_c_idx], axis, angle)

    # Calculate RMSD
    rmsd_standard_eth = rmsd(
        coords3, coords4, 
        m3.atomicnums, 
        m4.atomicnums,
        minimize=True)
    
    rmsd_symm_eth, mapping_eth = symmrmsd(
        coords3, 
        coords4,
        m3.atomicnums, 
        m4.atomicnums,
        m3.adjacency_matrix, 
        m4.adjacency_matrix,
        minimize=True,
        return_best_isomorphism=True,
    )

    assert math.isclose(rmsd_standard_eth,  0.947867, abs_tol=0.1)
    assert math.isclose(rmsd_symm_eth, 0.009792, abs_tol=0.1)
    assert mapping_eth == ([0, 1, 2, 5, 3, 4, 6, 7, 8], [0, 1, 2, 3, 4, 5, 6, 7, 8])

    coords3_reordered = coords3[mapping_eth[0],:]
    manual_rmsd0 = np.sqrt(np.mean(np.sum((coords3 - coords4)**2, axis=1)))
    manual_rmsd1 = np.sqrt(np.mean(np.sum((coords3_reordered - coords4)**2, axis=1)))

    assert math.isclose(manual_rmsd0, 0.947867, abs_tol=0.1)
    assert math.isclose(manual_rmsd1, 0.009792, abs_tol=0.1)