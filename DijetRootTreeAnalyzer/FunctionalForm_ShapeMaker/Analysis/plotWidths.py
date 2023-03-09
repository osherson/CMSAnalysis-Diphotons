import numpy as np
import ROOT
import sys,os
from array import array

ROOT.gROOT.SetBatch()
ROOT.gRandom.SetSeed(0)

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

alphamin, alphamax = 0.005, 0.025
alphastep = 0.001
alphalist = [round(aa,4) for aa in np.arange(alphamin, alphamax+alphastep, alphastep)]
alphalist = [0.01]

pnames = ["a1","a2","n1","n2","mean","sigma", "N"]

for palpha in alphalist:
  print("Starting alpha {}".format(palpha))
  a1a, a2a, n1a, n2a, meana, siga, Na = array("d"),array("d"),array("d"),array("d"),array("d"),array("d"),array("d")
  xarr = array("d")
  MakeFolder("Plots/Widths/alpha{}".format(palpha))

  for xaa in os.listdir(int_dir):
    xm,phim,alpha = getXPhiAlpha(xaa)
    intpath = os.path.join(int_dir,xaa)
    if(alpha != palpha): continue

    fname = "../../inputs/Shapes_fromInterpo/unBinned/{}/params_alpha.txt".format(xaa)
    if(not os.path.exists(fname)): continue
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


  for (pname,ar) in zip(pnames,[a1a, a2a, n1a, n2a, meana, siga, Na]):
    tg = ROOT.TGraph(len(xarr),xarr,ar)
    tg.SetTitle(pname)
    cc = ROOT.TCanvas("","",650,650)
    cc.cd()
    tg.SetMarkerStyle(20)
    tg.Draw()
    cc.Print("Plots/Widths/alpha{}/{}.png".format(palpha,pname))


