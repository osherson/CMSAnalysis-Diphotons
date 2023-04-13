#
import ROOT
RDF = ROOT.ROOT.RDataFrame
ROOT.ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(ROOT.kTRUE)
from ROOT import *
import sys,os
import glob
import time


dgq = sys.argv[1]


if dgq == 'gjets':
  base_dir = "/cms/sclark-2/RUCLU_Outputs/GJets/2016/"
  #base_dir = "/cms/sclark-2/RUCLU_Outputs/GJets/2017/"
  #base_dir = "/cms/sclark-2/RUCLU_Outputs/GJets/2018/"

  Runlist = [
            "HT40To100",
            "HT100To200",
            "HT200To400",
            "HT400To600",
            "HT600ToInf",
            ]



#Chain = ROOT.TChain("flattenerMatching/tree")
Chain = ROOT.TChain("flattener/tree")

bb=""

for run in Runlist:
  bb = run
  ct = 0
  print("Getting Run {}".format(run))

  if dgq != 'qg': flist = glob.glob(base_dir + run +"/flat*.root")
  else: flist = glob.glob(run+"/flat*.root")
  if len(flist) < 1: 
    print("Problem at {}".format(run))
    continue

  if(len(sys.argv)>2 and sys.argv[2]=='q'): flist=flist[0:3]
  for f in flist:
    Chain.Add(f)

    ct += 1
  #if ct > 1: break

ts = time.time()

nbins_dipho = 400
if dgq == 'gun': nbins_dipho = 100
dipho_low = 0
dipho_high = 10
xlow = 0
xhigh = 2
#xlow = 0.2
#xhigh = 0.8

Rdf = RDF(Chain)

Rdf = Rdf.Define("nRuclus", "ruclu_eta.size();")
#Rdf = Rdf.Define("nRuclus", "return ruclu_eta.size();")
Rdf = Rdf.Filter("nRuclus >= 1", "clusters")

#First get jets in barrel only
for jcol in ["jet_pt", "jet_eta", "jet_phi", "jet_mass", "jet_energy", "jet_btag", "jet_matchedEtaE"]:
  Rdf = Rdf.Define("{}_b".format(jcol), "{}[ abs(jet_eta < 1.4) ]".format(jcol) ) #Retain only jets in barrel

Rdf = Rdf.Define("nJets", "return jet_eta_b.size();")
Rdf = Rdf.Filter("nJets >= 1", "barrel jets")

ROOT.gInterpreter.Declare('#include "HelperFuncs.h"')
Rdf = Rdf.Define("MatchedClusterMass", "getMatchedClusterMass(ruclu_eta, ruclu_phi, ruclu_energy, moe, jet_pt_b, jet_eta_b, jet_phi_b, jet_mass_b, jet_energy_b, jet_matchedEtaE_b)")
Rdf = Rdf.Define("MatchedClusterDipho", "getMatchedClusterParam(ruclu_eta, ruclu_phi, ruclu_energy, moe, jet_pt_b, jet_eta_b, jet_phi_b, jet_mass_b, jet_energy_b, jet_matchedEtaE_b, diphoScores)")
Rdf = Rdf.Define("MatchedClusterMono", "getMatchedClusterParam(ruclu_eta, ruclu_phi, ruclu_energy, moe, jet_pt_b, jet_eta_b, jet_phi_b, jet_mass_b, jet_energy_b, jet_matchedEtaE_b, monophoScores)")
Rdf = Rdf.Define("MatchedClusterEnergy", "getMatchedClusterParam(ruclu_eta, ruclu_phi, ruclu_energy, moe, jet_pt_b, jet_eta_b, jet_phi_b, jet_mass_b, jet_energy_b, jet_matchedEtaE_b, ruclu_energy)")


mypCuts = "MatchedClusterEnergy>30 && MatchedClusterEnergy<60 && (MatchedClusterDipho>0.9 && MatchedClusterMono < 0.5)"
myfCuts = "MatchedClusterEnergy>30 && MatchedClusterEnergy<60 && (MatchedClusterDipho<0.9 && MatchedClusterMono > 0.5)"

Rdf = Rdf.Define("passmass", "MatchedClusterMass[{}]".format(mypCuts))
Rdf = Rdf.Define("failmass", "MatchedClusterMass[{}]".format(myfCuts))

### 
masshist_p = Rdf.Histo1D(("mass","Diphoton Mass, pass",nbins_dipho, dipho_low, dipho_high), 'passmass', 'wgt')
masshist_f = Rdf.Histo1D(("fail","Diphoton Mass, fail",nbins_dipho, dipho_low, dipho_high), 'failmass', 'wgt')

### 

oF = TFile("{}Out_m.root".format(dgq), "recreate")
oF.cd()
#Pass
masshist_p.GetXaxis().SetRangeUser(xlow,xhigh)
masshist_p.GetValue().Write()
masshist_f.GetXaxis().SetRangeUser(xlow,xhigh)
masshist_f.GetValue().Write()

#for hist in [masshist_p, ehist_eta, bhist_eta, pthist_eta]:
#  c1 = TCanvas()
#  hist.Draw("hist")
#  c1.Print("plots/jetvars/{}_{}.png".format(bb, hist.GetName()))

oF.Write()
oF.Save()
oF.Close()

tf = time.time()
print("Run time: {} min".format( (tf-ts) / 60 ))
