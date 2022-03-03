import ROOT
from ROOT import *
import numpy
import math
import sys
import array
import os
import random
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import time

ts = time.time()

#ROOT.ROOT.EnableImplicitMT()

ROOT.gROOT.SetBatch(ROOT.kTRUE)
RDF = ROOT.ROOT.RDataFrame

nbins = 100

year = sys.argv[1]
alpha_high = 100

folder = "/cms/xaastorage-2/DiPhotonsTrees/"

##
#Get Signal Files
sChain = TChain("pico_nom")
ct=0
for path, subdirs, files in os.walk(folder):
  for name in files:
    File = os.path.join(path, name)
    if name[0]=="X" and year in name:
      xamass = name[:name.find("_")]
      xmass = int(xamass[1 : xamass.find("A")])
      amass = float(xamass[xamass.find("A")+1 :].replace("p",".") )

      if (File.endswith(".root") and amass/xmass <= alpha_high and "v_" not in path):
        if(os.path.getsize(File) > 100):
          #if(ct < 10):
            print os.path.join(path, name)
            sChain.Add(File)
          #ct+=1

##

print("\nGetting Data Files")
#Get Data Files
dChain = TChain("pico_full")
ct=0
for path, subdirs, files in os.walk(folder):
  for name in files:
    File = os.path.join(path, name)
    #if "Run" in name and year in name and File.endswith(".root") and "v_" not in path:
    if "Run" in name and "Run_D" not in name and year in name and File.endswith(".root") and "v_" not in path:
    #if "Run_A" in name and year in name and File.endswith(".root") and "v_" not in path:
      print os.path.join(path, name)
      dChain.Add(File)


if(year=="16"): year=2016
elif(year=="17"): year=2017
elif(year=="18"): year=2018

sRdf = RDF(sChain)
dRdf = RDF(dChain)

#Rdf = Rdf.Filter("clu1_pt > 90 && clu2_pt > 90","pt cut")

nbins=75

snpv_hist = sRdf.Histo1D( ("npv_signal", "N Primary Vertices; npvt; entries", nbins,0,nbins-1), "pvtx_size")
dnpv_hist = dRdf.Histo1D( ("npv_data", "N Primary Vertices; npvt; events", nbins,0,nbins-1), "pvtx_size")

srep = sRdf.Report()
srep.Print()

histlist = [
  snpv_hist,
  dnpv_hist,
]

if not os.path.exists("outFiles/{}".format(year)):
  os.makedirs("outFiles/{}".format(year))

if not ( os.path.exists("Plots/{}".format(year)) ):
  os.makedirs("Plots/{}".format(year))

oFname = "outFiles/{}/vertices.root".format(year)
oF = TFile(oFname, "recreate")
oF.cd()

for hist in histlist:
  hist.Write()
  c1 = TCanvas()
  if(type(hist) == ROOT.TH2D ): 
    hist.Draw("colz")
  else: 
    hist.Draw("hist")
  c1.Print("Plots/{}/{}.png".format(year,hist.GetName()))

oF.Write()
oF.Save()
oF.Close()

print("\nSaving output as {}".format(oFname))

