import numpy as np
import ROOT
import sys,os
from array import array

#ROOT.gROOT.SetBatch()

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

allparams = {}

for palpha in alphalist:
  #if(palpha > 0.006):continue
  print("Starting alpha {}".format(palpha))
  a1a, a2a, n1a, n2a, meana, siga, Na = array("d"),array("d"),array("d"),array("d"),array("d"),array("d"),array("d")
  xarr = array("d")

  for xaa in os.listdir(int_dir):
    xm,phim,alpha = getXPhiAlpha(xaa)
    intpath = os.path.join(int_dir,xaa)
    #if(xaa != "X600A3"): continue
    if(alpha != palpha): continue

    fname = "../../inputs/Shapes_fromInterpo/unBinned/{}/params_alpha.txt".format(xaa)
    if(not os.path.exists(fname)): 
      print("bad")
      continue
    pfile = open(fname,"r")
    lin=pfile.readline()
    a1a.append(float(lin.split(",")[0]))
    a2a.append(float(lin.split(",")[1]))
    n1a.append(float(lin.split(",")[2]))
    n2a.append(float(lin.split(",")[3]))
    meana.append(float(lin.split(",")[4]))
    siga.append(float(lin.split(",")[5]))
    Na.append(float(lin.split(",")[6]))

    xarr.append(xm)

  allparams[palpha] = [xarr, a1a, a2a, n1a, n2a, meana, siga, Na]

for pp in range(len(pnames)):
  pname = pnames[pp]
  hist = ROOT.TH2F("hist_{}".format(pname),"{}; X Mass (GeV); #alpha", len(xlist)-1, np.array(xlist), len(alphalist)-1, np.array(alphalist))
  #hist = ROOT.TH2F("hist_{}".format(pname),"{}; X Mass (GeV); #alpha", 100, 0, 2000, 100, 0, 0.03)
  for ka in allparams.keys():
    for vv in range(len(allparams[ka][0])):
      hist.Fill(allparams[ka][0][vv], ka, allparams[ka][pp+1][vv])

  hist.SetTitle(pname)
  hist.GetXaxis().SetTitle("X Mass (GeV)")
  hist.GetYaxis().SetTitle("#alpha")
  cc = ROOT.TCanvas()
  cc.cd()
  hist.Draw("colz")
  cc.Print("Plots/Widths/{}_2D.png".format(pname))
