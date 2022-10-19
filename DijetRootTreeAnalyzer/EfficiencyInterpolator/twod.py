import numpy as np
import ROOT
from ROOT import *
from array import array
import os,sys

gROOT.SetBatch()

g_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning/"

alphaBins = range(0,14+1)

gen_phis = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03]
want_alpha = 0.008

alphamin, alphamax = 0, 0.031
nalphas = int((alphamax - alphamin)//0.001 + 2)

xmin, xmax = 200, 3010
nxs = int((xmax-xmin)//10 + 1)

for abin in alphaBins:
  #if(abin != 3): continue
  abin=str(abin)
  #thist = ROOT.TH2D("{}".format(abin),"Efficiency;X Mass;#alpha",  len(xlist)-1, xlist, len(alphalist)-1, alphalist)
  thist = ROOT.TH2D("{}".format(abin),"Efficiency;X Mass;#alpha".format(abin), nxs, xmin, xmax, nalphas, alphamin, alphamax) 
  for gf in os.listdir(os.path.join(g_dir, abin)):
      xmass = int(gf[1 : gf.find("A")])
      amass = float(gf[gf.find("A")+1 :].replace("p","."))
      phi = amass / xmass
      eff_file = open("{}/{}/{}/{}.txt".format(g_dir, abin, gf, gf))
      eff = float(eff_file.readline().rstrip())
      range_file = open("{}/{}/{}/arange.txt".format(g_dir, abin, gf))
      rr = range_file.readline().rstrip()
      la = float(rr.split(",")[0])
      ha = float(rr.split(",")[-1])
      eff_file.close()
      range_file.close()

      #print(xmass, phi, eff)
      thist.Fill(xmass, phi, eff)

  c1 = TCanvas("c{}".format(abin), "c{}".format(abin), 600,600)
  c1.cd()
  thist.SetStats(0)
  thist.SetTitle("Eff, Alpha Bin {}, {} < #alpha < {}".format(abin, la,ha))
  thist.Draw("colz")
  c1.Print("EffPlots/TwoD/alphabin{}.png".format(abin))
