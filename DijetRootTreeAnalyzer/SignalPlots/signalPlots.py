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

year='2018'

#xmass = 1000
if( len(sys.argv) >= 1):
  if("X" in sys.argv[1]):
    xmass = sys.argv[1]
    xmass = int(xmass[1:])

#print(xmass)

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"
const_alpha = False #Use this to get signals at one alpha val
this_alpha = 0.005 #Set this to the alpha you want. If const_alpha = False, this does nothing


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

AlphaBins = [0.,0.03]

def getNearestAlpha(in_a, g_alphas):

  minDiff = 999
  ng = 0
  for ga in g_alphas:
    diff = abs(ga-in_a)
    if(diff < minDiff): 
      minDiff = diff
      ng = ga
  
  return ng

def SaveHists(N, sig, sXr, sX1r, sXvAr):
  header = "{}/Plots/{}/".format(dir_path, sig)
  PL.MakeFolder(header)
  with open(sig+".txt", 'w') as eff:
      E = sX1r.GetEntries()
      G = lookup(sig)
      print "eff ("+sig+")---> " + str(float(E)/float(G))
      eff.write(str(float(E)/float(G)))
  os.system('mv ' + sig + '.txt {}/.'.format(header))
  for h in [sXr, sX1r]:
      h.SetFillColor(0)
      h.SetLineColor(1)
  for h in [sXr, sX1r, sXvAr]:
      h.SetTitle(sig)
  oF = TFile(header+"/PLOTS_"+N+".root", "recreate")
  sXr.Write()
  sX1r.Write()
  sXvAr.Write()
  oF.Close()

  return

def CenterAlpha(ahist, t_alpha):
  newbins = numpy.linspace(-0.03, 0.03, 601)
  newhist = ROOT.TH1D(t_alpha, "{};{};{}".format(ahist.GetTitle(), ahist.GetXaxis().GetTitle(), ahist.GetYaxis.GetTitle()), len(newbins)-1, numpy.array(newbins))

  for bb in range(ahist.GetNBinsX()):
    newhist.SetBinContent(bb, ahist.GetBinContent(bb))

  return newhist.Clone()


print("Doing Generated Signals")

#Get signals for one x mass
genXs = [200,300,400,500,600,750,1000,1500,2000,3000]

if(xmass not in genXs):
  print("Not a generated X Mass. Quitting")
  exit()

print("Using X = {} GeV Signals".format(xmass))
time.sleep(1)

SignalsGenerated = {}
for ff in os.listdir(xaastorage):
  if(ff[0]=="X" and "X{}A".format(xmass) in ff and year in ff):
    thisxa = ff[ : ff.find("_")]
    this_x = int(thisxa[1:thisxa.find("A")])
    this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
    if(this_phi / this_x > 0.026): continue
    SignalsGenerated[this_phi/this_x] = [os.path.join(xaastorage, ff)]

g_alphas = SignalsGenerated.keys()

hist_dic = {}
for abin_num in range(0,len(AlphaBins)-1):
  #if(abin_num != 3): continue

  lA = AlphaBins[abin_num]
  hA = AlphaBins[abin_num+1]
  print("---------------------------------------------------------------------------")
  print("Alpha bin: ")
  print("{}: {} - {}".format(abin_num, lA, hA))
  saveTree = False
  newd = "{}/../inputs/Shapes_fromGen/alphaBinning/{}/".format(dir_path,abin_num)
  PL.MakeFolder(newd)

  nearestAlpha = getNearestAlpha((lA+hA)/2, g_alphas)

  sigcount = 0
  for thisSigIndex, oneSig in SignalsGenerated.items():
    #if(sigcount > 1): break
    sigcount += 1
    whichSig = oneSig[0][0 : oneSig[0].find("_")]
    whichSig = whichSig.split("/")[-1]

    thisX = int(whichSig[1 : whichSig.find("A")])
    thisPhi = float(whichSig[whichSig.find("A")+1 : ].replace("p","."))
    thisAlpha = thisPhi / thisX
    #if(whichSig != "X200A1"):continue

    print("\nSignal: {}".format(whichSig))

    (sXr, sX1r, sA1r, sXvAr) = PL.GetDiphoShapeAnalysisPlusAlpha(SignalsGenerated[thisSigIndex], thisAlpha, "pico_nom", str(abin_num), CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")

    sXr.SetName("XM")
    sX1r.SetName("XM1")
    sXvAr.SetName("XMvA")
    print("Signal sX1r Entries, Integral: {}, {}".format(sX1r.GetEntries(), sX1r.Integral()))

    n_postcut = float(sX1r.GetEntries())
    n_gen = float(lookup(whichSig))
    eff = n_postcut / n_gen * 100
    if(eff < 10):
      print("Efficiency is {:.3f} %, skipping signal".format(eff))
      continue
    else:
      print("Efficiency: {:.3f} %".format(eff))

    hist_dic[thisAlpha] = (sX1r, sA1r)

    SaveHists(str(abin_num), whichSig, sXr, sX1r, sXvAr)

cX = ROOT.TCanvas()
xL = TLegend(0.68,0.60,0.89,0.89)
xL.SetLineColor(0)
xL.SetFillColor(0)
cA = ROOT.TCanvas()
aL = TLegend(0.68,0.60,0.89,0.89)
aL.SetLineColor(0)
aL.SetFillColor(0)

colorlist = [2,4,7,8,9]

xmax = 0
amax = 0
for alpha, (xhist, ahist) in hist_dic.items():
  xhist.Scale(1/xhist.Integral())
  if(xhist.GetMaximum() > xmax): xmax = xhist.GetMaximum()
  ahist.Scale(1/ahist.Integral())
  if(ahist.GetMaximum() > amax): amax = ahist.GetMaximum()

ii=0
for alpha, (xhist, ahist) in hist_dic.items():

  cX.cd()
  xhist.SetStats(0)
  xhist.SetLineColor(colorlist[ii]) 
  xhist.SetLineWidth(2)
  xhist.GetXaxis().SetRangeUser(0.75*xmass, 1.25*xmass)
  xhist.GetYaxis().SetRangeUser(0,xmax * 1.15)
  xhist.GetYaxis().SetTitle("Normalized Entries")
  xhist.SetTitle("X {} Signals, X Mass Shape".format(xmass))

  xL.AddEntry(xhist, "#alpha={}".format(alpha))
  if(ii==0): xhist.Draw("hist")
  else: xhist.Draw("histsame")

  cA.cd()
  ahist.SetStats(0)
  ahist.SetLineColor(colorlist[ii]) 
  ahist.SetLineWidth(2)
  ahist.SetFillColor(0)
  ahist.GetXaxis().SetRangeUser(-0.015, 0.015)
  ahist.GetYaxis().SetRangeUser(0,amax * 1.15)
  ahist.GetYaxis().SetTitle("Normalized Entries")
  ahist.GetXaxis().SetTitle("#alpha - #alpha_{gen}")
  ahist.SetTitle("X {} Signals, #alpha Shape".format(xmass))

  aL.AddEntry(ahist, "#alpha={}".format(alpha))
  if(ii==0): ahist.Draw("hist")
  else: ahist.Draw("histsame")

  ii += 1

cX.cd()
xL.Draw("same")
cX.Print("Plots/shape_X{}_xmass.png".format(xmass))
cA.cd()
aL.Draw("same")
cA.Print("Plots/shape_X{}_alpha.png".format(xmass))

