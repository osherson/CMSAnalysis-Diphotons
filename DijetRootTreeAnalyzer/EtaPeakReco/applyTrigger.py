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


#yrs = [(16,rd16),(17,rd17),(18,rd18)]
#yrs = [(16,rd16)]
yrs = ["2016","2017","2018"]
data_dir = "/cms/xaastorage-2/DiPhotonsTrees/"

for year in yrs:
  print("Beginning {}".format(year))
  ts = time.time()

  Chain = ROOT.TChain("pico_full")
  #Chain = ROOT.TChain("pico_skim")
  flist = []
  for fil in os.listdir(data_dir):
    if(fil.startswith("Run") and year in fil):
      flist.append(os.path.join(data_dir,fil))

  for f in flist:
    Chain.Add(f)

  Rdf = RDF(Chain)

###
  #Rdf = Rdf.Filter("HLT_DoublePhoton == 1", "Triggers")
  Rdf = Rdf.Filter("clu1_iso < 0.4", "Lead Cluster inside Jet")
  Rdf = Rdf.Filter("clu1_energy > 30 && clu1_energy < 60", "Lead Cluster energy")
  Rdf = Rdf.Filter("clu1_dipho > 0.9 ", "Lead Cluster diphoton score")

  rep = Rdf.Report()
  rep.Print()

  Rdf.Snapshot("pico_tree", "PicoTrees/data_{}.root".format(year))#, branchList, snapshotOptions) 
  tf = time.time()
  print("Processing {} took {:.2f} minutes".format(year, (tf-ts)/60))
