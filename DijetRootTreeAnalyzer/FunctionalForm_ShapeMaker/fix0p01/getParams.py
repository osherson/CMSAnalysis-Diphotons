import numpy as np
import ROOT
import sys,os

ROOT.gROOT.SetBatch()

xmin, xmax = 300, 3000
xstep = 10
xlist = [float(xx) for xx in range(xmin, xmax+xstep, xstep)]
alphamin, alphamax = 0.005, 0.025
alphastep = 0.001
alphalist = [round(aa,4) for aa in np.arange(alphamin, alphamax+alphastep, alphastep)]


pnames = ["a1","a2","n1","n2","mean","sigma", "N"]
hFile = ROOT.TFile("Plots/ZeroHists/hists.root","read")

badsigs = []
inF = open('BadSignals/allbad.txt')
for lin in inF.readlines():
   xx,aa = int(lin.split(",")[0]), float(lin.split(",")[1][:-1])
   badsigs.append((xx,aa))

for pname in pnames:
  #if(pname != "a1"): continue

  hist = hFile.Get("zeroed_{}".format(pname))

  #cc = ROOT.TCanvas()
  #cc.cd()
  #hist.Draw("colz")
  #cc.Print("tmp.png")

  tg = ROOT.TGraph2D(hist)
  c1 = ROOT.TCanvas()
  c1.cd()
  tg.Draw("colz")
  c1.Print("Plots/SmoothedHists/{}.png".format(pname))

  ParamFile = open("InterpoParamFiles/{}.txt".format(pname),"w")
  thist = tg.GetHistogram()

  c2 = ROOT.TCanvas()
  c2.cd()
  thist.Draw("colz")
  c2.Print("Plots/SmoothedHists/Hists/{}.png".format(pname))

  nbx = tg.GetXaxis().GetNbins()
  nby = tg.GetYaxis().GetNbins()
  miny=tg.GetYaxis().GetBinLowEdge(0)
  maxy=tg.GetYaxis().GetBinLowEdge(nby)+tg.GetYaxis().GetBinWidth(nby)

  print("Min Y: {}, Max Y: {}".format(miny,maxy))

  for (xx,aa) in badsigs:
    nbin=thist.FindBin(xx,aa)
    by = thist.GetYaxis().FindBin(aa)
    bx = thist.GetXaxis().FindBin(xx)

    by = max(by,1)
    by = min(by,nby-1)
    bx = max(bx,1)
    bx = min(bx,nby-1)
    newval = thist.GetBinContent(bx+1,by+1)
    if(newval==0.0):
      print(xx,aa)
      print("Bin Y: {}, Left Edge: {}".format(by, thist.GetYaxis().GetBinLowEdge(by)))
      print("Bin X: {}, Left Edge: {}".format(bx, thist.GetXaxis().GetBinLowEdge(bx)))
    ParamFile.write("{},{},{}\n".format(int(xx),aa,newval))
    #print("{},{},{}\n".format(int(xx),aa,newval))
  ParamFile.close()

  
 
