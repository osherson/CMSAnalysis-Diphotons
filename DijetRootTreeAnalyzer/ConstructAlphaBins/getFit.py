import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time
from array import array

RDF = ROOT.RDataFrame.RDataFrame

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../../.")
import PlottingPayload as PL
#gROOT.SetBatch()

year = 2018

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"
const_alpha = False #Use this to get signals at one alpha val

################################################

#Analysis Cuts
# masym, eta, dipho, iso
CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [0.25, 3.5, 0.9, 0.8] #Analysis Cuts

def GetSignalWidth(hist, inalpha):
  
  cbin = hist.FindBin(inalpha)

  bc = hist.GetBinContent(cbin)
  bcd = hist.GetBinContent(cbin-1)
  bcu = hist.GetBinContent(cbin+1)

  diff1 = bc - bcd
  diff2 = bc - bcu

  tdiff = diff1 + diff2

  return (tdiff, (bcd, bc, bcu), (hist.GetBinLowEdge(cbin-1), hist.GetBinLowEdge(cbin), hist.GetBinLowEdge(cbin+1)))


#################################################
SignalsGenerated = {}
#SignalsGenerated["X300A1p5"] = ["/cms/xaastorage-2/DiPhotonsTrees/X300A1p5_{}.root".format(year)]

#SignalsGenerated = {0.005:[], 0.01:[], 0.015:[], 0.02:[], 0.025:[]}

#Get all signals
for ff in os.listdir(xaastorage):
  #if(ff[0]=="X" and str(year) in ff and "X200A" not in ff):
  if(ff[0]=="X" and "X200A" not in ff): #All years together
    thisxa = ff[ : ff.find("_")]
    this_x = int(thisxa[1:thisxa.find("A")])
    this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
    if(this_phi / this_x > 0.026): continue
    if(const_alpha and this_phi / this_x != this_alpha): continue
    #SignalsGenerated[thisxa] = [os.path.join(xaastorage, ff)]
    if(thisxa in SignalsGenerated.keys()):
      SignalsGenerated[thisxa].append(os.path.join(xaastorage,ff))
    else:
      SignalsGenerated[thisxa] = [os.path.join(xaastorage,ff)]

ct = 0

galphas = [0.005, 0.01, 0.015, 0.02, 0.025]
#galphas = [0.005]
#galphas = galphas[0:2]

useAlphaBins = []

pts = {}
for galpha in galphas:
  mybins = []
  print("DOING ALPHA = {}".format(galpha))

  min_rms = 999
  use_mean = 0
  use_rms = 0
  from_x = 0
  for sig,flist in SignalsGenerated.items():
    this_x = int(sig[1:sig.find("A")])
    this_phi = float(sig[sig.find("A")+1:].replace("p","."))
    if(this_phi / this_x != galpha): continue
    print(sig)

    masym, deta, dipho, iso = CUTS[0], CUTS[1], CUTS[2], CUTS[3]
    trigger = "HLT_DoublePhoton"

    Chain = ROOT.TChain("pico_nom")
    #for f in SignalsGenerated[s]:
    for f in flist:
      Chain.Add(f)
    Rdf = RDF(Chain)
    Rdf = Rdf.Filter(trigger+" > 0.")
    Rdf = Rdf.Filter("clu1_pt > 90. && clu2_pt > 90. && masym < " + str(masym) + " && deta <     " + str(deta) + " && clu1_dipho > " + str(dipho) + " && clu2_dipho > " + str(dipho) + " && clu1_iso > " + str(iso) + " && clu2_iso > " + str(iso))

    alphahist = Rdf.Histo1D(("alphafine","alphafine",1000,0,0.03),"alpha")
    mean = alphahist.GetMean()
    rms = alphahist.GetRMS()

    ah = alphahist.GetValue().Clone()

    fit = TF1("fit","gaus(0)");


    ww = 2
    fitmin, fitmax = mean-ww*rms, mean+ww*rms
    ah.Fit(fit, "N","",fitmin, fitmax)

    gmean = fit.GetParameter("Mean")
    gsig = fit.GetParameter("Sigma")

    if("show" in sys.argv):
      c1 = TCanvas()
      c1.cd()
      ah.Draw("hist")
      fit.Draw("same")
      c1.Print("tmp.png")

#    if(rms < min_rms):
#      min_rms = rms
#      use_mean = mean
#      from_x = this_x

    if(gsig < min_rms):
      min_rms = gsig
      use_mean = mean
      from_x = this_x

  pts[galpha] = (use_mean,min_rms)

  print(from_x, use_mean, min_rms)

  useAlphaBins.append(use_mean-2*min_rms)
  useAlphaBins.append(use_mean)
  useAlphaBins.append(use_mean+2*min_rms)

print("Start Loop")

#useAlphaBins.sort()
print(useAlphaBins)

p_alphas = [aa for aa in pts.keys()]
p_means = [mm for (aa,(mm,rr)) in zip(p_alphas,pts.values())]
p_cmeans = [aa-mm for (aa,(mm,rr)) in zip(p_alphas,pts.values())]
p_widths = [rr for (mm,rr) in pts.values()]
p_zs = [0 for (mm,rr) in pts.values()]

print(p_means)
print(p_widths)

plt = ROOT.TGraphErrors(len(p_alphas),array('d', p_alphas), array('d',p_cmeans), array('d',p_zs), array('d',p_widths))
plt.GetXaxis().SetTitle("Gen Alpha")
plt.GetYaxis().SetTitle("Gen Alpha - Mean Alpha #pm RMS")
#plt.GetYaxis().SetTitleOffset(0.3)
plt.SetTitle("#alpha shape widths")
plt.SetMarkerColor(4)
plt.SetMarkerStyle(21)

c1 = ROOT.TCanvas()
c1.cd()
plt.Draw("AP")
c1.Print("errorPlot.png")

outfile = open("alphaBinEdges.txt","w")
for aa in useAlphaBins:
  outfile.write(str(aa)+"\n")

