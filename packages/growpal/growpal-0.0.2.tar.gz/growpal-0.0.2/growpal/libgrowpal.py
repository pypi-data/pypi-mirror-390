import os
import time
import numpy as np
from ase import Atom
from multiprocessing import Pool, cpu_count
from aegon.libpymatgen import inequivalent_finder
from aegon.libutils import rename, adjacency_matrix, readxyzs, writexyzs, sort_by_energy
#------------------------------------------------------------------------------------------
def neighbor_finder(atoms, dtol=1.2):
    """
    Build adjacency dictionary using list comprehension
    """
    dict_neig = {}
    adj_mtx = adjacency_matrix(atoms, dtol)
    for i, row in enumerate(adj_mtx):
        dict_neig[i] = [j for j, val in enumerate(row) if val == 1]
    return dict_neig

#------------------------------------------------------------------------------------------
def triangle_finder(neighbors_dict, atom):
    """
    Optimized version using sets for O(1) lookups
    """
    triangles = []
    neiga = neighbors_dict[atom]
    set_neiga = set(neiga)
    
    for n in neiga:
        neigb = neighbors_dict[n]
        for n2 in neigb:
            if n2 in set_neiga:
                auxlist = [atom, n, n2]
                auxlist.sort()
                if auxlist not in triangles:
                    triangles.append(auxlist)
    return triangles

#------------------------------------------------------------------------------------------
def focused_expansion(molin, vector):
    """
    Vectorized version
    """
    molout = molin.copy()
    positions = molout.positions
    vectors = positions - vector
    distances = np.linalg.norm(vectors, axis=1, keepdims=True)
    
    distances = np.where(distances == 0, 1e-10, distances)
    
    rnorm = vectors / distances
    edel = np.exp(-distances) * 1.2
    new_positions = positions + rnorm * edel
    
    molout.positions = new_positions
    return molout

#------------------------------------------------------------------------------------------
def add_all_interstitial_atoms(original_molecule, neighbors_dict, specie):
    """
    Optimized version using tuples and sets for visited_t
    """
    visited_t = set()
    xxx_mol = original_molecule.copy()
    atom_list = range(len(original_molecule))
    
    all_positions = original_molecule.positions
    
    for a in atom_list:
        triangles = triangle_finder(neighbors_dict, a)
        for t in triangles:
            t_tuple = tuple(t)
            if t_tuple in visited_t:
                continue
            
            v1 = all_positions[t[0]]
            v2 = all_positions[t[1]] 
            v3 = all_positions[t[2]]
            mid_vect = (v1 + v2 + v3) / 3
            
            add_atom = Atom(symbol=specie, position=mid_vect)
            xxx_mol.append(add_atom)
            visited_t.add(t_tuple)
            
    return xxx_mol

#------------------------------------------------------------------------------------------
def add_ineq_interstitial_atoms_with_expansion(original_molecule, atom_list):
    """
    Process eligible atoms with expansion
    """
    molist_out = []
    for add_atom in atom_list:
        mid_vect = np.array(add_atom.position)
        add_mol = original_molecule.copy()
        exp_mol = focused_expansion(add_mol, mid_vect)
        exp_mol.append(add_atom)
        molist_out.append(exp_mol)
    return molist_out

#------------------------------------------------------------------------------------------
def process_single_molecule(args):
    """
    Process one molecule - designed for parallel execution
    """
    imol, specie, dtol = args
    org_nnn = len(imol)
    org_mol = imol.copy()
    org_mol.info['e'] = 0.0
    org_mol.translate(-org_mol.get_center_of_mass())
    
    all_neighbors = neighbor_finder(org_mol, dtol)
    xxx_mol = add_all_interstitial_atoms(org_mol, all_neighbors, specie)
    inequivalent = inequivalent_finder(xxx_mol)
    elegible_atoms = [xxx_mol[i] for i in inequivalent if i >= org_nnn]
    mod_mol = add_ineq_interstitial_atoms_with_expansion(org_mol, elegible_atoms)
    mod_mol = rename(mod_mol, imol.info['i'], 4)
    
    return mod_mol

#------------------------------------------------------------------------------------------
def growpal_parallel(poscarlist, specie, dtol=1.2, n_cores=None):
    """
    Parallel version using multiprocessing Pool
    """
    start = time.time()
    
    if n_cores is None:
        n_cores = max(1, cpu_count() - 1)
    
    args_list = [(imol, specie, dtol) for imol in poscarlist]
    
    with Pool(processes=n_cores) as pool:
        results = pool.map(process_single_molecule, args_list)
    
    molist_out = []
    for result in results:
        molist_out.extend(result)
    
    end = time.time()
    print('GrowPal generation at %5.2f s' % (end - start))
    
    return molist_out

#------------------------------------------------------------------------------------------
def display_info(moleculein, stage_string):
    print("-------------------------------------------------------------------")
    print("------------------------- SUMMARY %s -------------------------" %(stage_string))
    print("Number File--------Name   Energy (ev)   Delta----E T")
    molzz = sort_by_energy(moleculein, 1)
    emin = molzz[0].info['e']
    for ii, imol in enumerate(molzz):
        ei = imol.info['e']
        id = imol.info['i']
        nt = imol.info['c']
        deltae  =  ei - emin
        kk=str(ii+1).zfill(6)
        print("%s %s %13.8f %12.8f %d" %(kk, id, ei, deltae, nt))
#------------------------------------------------------------------------------------------
#if __name__ == "__main__":
#    mol1 = readxyzs('../LJ012.xyz')
#    mol2 = growpal_parallel(mol1, 'Nb')
#    writexyzs(mol2, 'out.xyz')
