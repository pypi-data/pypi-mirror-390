#!/usr/bin/python3 -u
import os
from aegon.libutils import readxyzs, writexyzs, rename, cutter_energy
from aegon.libcalc_lj    import opt_LJ_parallel
from growpal.libgrowpal  import growpal_parallel, display_info
from growpal.libdisc_usr import comparator_usr_batch
from growpal.libselect_clustering import selectbyclustering_comb_prom
#------------------------------------------------------------------------------------------------
nproc = 26
growatom='Mo'
ecut=50.0
#rule0=[150, 150, 150, 150, 150, 100, 100, 50]
rule=[150, 150, 150, 150, 150, 150, 100, 100, 100, 100, 100, 100]
#------------------------------------------------------------------------------------------
molecu0=False
if __name__ == "__main__":
    for iii in range(4, 150+1):
        base_name = 'LJ'+str(iii).zfill(3)
        if os.path.isfile(base_name+'.xyz'):
            print ("%s exists" %(base_name))
            anterior=base_name+'.xyz'
            continue
        if not molecu0:
            molecu0 = readxyzs(anterior)

        molecu0 = rename(molecu0, base_name, 5)
        molecu1 = growpal_parallel(molecu0, growatom, dtol=1.2, n_cores=nproc)
        #----------OPT----------------
        for batch_size in [100, 150, 100, 150, 100]:
            molecu0 = parallel_opt_LJ(molecu1, n_jobs=nproc)
            molecu1 = comparator_usr_batch(molecu0, batch_size=batch_size, tols=0.99, tole=0.1, mono=True)
        #--------------------------------------------
        molecu1=cutter_energy(molecu1, ecut)
        molecu0=selectbyclustering_comb_prom(molecu1, rule, "MBTR_dis", "MBTR_cos")
        display_info(molecu0[0:5], base_name)
        writexyzs(molecu0, base_name+'.xyz')
