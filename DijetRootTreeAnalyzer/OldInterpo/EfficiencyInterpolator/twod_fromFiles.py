import numpy as np
import ROOT
from ROOT import *
from array import array
import os,sys

gROOT.SetBatch()

alphaBins = range(0,13+1)

gen_phis = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03]
want_alpha = 0.008

alphamin, alphamax = 0, 0.031
nalphas = int((alphamax - alphamin)//0.001 + 2)

xmin, xmax = 200, 3010
nxs = int((xmax-xmin)//10 + 1)

eff_dir = "./EfficiencyFiles"

hist_dic = {}
for abin in alphaBins:
  hist_dic[str(abin)] = ROOT.TH2D("{}".format(abin),"Efficiency, #alpha Bin {};X Mass;#alpha".format(abin), nxs, xmin, xmax, nalphas, alphamin, alphamax) 

for abin in alphaBins:
  for fil in os.listdir(eff_dir):
    if(not fil.startswith("alpha")): continue
    abin=str(abin)

    falpha, fabin = fil.split("_")[0],fil.split("_")[1]
    falpha = float(falpha[5:])
    fabin = fabin[8 : fabin.find(".")]

    if(fabin==abin):

      ff = open(os.path.join(eff_dir,fil), "r")
      for lin in ff.readlines():
        xmass = int(lin.split(",")[0])
        eff = float(lin.split(",")[1].rstrip())

        #range_file = open("{}/{}/{}/arange.txt".format(g_dir, abin, gf))
        #rr = range_file.readline().rstrip()
        #la = float(rr.split(",")[0])
        #ha = float(rr.split(",")[-1])
        #eff_file.close()
        #range_file.close()

        #print(xmass, phi, eff)
        hist_dic[abin].Fill(xmass, falpha, eff)

for (abin, thist) in hist_dic.items():
   c1 = TCanvas("c{}".format(abin), "c{}".format(abin), 600,600)
   c1.cd()
   thist.SetStats(0)
   #thist.SetTitle("Eff, Alpha Bin {}, {} < #alpha < {}".format(abin, la,ha))
   thist.Draw("colz")
   c1.Print("EffPlots/TwoD/alphabin{}.png".format(abin))
