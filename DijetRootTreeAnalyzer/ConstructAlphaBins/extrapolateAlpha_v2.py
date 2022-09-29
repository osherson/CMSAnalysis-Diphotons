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

edges = [round(e,5) for e in edges]

gaps = []
for ii in range(len(edges)-1):
  if(ii!= 0 and (ii+1) % 3 ==0): continue
  gap = round(edges[ii+1] - edges[ii],5)
  if(gap in gaps): continue
  else:
    gaps.append(gap)

colors = ["red","blue","green","purple","orange"]


plt.figure(figsize=(6,6))
line = np.polyfit(edges, edges,deg=2)
ppt = np.polyval(line, edges)
plt.plot(edges, ppt, color='gray', label="Fit",linewidth=1)

#plt.scatter(edges,edges, color='black', label="GenEdges",s=25)
for ii in range(0,len(edges)-3,3):
  plt.scatter(edges[ii : ii+3],edges[ii : ii+3], color=colors[ii//3], label="GenEdges",s=75, marker="*")
#
#plt.legend(loc='best')
plt.xlabel("alpha",fontsize=14)
plt.ylabel("alpha",fontsize=14)
plt.savefig("Plots/alphaBins_genPoints.png")
plt.show()


c1 = edges[0:3]
while c1[-1] < (edges[3]-gaps[0]):
  c1.append(c1[-1] + gaps[0])
c2 = edges[3:6]
while c2[-1] < (edges[6]-gaps[1]):
  c2.append(c2[-1] + gaps[1])
c3 = edges[6:9]
while c3[-1] < (edges[9]-gaps[2]):
  c3.append(c3[-1] + gaps[2])
c4 = edges[9:12]
while c4[-1] < (edges[12]-gaps[3]):
  c4.append(c4[-1] + gaps[3])
c5 = edges[12:15]
while c5[-1] < (edges[15]-gaps[4]):
  c5.append(c5[-1] + gaps[4])

#while c4[-1] < edges[13]-gaps[3]:
#  c4.append(c4[-1] + gaps[3])
#c5 = edges[13:15]
#while c5[-1] < edges[15]-gaps[4]:
#  c5.append(c5[-1] + gaps[4])

newbins = []
for cl in [c1,c2,c3,c4,c5]:
  for cc in cl:
    newbins.append(round(cc,5))

minGap = (newbins[1] - newbins[0] )*0.85
fbins = [newbins[0]]
badi=-999
for ii in range(1,len(newbins)-1):
  if(ii==badi):continue
  if(newbins[ii+1] - newbins[ii] < minGap):
    avg = (newbins[ii+1] + newbins[ii])/2
    print(newbins[ii+1], newbins[ii])
    fbins.append(avg)
    badi = ii + 1
  else: fbins.append(newbins[ii])

print(len(newbins))
print(len(fbins))

print("Done correcting")

fbins.append(0.03)
use_was = fbins

plt.clf()
plt.figure(figsize=(6,6))
plt.plot(edges, ppt, color='gray', label="Fit",linewidth=1)
plt.scatter(edges,edges, color='blue', label='Gen Mean +/- RMS points',s=75, marker="*")
plt.scatter(use_was, use_was, color='orange', label="AlphaBin Edges",s=20)

plt.xlabel("alpha", fontsize=14)
plt.ylabel("alpha", fontsize=14)

plt.legend(loc="best",fontsize=14)
plt.savefig("Plots/alphaBins_allPoints.png")
plt.show()


BinEdges = []
for ee in use_was:
  BinEdges.append(ee)
BinEdges.append(0.)
#BinEdges.append(0.03)
#print(BinEdges)
#print(type(BinEdges))
BinEdges.sort()

len(BinEdges)

outfile = open("FinalAlphaBinEdges.txt","w")
for bb in BinEdges:
  outfile.write(str(bb)+",")
  print(bb)

