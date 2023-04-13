import numpy as np
import ROOT
import sys,os
from array import array

ROOT.gROOT.SetBatch()

dir_path = os.path.dirname(os.path.realpath(__file__))

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = round(phi/x,3)
  return x,phi,alpha

def MakeFolder(N):
   import os
   if not os.path.exists(N):
    os.makedirs(N)

int_dir = "../../inputs/Shapes_fromInterpo/unBinned"

shape = "alpha"

if("clean" in sys.argv):
  print("Deleting old plots")
  os.system("rm -rf Plots/alpha*")

xmin, xmax = 300, 3000
xstep = 10
xlist = [float(xx) for xx in range(xmin, xmax+xstep, xstep)]
alphamin, alphamax = 0.005, 0.025
alphastep = 0.001
alphalist = [round(aa,4) for aa in np.arange(alphamin, alphamax+alphastep, alphastep)]

pnames = ["a1","a2","n1","n2","mean","sigma", "N"]
#pnames = ["a1"]

oFile = ROOT.TFile("Plots/Widths/param_hists.root","recreate")
oFile.cd()

for (pnum,pname) in enumerate(pnames):
  #if(pname != "mean"):continue
  hist = ROOT.TH2F("hist_{}".format(pname),"{}; X Mass (GeV); #alpha", len(xlist)-1, np.array(xlist), len(alphalist)-1, np.array(alphalist))
  ccount = 0
  for xaa in os.listdir(int_dir):
    xm,phim,alpha = getXPhiAlpha(xaa)
    intpath = os.path.join(int_dir,xaa)

    fname = "../../inputs/Shapes_fromInterpo/unBinned/{}/params_alpha_i.txt".format(xaa)
    if(not os.path.exists(fname)):
      fname = "../../inputs/Shapes_fromInterpo/unBinned/{}/params_alpha.txt".format(xaa)
      if(not os.path.exists(fname)): 
        #print("bad", xaa)
        continue
    else: ccount += 1
    pfile = open(fname,"r")
    lin=pfile.readline()
    param = float(lin.split(",")[pnum])
    hist.Fill(xm,alpha,param)

  print("Corrected files: {}".format(ccount))
  hist.SetTitle(pname)
  hist.GetZaxis().SetRangeUser(0,hist.GetMaximum())
  hist.SetStats(0)
  hist.GetXaxis().SetTitle("X Mass (GeV)")
  hist.GetYaxis().SetTitle("#alpha")
  c1 = ROOT.TCanvas()
  c1.cd()
  hist.Draw("colz")
  c1.Print("Plots/Widths_afterCorrection/{}_hist2D.png".format(pname))
  hist.Write()

oFile.Close()
  
