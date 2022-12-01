#
import ROOT
RDF = ROOT.ROOT.RDataFrame
ROOT.ROOT.EnableImplicitMT()
ROOT.gROOT.SetBatch(ROOT.kTRUE)
from ROOT import *
import sys,os
import glob
import time

gInterpreter.Declare('#include "./RDF_Functions.h"')


bd16 = "/cms/sclark-2/RUCLU_Outputs/DoubleEG/2016/"
bd17 = "/cms/sclark-2/RUCLU_Outputs/DoubleEG/2017/"
bd18 = "/cms/sclark-2/RUCLU_Outputs/EGamma/2018/"
Runlist16 = ["Run_B_ver1", "Run_B_ver2", "Run_C", "Run_D", "Run_E", "Run_F", "Run_F_HIPM", "Run_G", "Run_H", ]
Runlist17 = ["Run_B", "Run_C", "Run_D", "Run_E", "Run_F"]
Runlist18 = ["Run_A", "Run_B", "Run_C", "Run_D"]
rd16 = [bd16 + rr for rr in Runlist16]
rd17 = [bd17 + rr for rr in Runlist17]
rd18 = [bd18 + rr for rr in Runlist18]
allruns = rd16 + rd17 + rd18

yrs = [(16,rd16),(17,rd17),(18,rd18)]

for year,runlist in yrs:
  print("Beginning {}".format(year))
  ts = time.time()

  Chain = ROOT.TChain("flattener/tree")
  for run in runlist:
    flist = glob.glob(run+"/flat*.root")
    if len(flist) < 1: 
      print("Problem at {}".format(run))
      continue

    #if('q' in sys.argv): flist=flist[0:3]
    if('q' in sys.argv): flist=flist[0:20]
    for f in flist:
      Chain.Add(f)
  ####
  ### Get big cut of all triggers
  file1 = open('/home/sclark/tnames/tnames{}.txt'.format(year), 'r')
  Lines = file1.readlines()
  count = 0
  # Strips the newline character
  tcuts = ""
  for line in Lines:
    tcuts += "triggers[{}] == 1 || ".format(count)
    count += 1
  tcuts = tcuts[:tcuts.rfind("||")]

  Rdf = RDF(Chain)

###
  Rdf = Rdf.Define("sf", "return 1")
  Rdf = Rdf.Define("weight", "return 1")
  #Get pT all clusters
  Rdf = Rdf.Define("ruclu_pt", "get_pT(moe, ruclu_energy, ruclu_eta, ruclu_phi, pvtx_z, sf)")
  #Get index of two leading clusters in pT
  Rdf = Rdf.Define("pt_idx", "indexes(ruclu_pt)")
  Rdf = Rdf.Define("pt_idx_1", "pt_idx[0]")
  Rdf = Rdf.Define("pt_idx_2", "pt_idx[1]")
  Rdf = Rdf.Filter("pt_idx_1 != pt_idx_2", "Contains Two Separate Clusters")
  Rdf = Rdf.Filter(tcuts, "Triggers")
  #Xmass, aMass, alpha
  Rdf = Rdf.Define("XM", "get_XM(pt_idx_1, pt_idx_2, moe, ruclu_energy, ruclu_eta, ruclu_phi, pvtx_z, ruclu_pt)")
  Rdf = Rdf.Define("aM", "get_aM(pt_idx_1, pt_idx_2, moe, ruclu_energy)")
  Rdf = Rdf.Define("alpha", "aM/XM")
  #Helper variables for iso
  Rdf = Rdf.Define("clu_to_jet_DR", "get_match_DR(ruclu_pt, ruclu_eta, ruclu_phi, ruclu_energy, jet_pt, jet_eta, jet_phi, jet_energy)")
  Rdf = Rdf.Define("clu_to_jet_index", "get_match_index(ruclu_pt, ruclu_eta, ruclu_phi, ruclu_energy, jet_pt, jet_eta, jet_phi, jet_energy)")
  Rdf = Rdf.Define("jetE", "get_JetE(clu_to_jet_index, clu_to_jet_DR, jet_energy, ruclu_energy)")

  Rdf = Rdf.Define("clu1_to_jet_DR","clu_to_jet_DR[pt_idx_1]")
  Rdf = Rdf.Define("clu2_to_jet_DR","clu_to_jet_DR[pt_idx_2]")
  Rdf = Rdf.Filter("clu1_to_jet_DR < 0.4", "Lead Cluster inside Jet")
  #Iso, masym, deta
  Rdf = Rdf.Define("iso", "ruclu_energy / jetE")
  Rdf = Rdf.Define("masym", "get_Masym(pt_idx_1, pt_idx_2, moe, ruclu_energy)")
  Rdf = Rdf.Define("deta", "get_Deta(pt_idx_1, pt_idx_2, ruclu_eta)")
  #Now just save quantities for leading two clusters
  #Lead Cluster
  Rdf = Rdf.Define("clu1_pt","ruclu_pt[pt_idx_1]")
  Rdf = Rdf.Define("clu1_eta","ruclu_eta[pt_idx_1]")
  Rdf = Rdf.Define("clu1_phi","ruclu_phi[pt_idx_1]")
  Rdf = Rdf.Define("clu1_energy","ruclu_energy[pt_idx_1]")
  Rdf = Rdf.Define("clu1_moe","moe[pt_idx_1]")
  Rdf = Rdf.Define("clu1_mass","clu1_moe * clu1_energy")
  Rdf = Rdf.Define("clu1_iso","iso[pt_idx_1]")
  Rdf = Rdf.Define("clu1_monopho","monophoScores[pt_idx_1]")
  Rdf = Rdf.Define("clu1_dipho","diphoScores[pt_idx_1]")
  Rdf = Rdf.Define("clu1_hadron","hadronScores[pt_idx_1]")

  Rdf = Rdf.Filter("clu1_energy > 30 && clu1_energy < 60", "Lead Cluster energy")
  Rdf = Rdf.Filter("clu1_dipho > 0.9 ", "Lead Cluster diphoton score")

  rep = Rdf.Report()
  rep.Print()

  Rdf.Snapshot("pico_tree", "PicoTrees/data_{}.root".format(year))#, branchList, snapshotOptions) 
  tf = time.time()
  print("Processing 20{} took {:.2f} minutes".format(year, (tf-ts)/60))
