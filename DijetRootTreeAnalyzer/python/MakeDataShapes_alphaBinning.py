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

CUTS = [0.25, 1.5, 0.9, 0.1] #Loose 1
#CUTS = [0.5, 2.5, 0.9, 0.1] #Loose 2
#CUTS = [0.5, 3.5, 0.5, 0.1] #Loose 3 ALSO CHANGED PT CUT IN PLOTTING PAYLOAD

print("VERIFY CUTS: ")
print("masym < {}, deta < {}, dipho > {}, isolation > {}".format(CUTS[0], CUTS[1], CUTS[2], CUTS[3]))

#################################################

AlphaBins = [
               0.003,
               0.00347, 
               0.00395,   
               0.00444, 
               0.00494, 
               0.00545, 
               0.00597, 
               0.0065, 
               0.00704, 
               0.00759, 
               0.00815, 
               #0.00872, 
               0.0093, 
               #0.00989, 
               0.01049, 
               #0.0111, 
               #0.01173, 
               #0.01237, 
               #0.01302, 
               #0.01368, 
               #0.01436,
               #0.01505, 
               #0.01575, 
               #0.01647, 
               #0.0172, 
               #0.01794, 
               #0.0187, 
               #0.01947, 
               #0.02026, 
               #0.02106, 
               #0.02188, 
               #0.02271, 
               #0.02356, 
               #0.02443, 
               #0.02531, 
               #0.02621, 
               #0.02713, 
               #0.02806, 
               #0.02901, 
               0.03]

#AlphaBins = [0.003, 0.03]

for abin_num in range(0,len(AlphaBins)-1):
#for abin_num in range(len(AlphaBins)-2, 13, -1):

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




