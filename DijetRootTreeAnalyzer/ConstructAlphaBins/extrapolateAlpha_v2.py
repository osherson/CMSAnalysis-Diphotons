#!/usr/bin/env python
# coding: utf-8

###
#!!!!!!!!!!!!!!!!!!!!
# This will not run inside CMSSW, make sure you haven't done cmsenv if you want to run this
###

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

galphas = [0.005, 0.01, 0.015, 0.02, 0.025]
efile = open("alphaBinEdges.txt")

edges=[float(ll) for ll in efile.readlines()]
xs = [ii for ii in range(0,len(edges))]
edges.append(0.03)

plt.scatter(edges,edges, color='black', label="GenEdges",s=25)
line = np.polyfit(edges, edges,deg=2)
ppt = np.polyval(line, edges)
plt.plot(edges, ppt, linestyle='--',color='blue', label="Fit")

plt.legend(loc='best')
plt.xlabel("alpha",fontsize=14)
plt.ylabel("alpha",fontsize=14)
plt.xlim(0,0.035)
plt.ylim(0,0.035)
plt.savefig("Plots/alphaBins_genPoints.png")
plt.show()

use_was = []

gsize=3
for ii in range(2, len(edges)-3, gsize):
  wl = edges[ii] - edges[ii-1]
  wh = edges[ii+gsize] - edges[ii+gsize-1]

  print(wl, wh, wh - wl)

  np = edges[ii] + max(wl,wh)
  while np < (edges[ii+1] - max(wl,wh)):
    use_was.append(round(np,4))
    np += max(wl,wh)

np = edges[-2] + max(wl,wh)
while (np < 0.03-max(wl,wh)):
  use_was.append(round(np,4))
  np += max(wl,wh)

print("done with loop")
plt.clf()
plt.figure(figsize=(6,6))
plt.scatter(edges,edges, color='black', label='Gen Points',s=25)
plt.scatter(use_was, use_was, color='orange', label="Int Points",s=25)
plt.plot(edges, ppt, linestyle='--',color='blue', label="Fit")

plt.xlabel("alpha", fontsize=14)
plt.ylabel("alpha", fontsize=14)

plt.legend(loc="best",fontsize=14)
plt.savefig("Plots/alphaBins_allPoints.png")
plt.show()

BinEdges = []
for ee in edges:
  BinEdges.append(ee)
for ee in use_was:
  BinEdges.append(ee)
BinEdges.append(0.)
#BinEdges.append(0.03)
print(BinEdges)
print(type(BinEdges))
BinEdges.sort()

len(BinEdges)

outfile = open("FinalAlphaBinEdges.txt","w")
for bb in BinEdges:
  outfile.write(str(bb)+",")
  print(bb)

