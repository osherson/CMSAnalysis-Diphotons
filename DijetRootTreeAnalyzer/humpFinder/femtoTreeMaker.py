import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time
import os
RDF = ROOT.RDataFrame.RDataFrame

dir_path = os.path.dirname(os.path.realpath(__file__))
gROOT.SetBatch()

#year = sys.argv[1]
year='2018'

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"

sample="Data"

################################################
DATA = []
if(sample=="Data"):
  #Get DATA
  for ff in os.listdir(xaastorage):
    #if("Run" in ff and year in ff): #one year data
    if("Run" in ff and "20" in ff): #All Run II Data
      DATA.append(os.path.join(xaastorage,ff))

  if("quick" in sys.argv):
    DATA = ["/cms/xaastorage-2/DiPhotonsTrees/Run_D_2017.root"]

elif(sample=="GJets"):
  #Get DATA
  for ff in os.listdir("/cms/sclark-2/DiPhotonsTrees/GJets/"):
    if("HT" in ff and "20" in ff): #All Run II Data
      DATA.append(os.path.join("/cms/sclark-2/DiPhotonsTrees/GJets/",ff))

if(sample=="Signal"):
  #Get DATA
  for ff in os.listdir(xaastorage):
    #if("Run" in ff and year in ff): #one year data
    if(ff.startswith("X") and ff.endswith(".root") and "20" in ff): #All Run II Data
      DATA.append(os.path.join(xaastorage,ff))

    # Load files:
print(DATA)
if(sample=="Data"):
  Chain = ROOT.TChain("pico_skim")
elif(sample=="GJets"):
  Chain = ROOT.TChain("pico_full")
elif(sample=="Signal"):
  Chain = ROOT.TChain("pico_nom")

for f in DATA:
    Chain.Add(f)

Rdf = RDF(Chain)
# Make cuts:
Rdf = Rdf.Filter("HLT_DoublePhoton > 0.","trigger")

##
#Analysis Cuts
Rdf = Rdf.Filter("clu1_pt > 90. && clu2_pt > 90.", "pt > 90")
Rdf = Rdf.Filter("masym < 0.25", "Mass Asymmetry < 0.25")
Rdf = Rdf.Filter("deta < 1.5", "Delta Eta < 1.5")
Rdf = Rdf.Filter("clu1_dipho > 0.9 && clu2_dipho > 0.9", "dipho > 0.9")
Rdf = Rdf.Filter("clu1_iso > 0.8 && clu2_iso > 0.8", "iso > 0.8")

rep = Rdf.Report()
rep.Print()

#savename = "FemtoTrees/{}_trigger.root".format(sample)
#print("Saving Data Tree As: {}".format(savename))
#Rdf.Snapshot("femtotree", savename)
