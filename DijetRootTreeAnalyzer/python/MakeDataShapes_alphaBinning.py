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

AlphaBins = [0.0,0.00041,0.00083,0.00126,0.0017,0.00214,0.00259,0.00305,0.00352,0.004,0.00449,0.00499,0.0055,0.00602,0.00655,0.00709,0.00764,0.0082,0.00877,0.00935,0.00994,0.01054,0.01115,0.01178,0.01242,0.01307,0.01373,0.01441,0.0151,0.0158,0.01652,0.01725,0.01799,0.01875,0.01952,0.02031,0.02111,0.02193,0.02276,0.02361,0.02448,0.02536,0.02626,0.02718,0.02812,0.02907,0.03]

for abin_num in range(0,len(AlphaBins)-1):

  lA = AlphaBins[abin_num]
  hA = AlphaBins[abin_num+1]
  print("---------------------------------------------------------------------------")
  print("Alpha bin: ")
  print("{}: {} - {}".format(abin_num, lA, hA))
  newd = "{}/../inputs/Shapes_DATA/alphaBinning/{}/".format(dir_path,abin_num)
  PL.MakeFolder(newd)

  rfile = open("{}/arange.txt".format(newd),"w")
  rfile.write("{},{}".format(lA,hA))
  rfile.close()

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




