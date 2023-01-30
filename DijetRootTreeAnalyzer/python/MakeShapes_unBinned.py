import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../../.")
import PlottingPayload as PL
gROOT.SetBatch()

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"
const_alpha = False #Use this to get signals at one alpha val
this_alpha = 0.005 #Set this to the alpha you want. If const_alpha = False, this does nothing

def doOneInput(sig, h, H, S, norm = False):

    fname = "{}/../inputs/Shapes_fromGen/unBinned/{}/{}.root".format(dir_path,sig,S)
    if(H=="h_AveDijetMass_1GeV"):
      toF = TFile(fname, "recreate")
    else:
      toF = TFile(fname, "update")
    if norm:
        try:
          h.Scale(1./h.Integral())
        except ZeroDivisionError:
          print("Not normalizing")

    toF.cd()
    h.SetName(H)
    h.Write()
    toF.Write()
    toF.Save()
    toF.Close()

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


print("Doing Generated Signals")

SignalsGenerated = {}
for ff in os.listdir(xaastorage):
  if(ff[0]=="X"):
    thisxa = ff[ : ff.find("_")]
    this_x = int(thisxa[1:thisxa.find("A")])
    this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
    if(this_phi / this_x > 0.031 ): continue
    if(thisxa in SignalsGenerated.keys()):
      SignalsGenerated[thisxa].append(os.path.join(xaastorage, ff))
    else:
      SignalsGenerated[thisxa] = [os.path.join(xaastorage, ff)]

g_alphas = SignalsGenerated.keys()

lA = 0.0
hA = 0.03

for thisSigIndex, oneSig in SignalsGenerated.items():
  whichSig = oneSig[0][0 : oneSig[0].find("_")]
  whichSig = whichSig.split("/")[-1]
  thisX = int(whichSig[1 : whichSig.find("A")])
  thisPhi = float(whichSig[whichSig.find("A")+1 : ].replace("p","."))
  thisAlpha = thisPhi / thisX
  #if(whichSig != "X600A3"):continue
  #if(thisX != 600): continue

  print("\nSignal: {}".format(whichSig))
  new_dir = "{}/../inputs/Shapes_fromGen/unBinned/{}/".format(dir_path,whichSig)
  PL.MakeFolder(new_dir)

  (sXr, sX1r, sA1r, sPhir, sXvAr) = PL.GetDiphoShapeAnalysisPlusAlpha(SignalsGenerated[thisSigIndex], thisAlpha, "pico_nom", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
  doOneInput(whichSig, sX1r, "h_AveDijetMass_1GeV", "Sig_nominal", True)
  doOneInput(whichSig, sA1r, "h_alpha_fine", "Sig_nominal", True)
  doOneInput(whichSig, sPhir, "h_phi_fine", "Sig_nominal", True)

  (sXpu, sX1pu, sA1pu, sPhipu, sXvApu) = PL.GetDiphoShapeAnalysisPlusAlpha(SignalsGenerated[thisSigIndex], thisAlpha, "pico_nom", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeightUp*weight*10.*5.99")
  (sXpd, sX1pd, sA1pd, sPhipd, sXvApd) = PL.GetDiphoShapeAnalysisPlusAlpha(SignalsGenerated[thisSigIndex], thisAlpha, "pico_nom", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton","puWeightDown*weight*10.*5.99")
  (sXsu, sX1su, sA1su, sPhisu, sXvAsu) = PL.GetDiphoShapeAnalysisPlusAlpha(SignalsGenerated[thisSigIndex], thisAlpha, "pico_scale_up", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton","weight*10.*5.99")
  (sXsd, sX1sd, sA1sd, sPhisd, sXvAsd) = PL.GetDiphoShapeAnalysisPlusAlpha(SignalsGenerated[thisSigIndex], thisAlpha, "pico_scale_down", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton","weight*10.*5.99")

  with open(new_dir + whichSig+".txt", 'w') as eff:
      E = sX1r.GetEntries()
      G = lookup(whichSig)
      print "eff ("+whichSig+")---> " + str(float(E)/float(G))
      eff.write(str(float(E)/float(G)))

  doOneInput(whichSig, sX1pu, "h_AveDijetMass_1GeV", "Sig_PU", True)
  doOneInput(whichSig, sA1pu, "h_alpha_fine", "Sig_PU", True)
  doOneInput(whichSig, sX1pd, "h_AveDijetMass_1GeV", "Sig_PD", True)
  doOneInput(whichSig, sA1pd, "h_alpha_fine", "Sig_PD", True)
  doOneInput(whichSig, sX1su, "h_AveDijetMass_1GeV", "Sig_SU", True)
  doOneInput(whichSig, sA1su, "h_alpha_fine", "Sig_SU", True)
  doOneInput(whichSig, sX1sd, "h_AveDijetMass_1GeV", "Sig_SD", True)
  doOneInput(whichSig, sA1sd, "h_alpha_fine", "Sig_SD", True)

  dataFile = ROOT.TFile("/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_DATA/alphaBinning/ALL/DATA.root","read")
  os.system("cp /cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_DATA/alphaBinning/ALL/DATA.root {}/DATA.root".format(new_dir))
  dX = dataFile.Get("data_XM")
  dX1 = dataFile.Get("data_XM1")
  dXvA = dataFile.Get("data_XvA")

  oF = TFile("{}/PLOTS.root".format(new_dir), "recreate")
  sXr.Scale(1/sXr.Integral())
  sXr.Write()
  sX1r.Write()
  dX.Write()
  dX1.Write()

  dataFile.Close()
  oF.Close()


