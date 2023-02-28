import numpy as np
import ROOT
import sys,os
from array import array
import math

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

xmin, xmax = 300, 3000
xstep = 10
xlist = [float(xx) for xx in range(xmin, xmax+xstep, xstep)]
alphamin, alphamax = 0.005, 0.025
alphastep = 0.001
alphalist = [round(aa,4) for aa in np.arange(alphamin, alphamax+alphastep, alphastep)]

pnames = ["a1","a2","n1","n2","mean","sigma", "N"]

allparams = {}

histfile = ROOT.TFile("Plots/Widths/param_hists.root","read")
oFile = ROOT.TFile("Plots/ZeroHists/hists.root","recreate")
oFile.cd()


for pname in pnames:
  #if(pname != "n1"):continue
  hist = histfile.Get("hist_{}".format(pname))
  badfile = open("BadSignals/badsignals_{}.txt".format(pname),"w")
  #c = ROOT.TCanvas()
  #c.cd()
  #hist.Draw("colz")
  #c.Print("tmp.png")

  print("Hist X bins: {}".format(hist.GetNbinsX()))
  print("Hist Y bins: {}".format(hist.GetNbinsY()))

  zeroed = ROOT.TH2F("zeroed_{}".format(pname),"{}; X Mass (GeV); #alpha".format(pname), len(xlist)-1, np.array(xlist), len(alphalist)-1, np.array(alphalist))
  for ny in range(hist.GetNbinsY()+1):
    #if(ny < 10): continue
    falpha = hist.GetYaxis().GetBinLowEdge(ny)+hist.GetYaxis().GetBinWidth(ny)
    #if(falpha != 0.011): continue
    prof = hist.ProfileX(hist.GetName()+"_pfx",ny,ny+1)
    #print("Profile N Bins: {}".format(prof.GetNbinsX()))

    for bb in range(prof.GetNbinsX()):
      if(math.isnan(prof.GetBinContent(bb))):
        print("Nan in bin {}".format(bb))
        prof.SetBinEntries(bb,1)
        prof.SetBinContent(bb,0.)

    #cc = ROOT.TCanvas()
    #cc.cd()
    #hist.Draw("colz")

    x1,y1,x2,y2=prof.GetBinCenter(2),prof.GetBinContent(2),prof.GetBinCenter(prof.GetNbinsX()),prof.GetBinContent(prof.GetNbinsX())
    #if(abs(y1-mn)/mn > std): print("Bad at {}".format(hist.GetYaxis().GetBinLowEdge(ny)))

    slope = (y2-y1)/(x2-x1)
    intercept = y1-slope*x1
    linval = [slope*xx + intercept for xx in xlist]

    lin2 = ROOT.TLine(xlist[1],linval[1],xlist[-1],linval[-1])
    lin2.SetLineColor(ROOT.kRed)
    lin2.SetLineWidth(2)
    lin2.SetLineStyle(ROOT.kDashed)

    #cp = ROOT.TCanvas()
    #prof.SetStats(0)
    #prof.Draw("hist")
    #lin2.Draw("same")
    #cp.Print("Plots/{}/Profiles/prof_{}.png".format(pname,falpha))

    for bb in range(prof.GetNbinsX()):
      bc = prof.GetBinContent(bb)
      hbc = hist.GetBinContent(bb,ny)
      xc = prof.GetBinLowEdge(bb)
      if(xc < 300): continue
      dlin,ulin = min(linval),max(linval)
      minl,maxl = min(dlin,ulin), max(dlin,ulin)
      #zeroed.SetBinContent(bb,ny,hbc)
      if(bc < minl or bc > maxl):
        #print("Anamoly: {}, {}".format(xc,bc))
        badfile.write("{},{}\n".format(int(xc),falpha))
        zeroed.SetBinContent(bb,ny,0)
      else: zeroed.SetBinContent(bb,ny,hbc)

  cc = ROOT.TCanvas()
  cc.cd()
  zeroed.Draw("colz")
  cc.Print("Plots/ZeroHists/{}.png".format(pname))
  zeroed.Write()















