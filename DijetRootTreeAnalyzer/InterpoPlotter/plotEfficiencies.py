#import ROOT
import numpy
import os
import math
import sys
import matplotlib.pyplot as plt

#ROOT.gROOT.SetBatch()

def MakeFolder(N):
    import os
    if not os.path.exists(N):
     os.makedirs(N)

def GetXPhiAlpha(ins):
  X = int(ins[ins.find("X")+1 : ins.find("A")])
  Phi = float(ins[ins.find("A")+1 : ].replace("p","."))
  Alpha = round(Phi/X,3)
  return X, Phi, Alpha

I_DIR = "../inputs/Shapes_fromInterpo/alphaBinning"
G_DIR = "../inputs/Shapes_fromGen/alphaBinning"

GEN_ALPHAS = [0.005, 0.01, 0.015, 0.02, 0.025]

#for alphaBin in range(0,9+1):
for alphaBin in ["ALL"]:
#for alphaBin in [1]:
  print("Beginning Alpha Bin {}".format(alphaBin))

  #if(alphaBin != 1): continue

  ialphaDir = "{}/{}".format(I_DIR,alphaBin)
  galphaDir = "{}/{}".format(G_DIR,alphaBin)
  
  for plot_alpha in GEN_ALPHAS:
    #if(plot_alpha != 0.005): continue
    print("Starting signal alpha = {}".format(plot_alpha))
    int_files, gen_files = [],[]
    ieffs,geffs = [],[]
    ixs, gxs = [],[]

    for ii,alphaDir in enumerate([ialphaDir, galphaDir]):
      for si in os.listdir(alphaDir):
        xx,pp,aa = GetXPhiAlpha(si)
        #if(xx < 297 or xx > 1600): continue
        if(aa == plot_alpha):
          xdir = os.path.join(alphaDir, si)
          signame = xdir.split("/")[-1]
          if(alphaBin=="ALL"):
            if(os.path.exists("{}/PLOTS_0.root".format(xdir))):
              if(ii==0):int_files.append(["int", xx, pp, aa, "{}/{}.txt".format(xdir,signame)])
              else:gen_files.append(["gen", xx, pp, aa, "{}/{}.txt".format(xdir,signame)])
          else:
            if(os.path.exists("{}/PLOTS_{}.root".format(xdir, alphaBin))):
              if(ii==0):int_files.append(["int", xx, pp, aa, "{}/{}.txt".format(xdir, signame)])
              else:gen_files.append(["gen", xx, pp, aa, "{}/{}.txt".format(xdir, signame)])

  
    allFiles = int_files + gen_files
    if(len(allFiles)==0):
      print("No files for alphaBin {} signal Alpha = {}".format(alphaBin, plot_alpha))
      #continue
    for src, xm, pm, alph, fil in allFiles:
      #print(src, xm, pm, alph, fil)
      f = open(fil, "r")
      thisEff = float(f.readline())
      f.close()
      if(src=="int"): 
        ixs.append(xm)
        ieffs.append(thisEff)
      elif(src=="gen"):
        geffs.append(thisEff)
        gxs.append(xm)

    plt.title(r"Signal Efficiencies, $\alpha$={}".format(plot_alpha),fontsize=16)
    plt.xlabel("X Mass (GeV)", fontsize=14)
    plt.ylabel("Efficiency", fontsize=14)
    plt.scatter(gxs, geffs,  color='red', label="Generated")
    plt.scatter(ixs, ieffs,  color='blue', label="Interpolated")
    plt.legend(loc='best')
    MakeFolder("Plots/alphaBin{}/".format(alphaBin))
    plt.savefig("Plots/alphaBin{}/alpha{}_eff.png".format(alphaBin,plot_alpha))
    #plt.show()
    plt.clf()

