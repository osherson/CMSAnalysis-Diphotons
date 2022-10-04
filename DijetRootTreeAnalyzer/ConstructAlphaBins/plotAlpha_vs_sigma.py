import numpy as np
import matplotlib.pyplot as plt

fil = open("alphaSigma.txt","r")

asig = {}
alphas, sigmas, errs = [],[],[]

for ll in fil.readlines():
  a,s,smax = ll.split(",")
  a = float(a)
  s = 2*float(s)
  serr = 2*float(smax[:-1])
  alphas.append(a)
  sigmas.append(s)
  errs.append(serr)

#plt.figure(figsize=(6,6))
falphas = np.linspace(0, 0.031, 32) 
line = np.polyfit(alphas, sigmas, deg=1)
ppt = np.polyval(line, falphas)
plt.plot(falphas, ppt, color='gray', label="Fit",linewidth=1)

#plt.scatter(asig.keys(),asig.values())
plt.errorbar(alphas, sigmas, yerr=errs,fmt='o')
plt.title(r"$2 \sigma$ vs. $\alpha$",fontsize=18)
plt.xlabel(r"$\alpha$", fontsize=16)
plt.ylabel(r"$2 \sigma$", fontsize=16)
plt.ylim(0,max(sigmas)*1.15)
plt.xlim(0,0.031)
plt.savefig("sigma_vs_alpha.png")
plt.show()

start = 0.003
tv = start
bin_edges = [start]
tw = np.polyval(line,start)

prec=5

while(tv < (0.03-tw)):
  tw = round(np.polyval(line, tv+tw/2),prec)
  tv = round(tv + tw, prec)
  bin_edges.append(tv)

bin_edges = bin_edges[:-1]
bin_edges.append(0.03)
ones = np.ones(len(bin_edges))

print(bin_edges)
print("N Alpha Bins: {}".format(len(bin_edges)))

plt.figure(figsize=(10,5))
plt.scatter(bin_edges, ones, marker="|",s=500)
plt.plot([0., 1],[1,1], color='gray', linewidth=1)
plt.title(r"$\alpha$ Bin Edges", fontsize = 18)
plt.xlabel(r"$\alpha$", fontsize = 16)
plt.xlim(0,0.0302)
plt.yticks([])
plt.savefig("binedges.png")
plt.show()

outfile = open("FinalAlphaBinEdges.txt","w")
for bb in bin_edges:
  outfile.write(str(bb)+",")
outfile.close()
