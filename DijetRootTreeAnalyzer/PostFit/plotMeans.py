import ROOT
from ROOT import *
import numpy as np
import array
import sys,os

gROOT.SetBatch()

gen_alphas = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03]
xs = "1"
useFit=False
outfile = "fb_{}_biasOutput/BiasMeans.csv".format(xs)

#mlist = {"dijet":[], "atlas":[], "dipho":[], "moddijet":[], "myexp":[]}
funcNames = {0:"Dijet", 1:"Atlas", 2:"ModDijet", 3:"Diphoton", 4:"Power"}

mStyles = [20,21,22,33,34]
mColors = [2,4,6,8,9]

def checkPass(x, a, f, s):
  phimass = str(a*x).replace(".","p")
  if(phimass.endswith("p0")): phimass = phimass[:-2]
  xmass = str(x)
  outfile = "fb_{}_biasOutput/X{}A{}/{}_alphaAll_X{}A{}_pdf{}.root".format(xs, xmass, phimass, s, xmass, phimass, f)
  of = ROOT.TFile(outfile, "READ")
  kn = of.GetListOfKeys().At(0).GetName()
  canv = of.Get(kn)
  hist = canv.GetPrimitive("Bias Test, injected r={}".format(s))
  nEntry = int(hist.GetEntries())
  Mean = float(hist.GetMean())
  Rms = float(hist.GetRMS())

  return nEntry,Mean,Rms

for sig in ["null", "exp", "sig2"]:
#for sig in ["null"]:
  #mlist = {0:[], 1:[], 2:[], 3:[], 4:[]}
  mlist = {0.005:[], 0.01:[], 0.015:[], 0.02:[], 0.025:[], 0.03:[]}
  bfile = open(outfile, "r")
  for lin in bfile.readlines():
    if(lin.startswith("X")): continue

    lin = lin.rstrip()
    sl =lin.split(",")
    thisX = int(sl[0])
    thisAlpha = float(sl[1])
    thisSig = sl[2]
    thisFunc = int(sl[3])
    thisFitMean = float(sl[4])
    thisFitRms = float(sl[5])
    
    if(thisSig == sig):
      npass,hMean,hRms = checkPass(thisX, thisAlpha, thisFunc, sig)
      if(thisFitMean > 1 or hMean > 1): 
        if(npass < 400):
           print("X {}, Alpha {}, Fit {} signal only has {} successful fits. Skipping.".format(thisX, thisAlpha, thisFunc, npass))
           continue
      mlist[thisAlpha].append((thisX, thisFunc, thisFitMean, thisFitRms, hMean, hRms))
  
  bfile.close()
  for alpha in mlist.keys():
  #for alpha in [0.005]:
    leg = ROOT.TLegend(0.62,0.62, 0.89, 0.89)
    leg.SetBorderSize(0)
    leg.SetHeader("Toy Gen. Function")
    MG = ROOT.TMultiGraph()
    amax = 0

    for (ii,func) in enumerate([0,1,2,3,4]):
      xarr = array.array("d")
      marr = array.array("d")
      earr = array.array("d")
      zarr = array.array("d")
      for (xx, ff, mm, rr, hm, hr) in mlist[alpha]:
        if(ff != func): continue
        xarr.append(xx+func*6)
        if(useFit==True):
          marr.append(mm)
          earr.append(rr)
        else:
          marr.append(hm)
          earr.append(hr)
        zarr.append(0.)
    
      nmax = np.amax(marr) + np.amax(earr)
      if(nmax > amax): amax=nmax
      gr = TGraphErrors(len(xarr), xarr, marr, zarr, earr)
      gr.SetMarkerStyle( mStyles[func] )
      gr.SetMarkerColor( mColors[func] )
      gr.SetLineColor( mColors[func] )
      #gr.GetXaxis().SetRangeUser(0., 3100.)
      leg.AddEntry(gr, "{}".format(funcNames[func]))

      MG.Add(gr)

    c1 = ROOT.TCanvas()
    c1.cd()
    if(sig=="null"):
      MG.SetTitle( "Bias Test Means, Signal Gen #alpha={}".format(alpha))
    elif (sig=="exp"):
      MG.SetTitle( "Injection Test Means, r=expected, Signal Gen #alpha={}".format(alpha))
    elif (sig=="sig2"):
      MG.SetTitle( "Injection Test Means, r=2#sigma, Signal Gen #alpha={}".format(alpha))
    MG.GetXaxis().SetTitle( "X Mass (GeV)" )
    MG.GetYaxis().SetTitle( 'Mean Bias' )
    MG.GetXaxis().SetRangeUser(0.,3100.)
    MG.GetYaxis().SetRangeUser(-amax*1.02, amax*1.02)
    ax = MG.GetXaxis()
    ax.SetLimits(0.,3100.)
    MG.Draw("AP")
    ll = TLine(MG.GetXaxis().GetXmin(), -0.5, MG.GetXaxis().GetXmax(), -0.5)
    lh = TLine(MG.GetXaxis().GetXmin(), 0.5, MG.GetXaxis().GetXmax(), 0.5)
    #ll = TLine(0., -0.05, gr.GetXaxis().GetXmax(), -0.05)
    #lh = TLine(0., 0.05, gr.GetXaxis().GetXmax(), 0.05)

    for lin in [ll, lh]:
      lin.SetLineColor(12)
      lin.SetLineStyle(kDashed)
      lin.Draw("same")

    leg.Draw("SAME")
    if(not os.path.exists("./MeanPlots/fb_{}/{}".format(xs,sig))):
      os.system("mkdir -p MeanPlots/fb_{}/{}".format(xs,sig))
    c1.Print("MeanPlots/fb_{}/{}/alpha{}_means.png".format(xs,sig,alpha))
