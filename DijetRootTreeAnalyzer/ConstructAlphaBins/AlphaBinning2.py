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

SignalsGenerated = {0.005:[], 0.01:[], 0.015:[], 0.02:[], 0.025:[]}

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
    SignalsGenerated[this_phi / this_x].append(os.path.join(xaastorage,ff))

ct = 0

galphas = [0.005, 0.01, 0.015, 0.02, 0.025]
#galphas = [0.005]
#galphas = galphas[0:2]

useAlphaBins = []

for galpha in galphas:
  mybins = []
  print("DOING ALPHA = {}".format(galpha))

  alphaSigs = SignalsGenerated[galpha]
  #for s in SignalsGenerated:
  #  ct += 1

  #  thisx = int(s[1 : s.find("A")])
  #  thisphi = float(s[s.find("A")+1 :].replace("p","."))
  #  thisalpha = thisphi/thisx

  #  if(thisalpha != galpha): continue #Must keep this one
    #if(thisx != 600): continue #This one is for quicker running 

  #  print(thisx, thisphi)

  masym, deta, dipho, iso = CUTS[0], CUTS[1], CUTS[2], CUTS[3]
  trigger = "HLT_DoublePhoton"

  Chain = ROOT.TChain("pico_nom")
  #for f in SignalsGenerated[s]:
  for f in alphaSigs:
      Chain.Add(f)
  Rdf = RDF(Chain)
  Rdf = Rdf.Filter(trigger+" > 0.")
  Rdf = Rdf.Filter("clu1_pt > 90. && clu2_pt > 90. && masym < " + str(masym) + " && deta <     " + str(deta) + " && clu1_dipho > " + str(dipho) + " && clu2_dipho > " + str(dipho) + " && clu1_iso > " + str(iso) + " && clu2_iso > " + str(iso))

  alphahist = Rdf.Histo1D(("alphafine","alphafine",1000,0,0.03),"alpha")

  ahist = alphahist.GetValue().Clone()
  nTot = ahist.GetEntries()

  peakFraction = 0.75

  sigW = 999999.
  bestbins = (0,0,0)
  for nbins in range(200,2,-1):
    newbins = numpy.linspace(0,0.03,nbins)
    newhist = ahist.Rebin(nbins-1, "n", newbins)

    (tsw, ccs, bins) = GetSignalWidth(newhist, galpha)
    if(tsw < sigW and sum(ccs) / nTot >= 0.75):
      sigW = tsw
      bestbins = bins
  if(bestbins == (0,0,0)): print("PROBLEM COMPUTING BINS")
  mybins.append(bestbins)
  
  #sum1, sum2, sum3 = 0,0,0
  #for bb in mybins: 
  #  sum1 += bb[0]
  #  sum2 += bb[1]
  #  sum3 += bb[2]
  #a1,a2,a3 = sum1/len(mybins), sum2/len(mybins), sum3/len(mybins)

  #useAlphaBins.append(a1)
  #useAlphaBins.append(a2)
  #useAlphaBins.append(a3)
  useAlphaBins.append(bestbins[0])
  useAlphaBins.append(bestbins[1])
  useAlphaBins.append(bestbins[2])

print(useAlphaBins)

outfile = open("alphaBinEdges.txt","w")
for aa in useAlphaBins:
  outfile.write(str(aa)+"\n")

