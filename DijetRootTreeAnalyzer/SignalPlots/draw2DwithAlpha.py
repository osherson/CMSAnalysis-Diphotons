import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time

RDF = ROOT.RDataFrame.RDataFrame

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../../.")
import PlottingPayload as PL
gROOT.SetBatch()

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"

def lookup(N):
  ysum = 0
  for year in [2016, 2017, 2018]:
    LH = []
    f = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/Diphoton-Treemaker/HelperFiles/Signal_NEvents_{}.csv".format(year)
    r = open(f)
    for i in r.readlines():
      #print i
      LH.append(i.split(','))

    X = N.split('A')[0].split('X')[1]
    A = N.split('A')[1].replace('p', '.')
    for r in LH:
      if r[0] == X and r[1] == A: 
        print(year, r[2].rstrip())
        ysum += int(r[2].rstrip())
  print("Total Events: {}".format(ysum))
  return ysum

#Analysis Cuts
# masym, eta, dipho, iso
#CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [1.0, 3.5, 0.9, 0.8] #Loose
#CUTS = [0.25, 1.5, 0.9, 0.8] #Analysis Cuts
CUTS = [0.25, 1.5, 0.9, 0.1] #Loose Analysis Cuts

#################################################

XB = [250.0, 255.0, 261.0, 267.0, 273.0, 279.0, 285.0, 291.0, 297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0, 2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0]

#AlphaBins = [0.0, 0.00428, 0.00467, 0.00506, 0.00568, 0.00637, 0.00706, 0.00775, 0.00844, 0.00935, 0.00974, 0.01012, 0.01120, 0.01189, 0.01285, 0.0139285714286, 0.015, 0.01603, 0.01672, 0.01741, 0.01810, 0.01897, 0.01959, 0.02020, 0.02086, 0.02155, 0.02224, 0.02322, 0.02419, 0.02516, 0.03]

AlphaBins = [0.0,0.0046,0.0049,0.0051,0.0054,0.0057,0.006,0.0063,0.0066,0.0069,0.0072,0.0075,0.0078,0.0081,0.0084,0.0087,0.009,0.0094,0.0098,0.0101,0.0106,0.0111,0.0116,0.0121,0.0126,0.0131,0.014,0.0145,0.015,0.0155,0.016,0.0165,0.017,0.0175,0.018,0.0185,0.0192,0.0197,0.0202,0.0209,0.0216,0.0223,0.023,0.0237,0.0244,0.0251,0.0258,0.0265,0.0272,0.0279,0.0286,0.0293,0.03]
#AlphaBins = [0.,0.03]
#AlphaBins = [0.00506,0.00568]


SignalsGenerated = {}
for ff in os.listdir(xaastorage):
  if(ff[0]=="X"):
    thisxa = ff[ : ff.find("_")]
    this_x = int(thisxa[1:thisxa.find("A")])
    this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
    if(this_phi / this_x > 0.026 or this_x < 300): continue
    if(thisxa in SignalsGenerated.keys()):
      SignalsGenerated[thisxa].append(os.path.join(xaastorage, ff))
    else: 
      SignalsGenerated[thisxa] = [os.path.join(xaastorage, ff)]

for sig, flist in SignalsGenerated.items():
  print(sig)
  #if(sig != "X600A3"): continue

  Chain = ROOT.TChain("pico_nom")
  for f in flist:
      Chain.Add(f)
  Rdf = RDF(Chain)
  print("Initial values", Rdf.Count().GetValue())
  # Make cuts:
  Rdf = Rdf.Filter("HLT_DoublePhoton > 0.")
  masym, deta, dipho, iso = CUTS[0],CUTS[1],CUTS[2],CUTS[3]
  alpha = [0,0.03]
  Rdf = Rdf.Filter("clu1_pt > 90. && clu2_pt > 90. && alpha >= " + str(alpha[0]) + " && alpha < " + str(alpha[1]) + " && masym < " + str(masym) + " && deta <     " + str(deta) + " && clu1_dipho > " + str(dipho) + " && clu2_dipho > " + str(dipho) + " && clu1_iso > " + str(iso) + " && clu2_iso > " + str(iso))

  b_XMvA = Rdf.Histo2D(("XMvA", "{} Signal ;di-cluster mass (GeV);#alpha; events / bin".format(sig), len(XB)-1, numpy.array(XB), len(AlphaBins)-1, numpy.array(AlphaBins)), "XM", "alpha")
  hist = b_XMvA.GetValue().Clone()
  if(hist.GetEntries() < 2): 
    print("Not enough stuff")
    continue

  linelist = []
  for aa in AlphaBins:
    ll = ROOT.TLine(XB[0],aa, XB[-1], aa)
    ll.SetLineColor(18)
    linelist.append(ll)
    del ll

  c1 = ROOT.TCanvas()
  c1.cd()
  hist.SetStats(0)
  hist.Scale(1/hist.Integral())
  #his.GetYaxis().SetRangeUser(AlphaBins[1], AlphaBins[-2])
  hist.Draw("colz")
  
  for lin in linelist:
    lin.Draw("same")

  c1.Print("Plots/TwoD/{}.png".format(sig))


