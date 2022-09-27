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

sigalpha = 0.02

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"

def lookup(N):
  ysum = 0
  for year in [2016, 2017, 2018]:
    LH = []
    f = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/Diphoton-Treemaker/HelperFiles/Signal_NEvents_{}.csv".format(year)
    r = open(f)
    for i in r.readlines():
      #print i
      LH.append(i.split(','))

    X = N.split('A')[0].split('X')[1]
    A = N.split('A')[1].replace('p', '.')
    for r in LH:
      if r[0] == X and r[1] == A: 
        print(year, r[2].rstrip())
        ysum += int(r[2].rstrip())
  print("Total Events: {}".format(ysum))
  return ysum

#Analysis Cuts
# masym, eta, dipho, iso
#CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [1.0, 3.5, 0.9, 0.8] #Loose
#CUTS = [0.25, 1.5, 0.9, 0.8] #Analysis Cuts
CUTS = [0.25, 1.5, 0.9, 0.1] #Loose Analysis Cuts

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
             0.00974,
             0.01012,
             0.01120,
             0.01189,
             0.01285,
             0.0139285714286,
             0.015,
             0.01603,
             0.01672,
             0.01741,
             0.01810,
             0.01897,
             0.01959,
             0.02020,
             0.02086,
             0.02155,
             0.02224,
             0.02322,
             0.02419,
             0.02516,
             0.03
             ]

#AlphaBins = [0.,0.03]
#AlphaBins = [0.00506,0.00568]

def getNearestAlpha(in_a, g_alphas):

  minDiff = 999
  ng = 0
  for ga in g_alphas:
    diff = abs(ga-in_a)
    if(diff < minDiff): 
      minDiff = diff
      ng = ga
  
  return ng


def CenterAlpha(ahist, t_alpha):
  newbins = numpy.linspace(-0.03, 0.03, 601)
  newhist = ROOT.TH1D(t_alpha, "{};{};{}".format(ahist.GetTitle(), ahist.GetXaxis().GetTitle(), ahist.GetYaxis.GetTitle()), len(newbins)-1, numpy.array(newbins))
  for bb in range(ahist.GetNBinsX()):
    newhist.SetBinContent(bb, ahist.GetBinContent(bb))
  return newhist.Clone()

print("Doing Generated Signals")

#Get signals for one x mass
genXs = [200,300,400,500,600,750,1000,1500,2000,3000]

SignalsGenerated = {}
for xx in genXs:
  SignalsGenerated[xx] = []

print("Using alpha = {} GeV Signals".format(sigalpha))
time.sleep(1)

for ff in os.listdir(xaastorage):
  if(ff[0]=="X"):
    thisxa = ff[ : ff.find("_")]
    this_x = int(thisxa[1:thisxa.find("A")])
    this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
    if(this_phi / this_x == sigalpha): 
      #SignalsGenerated[this_x] = [os.path.join(xaastorage, ff)]
      SignalsGenerated[this_x].append(os.path.join(xaastorage, ff))

g_xmasses = SignalsGenerated.keys()

hist_dic = {}

sigcount = 0
for thisSigIndex, oneSig in SignalsGenerated.items():
  #if(sigcount > 0): break
  sigcount += 1
  whichSig = oneSig[0][0 : oneSig[0].find("_")]
  whichSig = whichSig.split("/")[-1]

  thisX = int(whichSig[1 : whichSig.find("A")])
  thisPhi = float(whichSig[whichSig.find("A")+1 : ].replace("p","."))
  thisAlpha = thisPhi / thisX
  #if(whichSig != "X200A1"):continue
  if(thisX != 3000): continue
  
  print("Doing X {} Phi {} Signal".format(thisX, thisPhi))

  for abin_num in range(0,len(AlphaBins)-1):
    #if(abin_num != 3): continue

    lA = AlphaBins[abin_num]
    hA = AlphaBins[abin_num+1]
    if(lA > 1.5*thisAlpha): continue
    print("---------------------------------------------------------------------------")
    print("Alpha bin: ")
    print("{}: {} - {}".format(abin_num, lA, hA))
    saveTree = False

    (sXr, sX1r, sA1r, sXvAr) = PL.GetDiphoShapeAnalysisPlusAlpha(SignalsGenerated[thisSigIndex], thisAlpha, "pico_nom", str(abin_num), CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")

    sXr.SetName("XM")
    sX1r.SetName("XM1")
    sXvAr.SetName("XMvA")
    print("Signal sX1r Entries, Integral: {}, {}".format(sX1r.GetEntries(), sX1r.Integral()))

    n_postcut = float(sX1r.GetEntries())
    n_gen = float(lookup(whichSig))
    eff = n_postcut / n_gen * 100
    print("Efficiency: {:.3f} %".format(eff))
    if(eff < 5): continue

    hist_dic[abin_num] = (sX1r, sA1r, lA, hA, eff)

  cX = ROOT.TCanvas()
  if(thisX == 3000):
    xL = TLegend(0.10,0.50,0.47,0.89)
  else:
    xL = TLegend(0.60,0.50,0.87,0.89)
  xL.SetLineColor(0)
  xL.SetFillColor(0)
  xL.SetTextSize(0.04)
  #cA = ROOT.TCanvas()
  #aL = TLegend(0.68,0.60,0.89,0.89)
  #aL.SetLineColor(0)
  #aL.SetFillColor(0)

  colorlist = [2,4,7,8,9]

  xmax = 0
  amax = 0
  for alpha, (xhist, ahist, lA, hA, eff) in hist_dic.items():
    xhist.Scale(1/xhist.Integral())
    if(xhist.GetMaximum() > xmax): xmax = xhist.GetMaximum()
    ahist.Scale(1/ahist.Integral())
    if(ahist.GetMaximum() > amax): amax = ahist.GetMaximum()

  ii=0
  for aBin, (xhist, ahist, lowA, hiA, eff) in hist_dic.items():

    cX.cd()
    xhist.SetStats(0)
    xhist.SetLineColor(colorlist[ii]) 
    xhist.SetLineWidth(2)
    xhist.SetFillColor(0)
    xhist.GetXaxis().SetRangeUser(0.75*thisX, 1.25*thisX)
    xhist.GetYaxis().SetRangeUser(0,xmax * 1.15)
    xhist.GetYaxis().SetTitle("Normalized Entries")
    xhist.SetTitle("{} Signals, X Mass Shape".format(whichSig))

    xL.AddEntry(xhist, "{}<#alpha<{}".format(lowA, hiA, eff))
    if(ii==0): xhist.Draw("hist")
    else: xhist.Draw("histsame")

#    cA.cd()
#    ahist.SetStats(0)
#    ahist.SetLineColor(colorlist[ii]) 
#    ahist.SetLineWidth(2)
#    ahist.SetFillColor(0)
#    ahist.GetXaxis().SetRangeUser(-0.015, 0.015)
#    ahist.GetYaxis().SetRangeUser(0,amax * 1.15)
#    ahist.GetYaxis().SetTitle("Normalized Entries")
#    ahist.GetXaxis().SetTitle("#alpha - #alpha_{gen}")
#    ahist.SetTitle("X {} Signals, #alpha Shape".format(xmass))
#
#    aL.AddEntry(ahist, "#alpha={}".format(alpha))
#    if(ii==0): ahist.Draw("hist")
#    else: ahist.Draw("histsame")

    ii += 1

  cX.cd()
  xL.Draw("same")
  cX.Print("Plots/OneSig/shape_{}_xmass.png".format(whichSig))
  #cA.cd()
  #aL.Draw("same")
  #cA.Print("Plots/OneSig/shape_X{}_alpha.png".format(xmass))

