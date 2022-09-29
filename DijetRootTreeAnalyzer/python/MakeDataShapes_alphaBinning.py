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

#############################
#Get DATA
DATA = []
for ff in os.listdir(xaastorage):
  #if("Run" in ff and year in ff): #one year data
  if("Run" in ff and "20" in ff): #All Run II Data
    DATA.append(os.path.join(xaastorage,ff))

#Analysis Cuts
# masym, eta, dipho, iso
#CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [1.0, 3.5, 0.9, 0.8] #Loose
#CUTS = [0.25, 1.5, 0.9, 0.8] #Analysis Cuts
CUTS = [0.25, 1.5, 0.9, 0.1] #Loose Analysis Cuts

#################################################

AlphaBins = [0.0,0.00454,0.00508,0.00561,0.00615,0.00669,0.00723,0.00777,0.00831,0.00885,0.009405,0.00998,0.01055,0.01108,0.01161,0.01214,0.01267,0.0132,0.013935,0.01482,0.0155,0.01606,0.01662,0.01718,0.01774,0.018475,0.01945,0.02025,0.02082,0.02139,0.02196,0.02265,0.02367,0.02457,0.02525,0.02593,0.02661,0.02729,0.02797,0.02865,0.03]

for abin_num in range(0,len(AlphaBins)-1):

  lA = AlphaBins[abin_num]
  hA = AlphaBins[abin_num+1]
  print("---------------------------------------------------------------------------")
  print("Alpha bin: ")
  print("{}: {} - {}".format(abin_num, lA, hA))
  newd = "{}/../inputs/Shapes_DATA/alphaBinning/{}/".format(dir_path,abin_num)
  PL.MakeFolder(newd)

  saveTree = False
  (dX, dX1, dXvA) = PL.GetDiphoShapeAnalysis(DATA, "pico_skim", "data", CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "1.", saveTree, "RunII/"+str(abin_num))
  print("Data Entries: {}".format(dX1.GetEntries()))

  dfname = newd + "DATA.root"
  dfile = ROOT.TFile(dfname, "recreate")
  dX1.SetName("data_XM1")
  dX.SetName("data_XM")
  dXvA.SetName("data_XvA")
  dX1.Write()
  dX.Write()
  dXvA.Write()
  dfile.Close()



