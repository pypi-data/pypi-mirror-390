import os
import time
import numpy as np
from numba import jit
import multiprocessing as mp
from ase.data import atomic_masses
from aegon.libutils import readxyzs, writexyzs, centroid, sort_by_energy, align_two
#------------------------------------------------------------------------------------------
tolsij = 0.95
tolene = 0.10
#------------------------------------------------------------------------------------------
# Funciones USR optimizadas
#------------------------------------------------------------------------------------------

@jit(nopython=True)
def lastwo_central_moment_numba(arr):
    xavg = np.mean(arr)
    res = arr - xavg
    ssq2 = np.mean(res**2) 
    ssq3 = np.mean(res**3) 
    return np.array([ssq2, ssq3])

def lastwo_central_moment(listxxx):
    arr = np.array(listxxx, dtype=np.float64)
    return lastwo_central_moment_numba(arr)

@jit(nopython=True) 
def find_extreme_points_numba(positions, centroid):
    n_atoms = len(positions)
    distances_to_centroid = np.zeros(n_atoms)    
    for i in range(n_atoms):
        distances_to_centroid[i] = np.linalg.norm(positions[i] - centroid)
    closest_idx = np.argmin(distances_to_centroid)
    farthest_idx = np.argmax(distances_to_centroid)
    distances_from_farthest = np.zeros(n_atoms)
    for i in range(n_atoms):
        distances_from_farthest[i] = np.linalg.norm(positions[i] - positions[farthest_idx])
    farthest_from_farthest_idx = np.argmax(distances_from_farthest)
    return (centroid, positions[closest_idx], 
            positions[farthest_idx], positions[farthest_from_farthest_idx])

def four_points(atoms):
    positions = np.array([atom.position for atom in atoms])
    ctd = centroid(atoms)
    return find_extreme_points_numba(positions, ctd)

@jit(nopython=True)
def calculate_usr_descriptors_numba(positions, points, masses=None, mass_avg=None):
    ctd, cst, fct, ftf = points
    n_atoms = len(positions)
    lctd = np.zeros(n_atoms)
    lcst = np.zeros(n_atoms) 
    lfct = np.zeros(n_atoms)
    lftf = np.zeros(n_atoms)    
    for i in range(n_atoms):
        pos = positions[i]
        lctd[i] = np.linalg.norm(pos - ctd)
        lcst[i] = np.linalg.norm(pos - cst)
        lfct[i] = np.linalg.norm(pos - fct)
        lftf[i] = np.linalg.norm(pos - ftf)
    a1 = lastwo_central_moment_numba(lctd)
    a2 = lastwo_central_moment_numba(lcst)
    a3 = lastwo_central_moment_numba(lfct)
    a4 = lastwo_central_moment_numba(lftf)
    if masses is None: 
        return np.concatenate((a1, a2, a3, a4))
    lctdm = np.zeros(n_atoms)
    lcstm = np.zeros(n_atoms)
    lfctm = np.zeros(n_atoms)
    lftfm = np.zeros(n_atoms)
    for i in range(n_atoms):
        mi = masses[i]
        lctdm[i] = lctd[i] * mi / mass_avg
        lcstm[i] = lcst[i] * mi / mass_avg
        lfctm[i] = lfct[i] * mi / mass_avg
        lftfm[i] = lftf[i] * mi / mass_avg
    b1 = lastwo_central_moment_numba(lctdm)
    b2 = lastwo_central_moment_numba(lcstm)
    b3 = lastwo_central_moment_numba(lfctm)
    b4 = lastwo_central_moment_numba(lftfm)
    return np.concatenate((a1, a2, a3, a4, b1, b2, b3, b4))

def USRMonoatom(moleculein):
    positions = np.array([atom.position for atom in moleculein])
    points = four_points(moleculein)
    return calculate_usr_descriptors_numba(positions, points)

def USRMultiatom(moleculein):
    positions = np.array([atom.position for atom in moleculein])
    masses = np.array([atomic_masses[atom.number] for atom in moleculein])
    mass_avg = np.mean(masses)
    points = four_points(moleculein)
    return calculate_usr_descriptors_numba(positions, points, masses, mass_avg)

@jit(nopython=True)
def similarity_numba(vi, vj, n_features):
    manhattan_distance = np.sum(np.abs(vi - vj))
    return 1.0 / (1.0 + manhattan_distance / float(n_features))

def compute_similarity_matrix_serial(descriptors, n_features):
    n_mols = len(descriptors)
    similarity_matrix = np.zeros((n_mols, n_mols))
    for i in range(n_mols):
        vi = descriptors[i]
        for j in range(i, n_mols):
            vj = descriptors[j]
            sij = similarity_numba(vi, vj, n_features)
            similarity_matrix[i, j] = sij
            similarity_matrix[j, i] = sij
    return similarity_matrix

def find_similar_elements(listmol, similarity_matrix, tols=tolsij, tole=tolene):
    similar_indices = []
    num_elements = similarity_matrix.shape[0]
    #debug = []    
    for i in range(num_elements):
        for j in range(i + 1, num_elements):
            edf = np.abs(listmol[i].info['e'] - listmol[j].info['e'])
            if (similarity_matrix[i, j] >= tols) and (edf <= tole):
                similar_indices.append(j)
                #x1 = listmol[j].copy()
                #x2 = listmol[i].copy()
                #y1, y2 = align_two(x1, x2)
                #debug.extend([y1, y2])
    similar_indices = list(set(similar_indices))
    disimilars_atoms = [listmol[i] for i in range(num_elements) if i not in similar_indices]
    #if debug: 
    #    writexyzs(debug, 'debug.xyz')
    return disimilars_atoms

def disc_USR_sublist(args):
    """Procesa una sublista de moléculas con USR - versión para multiprocessing"""
    sublist, tols, tole, mono = args
    num_molecules = len(sublist)
    if num_molecules == 0: 
        return []
    
    n_features = 8 if mono else 16
    
    # Calcular descriptores
    if mono:
        descriptors = [USRMonoatom(mol) for mol in sublist]
    else:
        descriptors = [USRMultiatom(mol) for mol in sublist]
    
    # Calcular matriz de similitud
    similarity_matrix = compute_similarity_matrix_serial(descriptors, n_features)
    
    return find_similar_elements(sublist, similarity_matrix, tols, tole)

def split_list(lst, n):
    """Divide una lista en n sublistas aproximadamente iguales"""
    k, m = divmod(len(lst), n)
    return [lst[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]

def _second_pass_filtering(molecules, tols, tole, mono):
    """
    Filtrado eficiente para segunda pasada cuando hay muchas moléculas
    Compara solo moléculas cercanas en energía para mayor eficiencia
    """
    if len(molecules) <= 1:
        return molecules
    
    molecules_sorted = sorted(molecules, key=lambda x: x.info['e'])
    n_mols = len(molecules_sorted)
    
    # Calcular descriptores una sola vez
    n_features = 8 if mono else 16
    if mono:
        descriptors = [USRMonoatom(mol) for mol in molecules_sorted]
    else:
        descriptors = [USRMultiatom(mol) for mol in molecules_sorted]
    
    keep_indices = set(range(n_mols))
    
    # Comparar cada molécula con sus vecinos cercanos en energía
    for i in range(n_mols):
        if i not in keep_indices:
            continue
            
        vi = descriptors[i]
        ei = molecules_sorted[i].info['e']
        
        # Buscar en un rango limitado alrededor de la energía actual
        search_range = min(50, n_mols // 10)
        start_j = max(0, i - search_range)
        end_j = min(n_mols, i + search_range + 1)
        
        for j in range(start_j, end_j):
            if j <= i or j not in keep_indices:
                continue
                
            edf = np.abs(ei - molecules_sorted[j].info['e'])
            if edf > tole:
                continue
                
            sij = similarity_numba(vi, descriptors[j], n_features)
            if sij >= tols:
                keep_indices.remove(j)
    
    return [molecules_sorted[i] for i in sorted(keep_indices)]

def comparator_usr_serial(molecules, tols=tolsij, tole=tolene, mono=False):
    """Comparador USR serial - completamente en memoria"""
    #start = time.time()
    ni = len(molecules)
    
    if ni == 0:
        return []
    
    n_features = 8 if mono else 16
    
    # Calcular descriptores
    if mono:
        descriptors = [USRMonoatom(mol) for mol in molecules]
    else:
        descriptors = [USRMultiatom(mol) for mol in molecules]
    
    # Calcular matriz de similitud
    similarity_matrix = compute_similarity_matrix_serial(descriptors, n_features)
    
    # Encontrar elementos similares
    filtered_molecules = find_similar_elements(molecules, similarity_matrix, tols, tole)
    
    #nf = len(filtered_molecules)
    #end = time.time()
    #print('USR comparison (serial) at %5.2f s [%d -> %d]' % (end - start, ni, nf))
    return filtered_molecules

def comparator_usr_batch(molecules, batch_size=100, tols=tolsij, tole=tolene, mono=False):
    """
    Versión alternativa que procesa por lotes sin multiprocessing
    Útil cuando multiprocessing tiene problemas
    """
    start = time.time()
    ni = len(molecules)
    
    if ni == 0:
        return []
    
    molecules = sort_by_energy(molecules, 1)
    
    # Si la lista es pequeña, procesar directamente
    if ni <= batch_size:
        return comparator_usr_serial(molecules, tols, tole, mono)
    
    # Procesar por lotes
    all_filtered_mols = []
    n_batches = (ni + batch_size - 1) // batch_size
    
    print(f"Processing {ni} molecules in {n_batches} batches of {batch_size}...")
    
    for i in range(n_batches):
        start_idx = i * batch_size
        end_idx = min((i + 1) * batch_size, ni)
        batch = molecules[start_idx:end_idx]
        
        #print(f"Processing batch {i+1}/{n_batches} ({len(batch)} molecules)...")
        filtered_batch = comparator_usr_serial(batch, tols, tole, mono)
        all_filtered_mols.extend(filtered_batch)
    
    # Aplicar segunda pasada de filtrado entre lotes
    if len(all_filtered_mols) > 1:
        print("Applying second pass filtering between batches...")
        all_filtered_mols = _second_pass_filtering(all_filtered_mols, tols, tole, mono)
    
    # Ordenar por energía
    all_filtered_mols = sort_by_energy(all_filtered_mols, 1)
    
    nf = len(all_filtered_mols)
    end = time.time()
    print('USR comparison (batch) at %5.2f s [%d -> %d]' % (end - start, ni, nf))
    
    return all_filtered_mols

#------------------------------------------------------------------------------------------
# Funciones adicionales para comparación con referencias
#------------------------------------------------------------------------------------------

def make_similarity_matrix_compare(moleculein, moleculeref, mono=False):
    """Matriz de similitud comparativa optimizada"""
    n_features = 8 if mono else 16
    
    # Calcular descriptores
    if mono:
        descriptors1 = [USRMonoatom(mol) for mol in moleculein]
        descriptors2 = [USRMonoatom(mol) for mol in moleculeref]
    else:
        descriptors1 = [USRMultiatom(mol) for mol in moleculein]
        descriptors2 = [USRMultiatom(mol) for mol in moleculeref]
    
    total_molecules1, total_molecules2 = len(moleculein), len(moleculeref)
    similarity_matrix = np.zeros((total_molecules1, total_molecules2), dtype=float)
    
    # Llenar matriz
    for i in range(total_molecules1):
        vi = descriptors1[i]
        for j in range(total_molecules2):
            vj = descriptors2[j]
            similarity_matrix[i, j] = similarity_numba(vi, vj, n_features)
    
    return similarity_matrix

def molin_sim_molref(moleculein, moleculeref, tols=tolsij, tole=tolene, mono=False):
    """Comparación molécula-referencia optimizada"""
    start = time.time()
    ni = len(moleculein)
    
    matrixs = make_similarity_matrix_compare(moleculein, moleculeref, mono)
    
    similares = []
    for i, imol in enumerate(moleculein):
        for j, jmol in enumerate(moleculeref):
            if (matrixs[i, j] >= tols) and (np.abs(imol.info['e'] - jmol.info['e']) <= tole):
                similares.append(i)
                break
    
    moleculeout = [imol for i, imol in enumerate(moleculein) if i not in similares] 
    nf = len(moleculeout)
    end = time.time()
    print('USR comparison (vs reference) at %5.2f s [%d -> %d]' % (end - start, ni, nf))
    return moleculeout
