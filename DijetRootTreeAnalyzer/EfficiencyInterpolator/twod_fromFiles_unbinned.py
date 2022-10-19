import numpy as np
import ROOT
from ROOT import *
from array import array
import os,sys

#gROOT.SetBatch()

gen_phis = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03]
want_alpha = 0.008

alphamin, alphamax = 0, 0.031
nalphas = int((alphamax - alphamin)//0.001 + 2)
alphalist = np.linspace(alphamin, alphamax, nalphas)

xmin, xmax = 200, 3010
nxs = int((xmax-xmin)//10 + 1)
xlist = np.linspace(xmin, xmax, nxs)

eff_dir = "./EfficiencyFiles/unBinned"

hist = ROOT.TH2D("eff","Efficiency of Known Signals, No Alpha Slicing;X Mass;#alpha", nxs, xmin, xmax, nalphas, alphamin, alphamax) 

xs = {}
for fil in os.listdir(eff_dir):

  falpha = fil.split("_")[0]
  falpha = float(falpha[5:falpha.rfind(".")])

  ff = open(os.path.join(eff_dir,fil), "r")
  for lin in ff.readlines():
    xmass = int(lin.split(",")[0])
    eff = float(lin.split(",")[1].rstrip())
    hist.Fill(xmass, falpha, eff)
    xs[(xmass,falpha)]=eff

c1 = TCanvas("c1", "c1", 600,600)
c1.cd()
hist.SetStats(0)
hist.Draw("colz")
c1.Print("EffPlots/TwoD/unbinned.png")

xl = array("d")
al = array("d")
el = array("d")

for ( (xx,aa),e) in xs.items():
  xl.append(xx)
  al.append(aa)
  el.append(e)


c3 = TCanvas("c3","c3", 600,600)
c3.cd()
tgr = TGraph2D(len(xl), xl,al,el)
tgr.SetNpx(nxs)
tgr.SetNpy(nalphas)
#tgr.GetYaxis().SetRangeUser(0,0.03)
tgr.SetTitle("TGraph Efficiency of known and Interp signals")
tgr.GetXaxis().SetTitle("X Mass")
tgr.GetYaxis().SetTitle("#alpha")
tgr.Draw("colz")
#tgr.Draw("P")
c3.Print("EffPlots/tg.png")

EffFile = open("EfficiencyFiles/FULL.csv","w")
thist = tgr.GetHistogram()
allstuff = []
for xx in xlist:
  for aa in alphalist:
    if((xx,aa) in xs.keys()):
      allstuff.append((xx,aa,xs[(xx,aa)]))
      EffFile.write("{},{},{}\n".format(int(xx),aa,xs[(xx,aa)]))
    else:
      if(aa > 0.005 and aa < 0.03 and xx > 300 and xx < 3000):
        newE = thist.GetBinContent(thist.FindBin(xx,aa))
        print(xx, aa, newE)
        allstuff.append((xx,aa,newE))
        EffFile.write("{},{},{}\n".format(int(xx),aa,newE))
EffFile.close()

fhist = ROOT.TH2D("feff","Efficiency of Known and Interp Signals, No Alpha Slicing;X Mass;#alpha", nxs, xmin, xmax, nalphas, alphamin, alphamax) 
ct = 0
for(xx,aa,ee) in allstuff:
  #if(ct > 10): break
  ct += 1
  fhist.Fill(xx,aa,ee)

c2 = TCanvas("c2", "c2", 600,600)
c2.cd()
fhist.SetStats(0)
fhist.Draw("colz")
c2.Print("EffPlots/TwoD/unbinned_full.png")
