#
import ROOT
RDF = ROOT.ROOT.RDataFrame
ROOT.ROOT.EnableImplicitMT()
#ROOT.gROOT.SetBatch(ROOT.kTRUE)
from ROOT import *
import sys,os
import glob
import time

dgq = sys.argv[1]

if dgq == 'data16':
  base_dir = "/cms/sclark-2/RUCLU_Outputs/DoubleEG/2016/"
  Runlist = ["Run_B_ver1",
          "Run_B_ver2",
          "Run_C",
          "Run_D",
          "Run_E",
          "Run_F",
          "Run_G",
          "Run_H",
          ]

if dgq == 'data17':
  base_dir = "/cms/sclark-2/RUCLU_Outputs/DoubleEG/2017/"
  Runlist = [
          "Run_B",
          "Run_C",
          "Run_D",
          "Run_E",
          "Run_F",
          ]

if dgq == 'data18':
  base_dir = "/cms/sclark-2/RUCLU_Outputs/EGamma/2018/"
  Runlist = [
          "Run_A",
          "Run_B",
          "Run_C",
          "Run_D",
          ]

if dgq == 'muon16':
  base_dir = "/cms/sclark-2/RUCLU_Outputs/SingleMuon/2016/"
  Runlist = ["Run_B_ver1",
          "Run_B_ver2",
          "Run_C",
          "Run_D",
          "Run_E",
          "Run_F",
          "Run_G",
          "Run_H",
          ]

if dgq == 'gjets':
  #base_dir = "/cms/sclark-2/RUCLU_Outputs/GJets/2016/"
  #base_dir = "/cms/sclark-2/RUCLU_Outputs/GJets/2017/"
  base_dir = "/cms/sclark-2/RUCLU_Outputs/GJets/2018/"

  Runlist = [
            "HT40To100",
            "HT100To200",
            "HT200To400",
            "HT400To600",
            "HT600ToInf",
            ]

if dgq == 'qcd':
  base_dir = "/cms/sclark/RUCLU_Outputs/qcd/2016/"

  Runlist = [
            "HT100to200",
            "HT200to300",
            "HT300to500",
            "HT500to700",
            "HT700to1000",
            "HT1000to1500",
            "HT1500to2000",
            "HT2000toInf",
            ]



if "data" not in dgq and "muon" not in dgq: Chain = ROOT.TChain("flattenerMatching/tree")
else: Chain = ROOT.TChain("flattener/tree")

for run in Runlist:
  bb = run
  ct = 0
  print("Getting Run {}".format(run))

  if dgq != 'mc': flist = glob.glob(base_dir + run +"/flat*.root")
  else: flist = glob.glob(run+"/flat*.root")
  if len(flist) < 1: 
    print("Problem at {}".format(run))
    continue

  if(len(sys.argv)>4 and sys.argv[4]=='q'): flist=flist[0:10]
  for f in flist:
    Chain.Add(f)

    ct += 1
  #if ct > 1: break

ts = time.time()

nbins_dipho = 400*4/10
dipho_low = 0
dipho_high = 4


####
### Get big cut of all triggers
if('16' in dgq):
  file1 = open('./tnames16.txt', 'r')
###
elif('17' in dgq):
  file1 = open('./tnames17.txt', 'r')
elif('18' in dgq):
  file1 = open('./tnames18.txt', 'r')
else:
  file1 = open('./tnames18.txt', 'r')

Lines = file1.readlines()
count = 0
# Strips the newline character
tcuts = ""
for line in Lines:
  tname=line.split(",")[0]
  use=line.split(",")[1]
  if("1" in use):
    tcuts += "triggers[{}] == 1 || ".format(count)
    count += 1
tcuts = tcuts[:tcuts.rfind("||")]

elow=sys.argv[2]
ehigh=sys.argv[3]

Rdf = RDF(Chain)

Rdf = Rdf.Define("nRuclus", "ruclu_eta.size();")
Rdf = Rdf.Define("nWgt", "return 1.;")
Rdf = Rdf.Filter("nRuclus >= 1", "clusters")
#Rdf = Rdf.Filter(tcuts, "Triggers")

for jcol in ["jet_pt", "jet_eta", "jet_phi", "jet_mass", "jet_energy", "jet_btag"]:
  Rdf = Rdf.Define("{}_b".format(jcol), "{}[ abs(jet_eta < 1.4) ]".format(jcol) ) #Retain only jets in barrel

Rdf = Rdf.Define("nJets", "return jet_eta_b.size();")
Rdf = Rdf.Filter("nJets >= 1", "barrel jets")

#ROOT.gInterpreter.Declare('#include "../HelperFuncs.h"')
ROOT.gInterpreter.Declare('#include "./HelperFuncs.h"')
Rdf = Rdf.Define("nj_dr", "getClosestJetDR(ruclu_eta, ruclu_phi, ruclu_energy, moe, jet_pt_b, jet_eta_b, jet_phi_b, jet_mass_b)")

#myCuts = "nj_dr < 0.4 && ruclu_energy>{} && ruclu_energy<{} && diphoScores>0.9".format(elow, ehigh)
#myfCuts = "nj_dr < 0.4 && ruclu_energy>{} && ruclu_energy<{} && diphoScores<0.9".format(elow, ehigh)
myCuts = "nj_dr < 0.15 && ruclu_energy>{} && ruclu_energy<{} && diphoScores>0.9".format(elow, ehigh)
myfCuts = "nj_dr < 0.15 && ruclu_energy>{} && ruclu_energy<{} && diphoScores<0.9".format(elow, ehigh)

for rcol in ["ruclu_energy", "ruclu_eta", "ruclu_phi", "moe", "diphoScores", "monophoScores"]:
  Rdf = Rdf.Define("{}_pp".format(rcol), "{}[ ({}) ]".format(rcol, myCuts) ) #Only passing clusters
  Rdf = Rdf.Define("{}_ff".format(rcol), "{}[ ({}) ]".format(rcol, myfCuts) ) #fail

rr = Rdf.Report()
rr.Print()

###
#Pass Variables
Rdf = Rdf.Define("ClusterMass","ruclu_energy * moe")
Rdf = Rdf.Define("ClusterMass_pp","ruclu_energy_pp * moe_pp")
Rdf = Rdf.Define("nj_e_pp", "getClosestJetEn(ruclu_eta_pp, ruclu_phi_pp, ruclu_energy_pp, moe_pp, jet_pt_b, jet_eta_b, jet_phi_b, jet_mass_b, jet_energy_b)")
Rdf = Rdf.Define("nj_dr_pp", "getClosestJetDR(ruclu_eta_pp, ruclu_phi_pp, ruclu_energy_pp, moe_pp, jet_pt_b, jet_eta_b, jet_phi_b, jet_mass_b)")
Rdf = Rdf.Define("eratio_pp", "ruclu_energy_pp / nj_e_pp")
Rdf = Rdf.Define("ClusterMass_iso_pp","ClusterMass_pp[eratio_pp > 0.5 && eratio_pp < 1.0]")
Rdf = Rdf.Define("energy_iso_pp","ruclu_energy_pp[eratio_pp > 0.5 && eratio_pp < 1.0]")
#Rdf = Rdf.Define("eta_iso_pp","ruclu_eta_pp[eratio_pp > 0.5 && eratio_pp < 1.0]")
#Rdf = Rdf.Define("phi_iso_pp","ruclu_phi_pp[eratio_pp > 0.5 && eratio_pp < 1.0]")

###
#Fail Variables
Rdf = Rdf.Define("ClusterMass_ff","ruclu_energy_ff * moe_ff")
Rdf = Rdf.Define("nj_e_ff", "getClosestJetEn(ruclu_eta_ff, ruclu_phi_ff, ruclu_energy_ff, moe_ff, jet_pt_b, jet_eta_b, jet_phi_b, jet_mass_b, jet_energy_b)")
Rdf = Rdf.Define("nj_dr_ff", "getClosestJetDR(ruclu_eta_ff, ruclu_phi_ff, ruclu_energy_ff, moe_ff, jet_pt_b, jet_eta_b, jet_phi_b, jet_mass_b)")
Rdf = Rdf.Define("eratio_ff", "ruclu_energy_ff / nj_e_ff")
Rdf = Rdf.Define("ClusterMass_iso_ff","ClusterMass_ff[eratio_ff > 0.5 && eratio_ff < 1.0]")
#Rdf = Rdf.Define("energy_iso_ff","ruclu_energy_ff[eratio_ff > 0.5 && eratio_ff < 1.0]")
#Rdf = Rdf.Define("eta_iso_ff","ruclu_eta_ff[eratio_ff > 0.5 && eratio_ff < 1.0]")
#Rdf = Rdf.Define("phi_iso_ff","ruclu_phi_ff[eratio_ff > 0.5 && eratio_ff < 1.0]")

### 
# Pass Plots
masshist_pp = Rdf.Histo1D(("mass_pp","Diphoton Mass, pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'ClusterMass_iso_pp', 'nWgt')
print("Pass Entries: {}".format(masshist_pp.GetValue().GetEntries()))
#energyhist_pp = Rdf.Histo1D(("energy_pp","Cluster Energy, pass; Energy (GeV); Events",100, 25, 65), 'energy_iso_pp', 'nWgt')
#etahist_pp = Rdf.Histo1D(("eta_pp","Cluster #eta, pass; #eta; Events",100, -2, 2), 'eta_iso_pp', 'nWgt')
#phihist_pp = Rdf.Histo1D(("phi_pp","Cluster #phi, pass; #phi; Events",100, -4, 4), 'phi_iso_pp', 'nWgt')
##drhist_pp = Rdf.Histo1D(("dr_pp","#Delta R to Nearest Jet, pass; #Delta R; Events", 100, 0, 1),'nj_dr_pp', 'nWgt')
##rathist_pp = Rdf.Histo1D(("eratio_pp","Cluster Energy / Jet Energy, pass; Energy Ratio; Events", 100, 0, 2),'eratio_pp', 'nWgt')
##2d
#twoD_CluE_pp = Rdf.Histo2D(("energytwod_pp"," Cluster Energy vs. Diphoton Mass pass; Mass (GeV); Energy (GeV)", nbins_dipho, dipho_low, dipho_high, 100, 25, 65),"ClusterMass_pp","ruclu_energy_pp", "nWgt")
#twoD_deltaR_pp = Rdf.Histo2D(("drtwod_pp"," #Delta R(Cluster, Nearest Jet) vs. Diphoton Mass pass; Mass (GeV); #DeltaR", nbins_dipho, dipho_low, dipho_high, 100, 0, 0.45),"ClusterMass_pp","nj_dr_pp", "nWgt")
#twoD_Iso_pp = Rdf.Histo2D(("isotwod_pp"," (Cluster Energy / Jet Energy) vs. Diphoton Mass pass; Mass (GeV); Energy Ratio", nbins_dipho, dipho_low, dipho_high, 100, 0, 2),"ClusterMass_pp","eratio_pp", "nWgt")
twoD_E_pp = Rdf.Histo2D(("etwod_pp"," (Cluster Energy / Jet Energy) vs. Diphoton Mass pass; Mass (GeV); Energy Ratio", nbins_dipho, dipho_low, dipho_high, 100, 0,
200),"ClusterMass_iso_pp","energy_iso_pp", "nWgt")


### 
# Fail Plots
masshist_ff = Rdf.Histo1D(("mass_ff","Diphoton Mass, fail",nbins_dipho, dipho_low, dipho_high), 'ClusterMass_iso_ff', 'nWgt')
print("Fail Entries: {}".format(masshist_ff.GetValue().GetEntries()))
#energyhist_ff = Rdf.Histo1D(("energy_ff","Cluster Energy, fail; Energy (GeV); Events",100, 25, 65), 'ruclu_energy_ff', 'nWgt')
#etahist_ff = Rdf.Histo1D(("eta_ff","Cluster #eta, fail; #eta; Events",100, -2, 2), 'eta_iso_ff', 'nWgt')
#phihist_ff = Rdf.Histo1D(("phi_ff","Cluster #phi, fail; #phi; Events",100, -4, 4), 'phi_iso_ff', 'nWgt')
##drhist_ff = Rdf.Histo1D(("dr_ff","#Delta R to Nearest Jet, fail; #Delta R; Events", 100, 0, 1),'nj_dr_ff', 'nWgt')
##rathist_ff = Rdf.Histo1D(("eratio_ff","Cluster Energy / Jet Energy, fail; Energy Ratio; Events", 100, 0, 2),'eratio_ff', 'nWgt')
##2d
#twoD_CluE_ff = Rdf.Histo2D(("energytwod_ff"," Cluster Energy vs. Diphoton Mass fail; Mass (GeV); Energy (GeV)", nbins_dipho, dipho_low, dipho_high, 100, 25, 65),"ClusterMass_ff","ruclu_energy_ff", "nWgt")
#twoD_deltaR_ff = Rdf.Histo2D(("drtwod_ff"," #Delta R(Cluster, Nearest Jet) vs. Diphoton Mass fail; Mass (GeV); #DeltaR", nbins_dipho, dipho_low, dipho_high, 100, 0, 0.45),"ClusterMass_ff","nj_dr_ff", "nWgt")
#twoD_Iso_ff = Rdf.Histo2D(("isotwod_ff"," (Cluster Energy / Jet Energy) vs. Diphoton Mass fail; Mass (GeV); Energy Ratio", nbins_dipho, dipho_low, dipho_high, 100, 0, 2),"ClusterMass_ff","eratio_ff", "nWgt")


oF = TFile("{}Out_e{}_{}.root".format(dgq,elow,ehigh), "recreate")
oF.cd()
#Pass
masshist_pp.GetValue().Write()
#energyhist_pp.Write()
#etahist_pp.Write()
##phihist_pp.Write()
##drhist_pp.Write()
##rathist_pp.Write()
#twoD_CluE_pp.Write()
#twoD_deltaR_pp.Write()
#twoD_Iso_pp.Write()
twoD_E_pp.Write()

#Fail
masshist_ff.GetValue().Write()
#energyhist_ff.Write()
#etahist_ff.Write()
#phihist_ff.Write()
##drhist_ff.Write()
##rathist_ff.Write()
#twoD_CluE_ff.Write()
#twoD_deltaR_ff.Write()
#twoD_Iso_ff.Write()


oF.Write()
oF.Save()
oF.Close()

c1 = ROOT.TCanvas()
c1.cd()
masshist_pp.GetValue().Draw("hist")
c1.Print("tmp.png")


tf = time.time()
print("Run time: {} min".format( (tf-ts) / 60 ))
