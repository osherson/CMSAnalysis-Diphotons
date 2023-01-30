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

unb_dir = "../inputs/Shapes_fromGen/unBinned/"

hist = ROOT.TH2D("eff","Efficiency of Known Signals, No Alpha Slicing;X Mass;#alpha", nxs, xmin, xmax, nalphas, alphamin, alphamax) 

xs = {}
for xa in os.listdir(unb_dir):

  ff = open("{}{}/{}.txt".format(unb_dir,xa,xa), "r")
  xmass = int(xa[1:xa.find("A")])
  alpha = float(xa[xa.find("A")+1 : ].replace("p",".")) / xmass
  for lin in ff.readlines():
    eff = float(lin)
    hist.Fill(xmass, alpha, eff)
    xs[(xmass,alpha)]=eff
  ff.close()

 
c1 = TCanvas("c1", "c1", 800,600)
c1.cd()
hist.SetStats(0)
hist.SetTitle("Efficiency of Known Signals")
hist.SetTitleSize(0.05)
hist.GetYaxis().SetTitle("#alpha_{gen}")
hist.GetXaxis().SetTitle("M_{X,gen}")
hist.GetXaxis().SetTitleSize(0.04)
hist.GetYaxis().SetTitleSize(0.045)
hist.GetXaxis().SetTitleOffset(1.0)
hist.GetYaxis().SetTitleOffset(1.0)
hist.Draw("colz")
c1.Print("EffStuff/Plots/unbinned.png")
#exit()

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
c3.Print("EffStuff/Plots/Full_twod.png")

EffFile = open("./EffStuff/FULL.csv","w")
thist = tgr.GetHistogram()
allstuff = []
for xx in xlist:
  for aa in alphalist:
    if((xx,aa) in xs.keys()):
      allstuff.append((xx,aa,xs[(xx,aa)]))
      EffFile.write("{},{},{}\n".format(int(xx),aa,xs[(xx,aa)]))
    else:
      if(aa >= 0.005 and aa <= 0.03 and xx >= 300 and xx <= 3000):
        newE = thist.GetBinContent(thist.FindBin(xx,aa))
        #print(xx, aa, newE)
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
c2.Print("EffStuff/Plots/unbinned_full.png")
