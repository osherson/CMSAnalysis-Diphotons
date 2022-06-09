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
gROOT.SetBatch()

sample = sys.argv[1]
etype = sys.argv[2]
if(etype=="m"): etype="monopho"
if(etype=="d"): etype="dipho"
if(etype=="h"): etype="hadron"

storage = "/cms/sclark-2/DiPhotonsTrees/"

################################################
#Get DATA
DATA = []
for ss,dd,ff in os.walk(storage):
  if(sample in ss):
    for f in ff:
      DATA.append(os.path.join(storage,ss,f))

#DATA = [DATA[0]]
print(DATA)
time.sleep(3)

dChain = ROOT.TChain("pico_nom")

for df in DATA:
    dChain.Add(df)
Rdf = RDF(dChain)

#Rdf = Rdf.Filter("clu1_moe > 0.005 && clu1_moe < 0.025", "MoE Cut")
Rdf = Rdf.Filter("clu1_moe > 0.01 && clu1_moe < 0.011", "MoE Cut")
Rdf = Rdf.Filter("clu1_iso > 0.9 ", "Isolation Cut")

if(etype=="monopho"):
  Rdf = Rdf.Filter("clu1_monopho > 0.99 ", "Classifier Cut")
elif(etype=="dipho"):
  Rdf = Rdf.Filter("clu1_dipho > 0.99 ", "Classifier Cut")
elif(etype=="hadron"):
  Rdf = Rdf.Filter("clu1_hadron > 0.99 ", "Classifier Cut")

Rdf = Rdf.Define("clu1_mass","clu1_moe * clu1_energy")

rep = Rdf.Report()
rep.Print()

Rdf.Snapshot("tree","./Trees/{}/cutTree_{}_{}.root".format(sample,sample,etype))

