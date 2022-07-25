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
#gROOT.SetBatch()

year = 2018
igen = "g"

try: signalMass = sys.argv[3] #signal mass point, XxxxAaaa, only use for interpolated
except IndexError: print("Getting all generated signal shapes")

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"
const_alpha = False #Use this to get signals at one alpha val


################################################

#Analysis Cuts
# masym, eta, dipho, iso
CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [0.25, 3.5, 0.9, 0.8] #Analysis Cuts

xaa = TH2D("twod","M_{#phi} vs. M_{X} vs. #alpha", 3100,0,3100, 40,0,40)
alpha = TH1D("alph","#alpha_{RMS} per alpha",31,0,0.03)

#################################################
#Generated Signals 
if(igen == "g"):

  SignalsGenerated = {}
  #SignalsGenerated["X300A1p5"] = ["/cms/xaastorage-2/DiPhotonsTrees/X300A1p5_{}.root".format(year)]

  #Get all signals
  for ff in os.listdir(xaastorage):
    if(ff[0]=="X" and str(year) in ff and "X200A" not in ff):
      thisxa = ff[ : ff.find("_")]
      this_x = int(thisxa[1:thisxa.find("A")])
      this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
      if(const_alpha and this_phi / this_x != this_alpha): continue
      SignalsGenerated[thisxa] = [os.path.join(xaastorage, ff)]


  ct = 0
  for s in SignalsGenerated:
    ct += 1
    saveTree = False
    thisx = int(s[1 : s.find("A")])
    thisphi = float(s[s.find("A")+1 :].replace("p","."))

    #if(thisx > 301): continue

    (sXr, sX1r, sXvAr) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [0.,0.5], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
    alphaRMS = sXvAr.GetRMS(2)

    print(thisx, thisphi, alphaRMS)

    xaa.Fill(thisx, thisphi, alphaRMS)
    alpha.Fill(thisphi/thisx, alphaRMS)

outfile = TFile("alphaplot.root","RECREATE")
outfile.cd()
alpha.GetXaxis().SetTitle("#alpha")
alpha.GetYaxis().SetTitle("#alpha_{RMS}")
alpha.Write()
outfile.Close()

c1 = TCanvas("c","c",800,600)
c1.cd()
alpha.Draw("e")
c1.Print("alphaplot.png")
 
  
   

    
