#!/usr/bin/python3 -u
import os.path
import numpy as np
from aegon.libutils import readxyzs
#------------------------------------------------------------------------------------------
def LennardJones(moleculein):
    epsilon=1.0
    sigma=3.0/np.power(2,1/6)
    energy=0.0
    natoms=len(moleculein)
    for iatom in range(natoms):
        ipos=moleculein[iatom].position
        for jatom in range(iatom+1,natoms):
            jpos = moleculein[jatom].position
            rij = np.linalg.norm(jpos - ipos)
            arg1=(sigma/rij)
            arg6=np.power(arg1,6)
            energy += arg6 * (arg6 - 1.0)
    energy=energy*4.0*epsilon
    return energy
#------------------------------------------------------------------------------------------
ljenergy={}
ljnet=readxyzs('Wales003to150.xyz')
for imol in ljnet:
    ljenergy[len(imol)]=imol.info['e']

ii=4
lista=[]
file='LJ'+str(ii).zfill(3)+'.xyz'
title = "resultados.txt"

if os.path.exists(title):
    os.remove(title)

with open(title, 'a') as f_out:
    while os.path.isfile(file):
        mol=readxyzs(file)
        nm=len(mol)
        #egulp=mol[0].e
        id=mol[0].info['i']
        nn=id[6:11]
        efili=LennardJones(mol[0])
        etrue=ljenergy[ii]
        deltae=(efili-etrue)
        pg='X'
        result_line = '%s (%4d) %11.6f %5.2f %-3s ISO%s\n' % (file[2:6], nm, efili, deltae, pg, nn)
        f_out.write(result_line)
        ii=ii+1
        file='LJ'+str(ii).zfill(3)+'.xyz'
exit()
#------------------------------------------------------------------------------------------
