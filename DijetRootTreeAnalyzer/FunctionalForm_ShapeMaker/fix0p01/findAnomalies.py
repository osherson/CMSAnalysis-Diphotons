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
oFile = ROOT.TFile("Plots/SmoothedHistsY/hists.root","recreate")
oFile.cd()

for pname in pnames:
  #if(pname != "a1"):continue

  hist = histfile.Get("hist_{}".format(pname))
  badlist = []
  paramlist = []

  zeroed = hist.Clone("zeroed_{}".format(pname))
  zmax = zeroed.GetMaximum()
  zeroed.GetZaxis().SetRangeUser(0,zmax)
  zeroed.SetTitle("{} Cloned".format(pname))
  zeroed.SetStats(0)
  smooth = hist.Clone("smooth_{}".format(pname))
  smooth.SetTitle("{} Cloned".format(pname))
  smooth.SetStats(0)
  smooth.GetZaxis().SetRangeUser(0,zmax)

  nxbins,nybins = hist.GetNbinsX(), hist.GetNbinsY()

  c2 = ROOT.TCanvas()
  c2.cd()
  zeroed.Draw("COLZ")
  c2.Print("tmpp.png")

  for ny in range(hist.GetNbinsY()+1):
    falpha = hist.GetYaxis().GetBinLowEdge(ny)+hist.GetYaxis().GetBinWidth(ny)
    #if(falpha != 0.011): continue
    #print(falpha)

    x1,x2 = hist.GetXaxis().GetBinLowEdge(0)+hist.GetXaxis().GetBinWidth(0), hist.GetXaxis().GetBinLowEdge(nxbins)+hist.GetXaxis().GetBinWidth(nxbins)
    firstbin,lastbin = hist.FindBin(x1,falpha), hist.FindBin(x2,falpha)
    z1,z2 = hist.GetBinContent(firstbin), hist.GetBinContent(lastbin)
    #print(x1, x2)
    #print(firstbin, lastbin, lastbin-firstbin)
    #print(z1, z2)

    slope = (z2-z1)/(x2-x1)
    intercept = z1-slope*x1
    linval = [slope*xx + intercept for xx in xlist]

    for (nx,bb) in enumerate(range(firstbin,lastbin)):
      thiscontent = hist.GetBinContent(bb)
      thisx = hist.GetXaxis().GetBinLowEdge(nx)+hist.GetXaxis().GetBinWidth(nx) 
      pdiff = abs(linval[nx] - thiscontent) / (thiscontent) * 100
      #print(linval[nx], thiscontent, pdiff)
      if(pdiff > 5 or (falpha==0.01 and pname != "mean")):
        zeroed.SetBinContent(bb,0)
        smooth.SetBinContent(bb,linval[nx])
        #paramdic[(thisx,falpha)] = linval[nx]
        badlist.append( (int(thisx),falpha) )
        paramlist.append( (int(thisx),falpha,linval[nx]) )
      if(math.isnan(thiscontent)):
        zeroed.SetBinContent(bb,0)
        smooth.SetBinContent(bb,linval[nx])
        badlist.append( (int(thisx),falpha) )
        paramlist.append( (int(thisx),falpha,linval[nx]) )
        #paramdic[(thisx,falpha)] = linval[nx]

  cc = ROOT.TCanvas()
  cc.cd()
  zeroed.SetTitle("{} After Loop".format(pname))
  zeroed.Draw("colz")
  cc.Print("Plots/ZeroHists/{}.png".format(pname))
  #zeroed.Write()

  cs = ROOT.TCanvas()
  cs.cd()
  smooth.SetTitle("{} Smoothed".format(pname))
  smooth.Draw("colz")
  cs.Print("Plots/SmoothedHists/{}.png".format(pname))

#############################################################

  zeroy = smooth.Clone("zeroy_{}".format(pname))
  zmax = zeroy.GetMaximum()
  zeroy.GetZaxis().SetRangeUser(0,zmax)
  zeroy.SetTitle("{} Cloned".format(pname))
  zeroy.SetStats(0)
  smoothY = smooth.Clone("smoothY_{}".format(pname))
  smoothY.SetTitle("{} Cloned".format(pname))
  smoothY.SetStats(0)
  smoothY.GetZaxis().SetRangeUser(0,zmax)

  nxbins,nybins = smooth.GetNbinsX(), smooth.GetNbinsY()

  c2 = ROOT.TCanvas()
  c2.cd()
  zeroy.Draw("COLZ")
  c2.Print("tmpp.png")

  for nx in range(hist.GetNbinsX()+1):
    fX = hist.GetXaxis().GetBinLowEdge(nx)+hist.GetXaxis().GetBinWidth(nx)
    #if(fX > 320): continue

    y1,y2 = smooth.GetYaxis().GetBinLowEdge(1)+smooth.GetYaxis().GetBinWidth(1), smooth.GetYaxis().GetBinLowEdge(nybins)+smooth.GetYaxis().GetBinWidth(nybins)
    firstbin,lastbin = smooth.FindBin(fX,y1), smooth.FindBin(fX,y2)
    z1,z2 = smooth.GetBinContent(firstbin), smooth.GetBinContent(lastbin)
    #print(x1, x2)
    #print(firstbin, lastbin, lastbin-firstbin)
    #print(z1, z2)

    slope = (z2-z1)/(y2-y1)
    intercept = z1-slope*y1
    linval = [slope*aa + intercept for aa in alphalist]

    #print("fX: {}".format(fX))

    for (na,thisalpha) in enumerate(alphalist):
      thisbin = smooth.FindBin(fX,thisalpha)
      thiscontent = smooth.GetBinContent(thisbin)
      pdiff = abs(linval[na] - thiscontent) / (thiscontent) * 100
      if(pdiff > 5 or (falpha==0.01 and pname != "mean")):
        zeroy.SetBinContent(thisbin,0)
        smoothY.SetBinContent(thisbin,linval[na])
        #paramdic[(fX,thisalpha)] = linval[na]
        if( (int(fX),thisalpha) not in badlist):
          badlist.append( (int(fX),thisalpha))
          paramlist.append( (int(fX),thisalpha,linval[na]) )
        else:
          print("Replacing {}".format((int(fX),thisalpha)))
          idx = badlist.index( (int(fX),thisalpha) )
          paramlist[idx] = (int(fX),thisalpha,linval[na])
      if(math.isnan(thiscontent)):
        zeroy.SetBinContent(thisbin,0)
        smoothY.SetBinContent(thisbin,linval[na])
        #paramdic[(fX,thisalpha)] = linval[na]
        if( (int(fX),thisalpha) not in badlist):
          badlist.append( (int(fX),thisalpha))
          paramlist.append( (int(fX),thisalpha,linval[na]) )
        else:
          print("Replacing {}".format((int(fX),thisalpha)))
          idx = badlist.index( (int(fX),thisalpha) )
          paramlist[idx] = (int(fX),thisalpha,linval[na])

  cc = ROOT.TCanvas()
  cc.cd()
  zeroy.SetTitle("{} After Loop".format(pname))
  zeroy.Draw("colz")
  cc.Print("Plots/ZeroHistsY/{}.png".format(pname))
  #zeroy.Write()

  cs = ROOT.TCanvas()
  cs.cd()
  smoothY.SetTitle("{} smoothed".format(pname))
  smoothY.Draw("colz")
  smoothY.Write()
  cs.Print("Plots/SmoothedHistsY/{}.png".format(pname))

  badfile = open("BadSignals/badsignals_{}.txt".format(pname),"w")
  for (xx,aa,pval) in paramlist:
        badfile.write("{},{}\n".format(int(xx),aa))
  badfile.close()

  paramfile = open("InterpoParamFiles/{}.txt".format(pname),"w")
  for xm in xlist:
    for aa in alphalist:
      thisbin = smoothY.FindBin(xm,aa)
      thiscontent = smoothY.GetBinContent(thisbin)
      paramfile.write("{},{},{}\n".format(int(xm),aa,thiscontent))
  paramfile.close()



