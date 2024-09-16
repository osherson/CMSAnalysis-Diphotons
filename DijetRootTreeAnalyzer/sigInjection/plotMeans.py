import ROOT
from ROOT import *
import numpy as np
import array
import sys,os

gROOT.SetBatch()

gen_alphas = [0.005, 0.01, 0.015, 0.02, 0.025]
xs = "1"

#outdir = "fb_{}_biasOutput".format(xs)
#outdir = "combineOutputEnvelope".format(xs)
outdir = "newSetParams".format(xs)

#mlist = {"dijet":[], "atlas":[], "dipho":[], "moddijet":[], "myexp":[]}
funcNames = {0:"Dijet", 1:"Atlas", 2:"ModDijet", 3:"Diphoton", 4:"Power"}
#funcName = {0:"Dijet"}

mStyles = [20,21,22,33,34]
mColors = [2,4,6,8,9]

def checkPass(x, a, f, s):
  phimass = str(a*x).replace(".","p")
  if(phimass.endswith("p0")): phimass = phimass[:-2]
  xmass = str(x)
  outfile = "fb_{}_biasOutput/X{}A{}/{}_alphaAll_X{}A{}_pdf{}.root".format(xs, xmass, phimass, s, xmass, phimass, f)
  if(os.path.exists(outfile)==False): 
    print("{} does not exist".format(outfile))
    return -999,0,0,

  of = ROOT.TFile(outfile, "READ")
  kn = of.GetListOfKeys().At(0).GetName()
  canv = of.Get(kn)
  hist = canv.GetPrimitive("Bias Test, injected r={}".format(s))
  nEntry = int(hist.GetEntries())
  Mean = float(hist.GetMean())
  Rms = float(hist.GetRMS())

  return nEntry,Mean,Rms

#for sig in ["null", "exp", "sig2"]:
#for sig in ["null"]:
for sig in ["exp"]:
  #mlist = {0:[], 1:[], 2:[], 3:[], 4:[]}
  mlist = {0.005:[], 0.01:[], 0.015:[], 0.02:[], 0.025:[] }
  
  for sigXA in os.listdir(outdir):
    if(sigXA[0] != "X"):continue
    thisX = int(sigXA[1 : sigXA.find("A")])
    thisPhi = float(sigXA[sigXA.find("A")+1 : ].replace("p","."))
    thisAlpha = round(thisPhi/thisX,3)
    if(thisAlpha == 0.03): continue

    for thisFunc in [0,1,2,3,4]:
    #for thisFunc in [0]:
      #outfile = "fb_{}_biasOutput/{}/{}_alphaAll_{}_pdf{}.root".format(xs, sigXA, sig, sigXA, thisFunc)
      #outfile = "combineOutputEnvelope/{}/{}_alphaAll_{}_pdf{}.root".format(sigXA, sig, sigXA, thisFunc)
      outfile = "{}/{}/{}_alphaAll_{}_pdf{}_nofit.root".format(outdir, sigXA, sig, sigXA, thisFunc)
      if(os.path.exists(outfile)==False): 
        print("{} does not exist").format(outfile)
        continue

      of = ROOT.TFile(outfile, "READ")
      kn = of.GetListOfKeys().At(0).GetName()
      canv = of.Get(kn)
      hist = canv.GetPrimitive("Bias Test, injected r={}".format(sig))
      nEntry = int(hist.GetEntries())
      hMean = float(hist.GetMean())
      hRms = float(hist.GetRMS())
      if(nEntry < 20):
        print("X {}, Alpha {}, Fit {} signal only has {} successful fits. Skipping.".format(thisX, thisAlpha, thisFunc, nEntry))
        continue
      mlist[thisAlpha].append((thisX, thisFunc, hMean, hRms))
  
  for alpha in mlist.keys():
  #for alpha in [0.005]:
    leg = ROOT.TLegend(0.68,0.62, 0.89, 0.89)
    leg.SetBorderSize(0)
    leg.SetHeader("Toy Gen. Function")
    MG = ROOT.TMultiGraph()
    amax = 0

    for (ii,func) in enumerate([0,1,2,3,4]):
      xarr = array.array("d")
      marr = array.array("d")
      earr = array.array("d")
      zarr = array.array("d")
      for (xx, ff, hm, hr) in mlist[alpha]:
        if(ff != func): continue
        xarr.append(xx+func*6)
        marr.append(hm)
        earr.append(hr)
        zarr.append(0.)
    
      if(len(marr)==0 or len(earr)==0):continue
      mxarray = [abs(xx) for xx in marr]
      exarray = [abs(xx) for xx in earr]
      nmax = np.amax(mxarray) + np.amax(exarray)
      if(nmax > amax): amax=nmax
      print(amax)
      gr = TGraphErrors(len(xarr), xarr, marr, zarr, earr)
      gr.SetMarkerStyle( mStyles[func] )
      #gr.SetMarkerSize(0.5)
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
    #MG.GetYaxis().SetRangeUser(-amax*1.02, amax*1.02)
    MG.GetYaxis().SetRangeUser(-2,2)
    #MG.GetYaxis().SetRangeUser(-4., 4.)
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
    if(not os.path.exists("./MeanPlots/Unblind/{}".format(sig))):
      os.system("mkdir -p MeanPlots/Unblind/{}".format(sig))
    c1.Print("MeanPlots/Unblind/{}/alpha{}_means.png".format(sig,alpha))
