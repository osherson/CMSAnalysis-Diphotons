#!/usr/bin/env python
# coding: utf-8

###
#!!!!!!!!!!!!!!!!!!!!
# This ill not run inside CMSSW, make sure you haven't done cmsenv if you want to run this
###

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

galphas = [0.005, 0.01, 0.015, 0.02, 0.025]
efile = open("alphaBinEdges.txt")

edges=[float(ll) for ll in efile.readlines()]
xs = [ii for ii in range(0,len(edges))]

plt.scatter(edges,edges, color='black', label="GenEdges")
line = np.polyfit(edges, edges,deg=2)
ppt = np.polyval(line, edges)
plt.plot(edges, ppt, linestyle='--',color='blue', label="Fit")

plt.legend(loc='best')
plt.xlabel("alpha",fontsize=14)
plt.ylabel("alpha",fontsize=14)
plt.show()

def findClosestG(ga, aa):
    dmin = 999.
    
    for gg in ga:
        diff = abs(gg-aa)
        if (diff < dmin):
            dmin = diff
            ng = gg
    return ng


N_SLICE = 30
want_alphas = np.linspace(0.005, 0.025, N_SLICE)
use_was = []

thresh = edges[1] - edges[0]

for wa in want_alphas:
    ng = findClosestG(galphas, wa)
    idx = 3*galphas.index(ng)+1
    
    ed, ee, eu = edges[idx-1], edges[idx] ,edges[idx+1]
    if(ed > ee): print("problem D")
    elif(eu < ee): print("problem U")
    
    if(wa > ed and wa < eu): continue
    if(abs(eu - wa) < thresh or abs(ed-wa)<thresh): continue
    else: use_was.append(wa)

plt.figure(figsize=(6,6))
plt.scatter(edges,edges, color='black', label='Gen Points')
plt.scatter(use_was, use_was, color='orange', label="Int Points")
plt.plot(edges, ppt, linestyle='--',color='blue', label="Fit")

plt.xlabel("alpha", fontsize=14)
plt.ylabel("alpha", fontsize=14)

plt.legend(loc="best",fontsize=14)
plt.show()

BinEdges = list(np.concatenate((edges,use_was)))
BinEdges.append(0.)
BinEdges.append(0.03)
finalBinEdges = np.sort(BinEdges)

len(finalBinEdges)

for bb in finalBinEdges:
    print(bb)

