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
RDF = ROOT.RDataFrame.RDataFrame

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"

#############################
#Get DATA
DATA = []
for ff in os.listdir(xaastorage):
  #if("Run" in ff and year in ff): #one year data
  if("Run" in ff and "20" in ff): #All Run II Data
    DATA.append(os.path.join(xaastorage,ff))

CUTS = [0.25, 1.5, 0.9, 0.1] #Loose 1
#CUTS = [0.5, 2.5, 0.9, 0.1] #Loose 2
#CUTS = [0.5, 3.5, 0.5, 0.1] #Loose 3 ALSO CHANGED PT CUT IN PLOTTING PAYLOAD

AlphaBins = [0, 0.01505, 0.03]
#AlphaBins = [0, 0.03]

for abin_num in range(0,len(AlphaBins)-1):
#for abin_num in range(len(AlphaBins)-2, 13, -1):

  lA = AlphaBins[abin_num]
  hA = AlphaBins[abin_num+1]
  print("---------------------------------------------------------------------------")
  print("Alpha bin: ")
  print("{}: {} - {}".format(abin_num, lA, hA))

  Chain = ROOT.TChain("pico_skim")
  for f in DATA:
      Chain.Add(f)
  Rdf         =   RDF(Chain)
  # Make cuts:
  masym=CUTS[0]
  deta=CUTS[1]
  dipho=CUTS[2]
  iso=CUTS[3]
  Rdf         =   Rdf.Filter("HLT_DoublePhoton > 0.", "trigger")
  Rdf = Rdf.Filter("XM > 2000","X Mass")
  Rdf         =   Rdf.Filter("clu1_pt > 90. && clu2_pt > 90. && alpha >= " + str(lA) + " && alpha < " + str(hA) + " && masym < " + str(masym) + " && deta <     " + str(deta) + " && clu1_dipho > " + str(dipho) + " && clu2_dipho > " + str(dipho) + " && clu1_iso > " + str(iso) + " && clu2_iso > " + str(iso), "Cuts")
  rep = Rdf.Report()
  rep.Print()

  cols=Rdf.AsNumpy(["XM","alpha"])
  xm, al = cols["XM"], cols["alpha"]
  for x,a in zip(xm,al):
    print(x,a)






