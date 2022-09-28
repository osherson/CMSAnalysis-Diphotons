import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time
from array import array

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../../.")
import PlottingPayload as PL
#gROOT.SetBatch()

year='2018'
xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"

LH = []
f = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/Diphoton-Treemaker/HelperFiles/Signal_NEvents_{}.csv".format(year)
r = open(f)
for i in r.readlines():
    #print i
    LH.append(i.split(','))

def lookup(N):
    X = N.split('A')[0].split('X')[1]
    A = N.split('A')[1].replace('p', '.')
    for r in LH:
        if r[0] == X and r[1] == A: return r[2]


#Analysis Cuts
# masym, eta, dipho, iso
#CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [1.0, 3.5, 0.9, 0.8] #Loose
#CUTS = [0.25, 1.5, 0.9, 0.8] #Analysis Cuts

CUTS = [0.25, 1.5, 0.9, 0.1] #Loose Analysis Cuts
#CUTS = [1.0, 3.5, 0.0, 0.0] 

#################################################

AlphaBins = [
             0.0,
             0.00428,
             0.00467,
             0.00506,
             0.00568,
             0.00637,
             0.00706,
             0.00775,
             0.00844,
             0.00935,
#             0.00974,
#             0.01012,
#             0.01120,
#             0.01189,
#             0.01285,
#             0.0139285714286,
#             0.015,
#             0.01603,
#             0.01672,
#             0.01741,
#             0.01810,
#             0.01897,
#             0.01959,
#             0.02020,
#             0.02086,
#             0.02155,
#             0.02224,
#             0.02322,
#             0.02419,
#             0.02516,
             0.03
             ]

#AlphaBins = [0.,0.03]

def getNearestAlpha(in_a, g_alphas):

  minDiff = 999
  ng = 0
  for ga in g_alphas:
    diff = abs(ga-in_a)
    if(diff < minDiff):
      minDiff = diff
      ng = ga

  return ng


#Get signals for one x mass
genXs = [300,400,500,600,750,1000,1500,2000,3000]
gen_alphas = [0.005, 0.01, 0.015, 0.02, 0.025]
#genXs = [300]

for abin_num in range(0,len(AlphaBins)-1):
  effs = []
  xms = []
  #if(abin_num != 4): continue
  lA = AlphaBins[abin_num]
  hA = AlphaBins[abin_num+1]
  print("---------------------------------------------------------------------------")
  print("Alpha bin: ")
  print("{}: {} - {}".format(abin_num, lA, hA))

  nearestAlpha = getNearestAlpha((lA+hA)/2, gen_alphas)
  print(nearestAlpha)

  SignalsGenerated = {}
  for xmass in genXs:
    for ff in os.listdir(xaastorage):
      if(ff[0]=="X" and "X{}A".format(xmass) in ff and year in ff):
        thisxa = ff[ : ff.find("_")]
        this_x = int(thisxa[1:thisxa.find("A")])
        this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
        #if(this_phi / this_x > 0.026): continue
        if(this_phi / this_x != nearestAlpha): continue
        #SignalsGenerated[this_phi/this_x] = [os.path.join(xaastorage, ff)]
        SignalsGenerated[this_x] = [os.path.join(xaastorage, ff)]

  newd = "{}/../inputs/Shapes_fromGen/alphaBinning/{}/".format(dir_path,abin_num)
  PL.MakeFolder(newd)

  for thisSigIndex, oneSig in SignalsGenerated.items():
    whichSig = oneSig[0][0 : oneSig[0].find("_")]
    whichSig = whichSig.split("/")[-1]
    wx = int(whichSig[1 : whichSig.find("A")])
    #wp = float(whichSig[whichSig.find("A")+1 :].replace("p","."))
    #wa = wp/wx
    #if(wa != nearestAlpha):
    #  continue

    print("\nSignal: {}".format(whichSig))
    PL.MakeFolder("{}{}/".format(newd,whichSig))
    rfile = open("{}{}/arange.txt".format(newd,whichSig),"w")
    rfile.write("{},{}".format(lA,hA))

    (sXr, sX1r, sXvAr) = PL.GetDiphoShapeAnalysis(SignalsGenerated[thisSigIndex], "pico_nom", str(abin_num), CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
    print("Signal sX1r Entries, Integral: {}, {}".format(sX1r.GetEntries(), sX1r.Integral()))

    if(sX1r.GetEntries()<100 or sXr.GetEntries() < 100): 
      print("skipping, too few events")
      continue
    if(sX1r.Integral()<0.00001 or sXr.Integral() < 0.00001): 
      print("Skipping, Integral = 0")
      continue

    (sX, sX1, sXvA) = PL.GetDiphoShapeAnalysis(SignalsGenerated[thisSigIndex], "pico_nom", str(abin_num), CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
    n_postcut = float(sX1r.GetEntries())
    n_gen = float(lookup(whichSig))
    eff = n_postcut / n_gen * 100

    effs.append(eff)
    xms.append(wx)
    continue

  if(len(effs) < 1):continue
  for xx,ee in zip(xms, effs):
    print(xx,ee)

  c1 = ROOT.TCanvas( 'c1', '', 200, 10, 700, 500 )
  c1.cd()
  gr = ROOT.TGraph( len(effs), array("d", xms), array("d",effs) )
  gr.SetLineColor( 2 )
  gr.SetLineWidth( 4 )
  gr.SetMarkerColor( 2 )
  gr.SetMarkerStyle( 20 )
  gr.SetTitle( 'Efficiency' )
  gr.GetXaxis().SetTitle( 'X Mass (GeV)' )
  gr.GetYaxis().SetTitle( 'Efficiency (%)' )
  gr.Draw( 'AP' )
  c1.Print("tmp.png")
