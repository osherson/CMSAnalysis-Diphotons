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

year = sys.argv[1]

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"


################################################
#Get DATA
DATA = []
for ff in os.listdir(xaastorage):
  if("Run" in ff and year in ff): #one year data
  #if("Run" in ff and "20" in ff): #All Run II Data
    DATA.append(os.path.join(xaastorage,ff))

#DATA = [DATA[0]]
print(DATA)
time.sleep(3)

#Analysis Cuts
masym = 1.0
deta = 3.5
dipho = 0.5
iso = 0.5

eta_mass = 0.547862

#dChain = ROOT.TChain("pico_full")
dChain = ROOT.TChain("pico_skim")

for df in DATA:
    dChain.Add(df)
Rdf = RDF(dChain)
# Make cuts:
#Rdf = Rdf.Filter("HLT_DoublePhoton > 0.", "Trigger")
Rdf = Rdf.Filter("clu1_energy > 30 && clu1_energy < 60 && clu2_energy > 30 && clu2_energy < 60", "Energy Cut")
Rdf = Rdf.Filter("clu1_dipho > 0.9 && clu1_monopho < 0.5 && clu2_dipho > 0.9 && clu2_monopho < 0.5", "Classifier Cut")
Rdf = Rdf.Filter("clu1_iso > 0.5 && clu2_iso > 0.5 ", "Isolation Cut")

Rdf = Rdf.Define("clu1_mass","clu1_moe * clu1_energy")
Rdf = Rdf.Define("clu2_mass","clu2_moe * clu2_energy")
Rdf = Rdf.Filter("abs(clu1_mass - {}) < 0.05 || abs(clu2_mass - {}) < 0.05".format(eta_mass, eta_mass), "Eta Mass Cut")


rep = Rdf.Report()
rep.Print()

Rdf.Snapshot("tree","./Trees/{}/etaTree.root".format(year))

