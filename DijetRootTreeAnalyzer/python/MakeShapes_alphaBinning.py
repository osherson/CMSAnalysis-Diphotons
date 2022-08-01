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

#year = sys.argv[1]
year='2018'

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"
const_alpha = False #Use this to get signals at one alpha val
this_alpha = 0.005 #Set this to the alpha you want. If const_alpha = False, this does nothing

def doOneInput(N, sig, h, H, S, norm = False):
    toF = TFile("{}/../inputs/Shapes_fromGen/alphaBinning/{}/{}/{}.root".format(dir_path,N,sig,S), "recreate")
    if norm:
        h.Scale(1./h.Integral())
    toF.cd()
    h.SetName(H)
    h.Write()
    toF.Write()
    toF.Save()
    toF.Close()

def doOneInputInterpo(N, h, H, S, norm = False):
    toF = TFile("{}/../inputs/Shapes_fromInterpo/".format(dir_path)+N+"/"+S+".root", "recreate")
    if norm:
        h.Scale(1./h.Integral())
    toF.cd()
    h.SetName(H)
    h.Write()
    toF.Write()
    toF.Save()
    toF.Close()

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

def SaveHists(N, sig, sXr, sX1r, sXvAr, sX, sX1, dX, dX1, dXvA, sX1pu, sX1pd, sX1su, sX1sd):
    header = "{}/../inputs/Shapes_fromGen/alphaBinning/{}/{}/".format(dir_path,N,sig)
    PL.MakeFolder(header)
    with open(sig+".txt", 'w') as eff:
        E = sX1.GetEntries()
        G = lookup(sig)
        print "eff ("+sig+")---> " + str(float(E)/float(G))
        eff.write(str(float(E)/float(G)))
    os.system('mv ' + sig + '.txt {}/.'.format(header))
    doOneInput(N, sig, sX1, "h_AveDijetMass_1GeV", "Sig_nominal", True)
    doOneInput(N, sig, sX1pu, "h_AveDijetMass_1GeV", "Sig_PU", True)
    doOneInput(N, sig, sX1pd, "h_AveDijetMass_1GeV", "Sig_PD", True)
    doOneInput(N, sig, sX1su, "h_AveDijetMass_1GeV", "Sig_SU", True)
    doOneInput(N, sig, sX1sd, "h_AveDijetMass_1GeV", "Sig_SD", True)
    doOneInput(N, sig, dX1, "data_XM1", "DATA")
    AE = str(sX.Integral()/sXr.Integral())
    for h in [sXr, sX1r]:
        h.SetFillColor(0)
        h.SetLineColor(1)
    oF = TFile(header+"/PLOTS_"+N+".root", "recreate")
    sX.Write()
    sX1.Write()
    dX.Write()
    dX1.Write()
    PL.FindAndSetLogMax(sXr, dX)
    PL.FindAndSetLogMax(sX1r, dX1)
    for d in [dX, dX1]:
        d.SetTitle("#alpha window signal efficiency = " + AE)
        d.SetMarkerStyle(20)
        d.SetMarkerColor(1)
        d.SetLineColor(1)
        d.SetLineWidth(1)
        d.SetMarkerSize(0.4)
    L = TLegend(0.11,0.8,0.89,0.89)
    L.SetFillColor(0)
    L.SetLineColor(0)
    L.SetNColumns(2)
    L.AddEntry(dX, "data ("+str(dX.Integral())+" events)", "PL")
    L.AddEntry(sX, sig + " (10 fb)", "FL")
    C = TCanvas()
    C.cd()
    C.SetLogy(1)
    dX.Draw("e")
    sXr.Draw("samehist")
    sX.Draw("samehist")
    L.Draw("same")
    C.Print(header+"/sX.png")
    dX1.Draw("e")
    sX1r.Draw("samehist")
    sX1.Draw("samehist")
    L.Draw("same")
    C.Print(header+"/sX1M.png")
########### 
    lA = sXvAr.GetMean(2) - 3.*sXvAr.GetRMS(2)
    hA = sXvAr.GetMean(2) + 3.*sXvAr.GetRMS(2)

    xmin = 250
    xmax = sX1.GetBinLowEdge(sX1.GetNbinsX()-1)

    lLine = TLine(xmin, lA, xmax, lA)
    lLine.SetLineColor(ROOT.kRed)
    lLine.SetLineStyle(ROOT.kDashed)
    lLine.SetLineWidth(2)
    hLine = TLine(xmin, hA, xmax, hA)
    hLine.SetLineColor(ROOT.kRed)
    hLine.SetLineStyle(ROOT.kDashed)
    hLine.SetLineWidth(2)

    C.SetLogy(0)
    sXvAr.Draw("col")
    lLine.Draw("same")
    hLine.Draw("same")
    C.Print(header+"/sXvA.png")
############
    dXvA.Draw("col")
    lLine.Draw("same")
    hLine.Draw("same")
    C.Print(header+"/dXvA.png")
    oF.Write()
    oF.Save()
    oF.Close()


################################################
#Get DATA
DATA = []
for ff in os.listdir(xaastorage):
  #if("Run" in ff and year in ff): #one year data
  if("Run" in ff and "20" in ff): #All Run II Data
    DATA.append(os.path.join(xaastorage,ff))

#DATA = [DATA[-1]]
print(DATA)
time.sleep(1)

#Analysis Cuts
# masym, eta, dipho, iso
CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [0.25, 3.5, 0.9, 0.8] #Analysis Cuts

#################################################

AlphaBins = [
             0.0,
             0.00428571428571,
             0.00467532467532,
             0.00506493506494,
             0.005689655172413793,
             0.006379310344827587,
             0.00706896551724138,
             0.007758620689655172,
             0.008448275862068966,
             0.00935064935065,
             0.00974025974026,
             0.0101298701299,
             0.01120689655172414,
             0.011896551724137932,
             0.0128571428571,
             0.0139285714286,
             0.015,
#             0.01603448275862069,
#             0.016724137931034482,
#             0.017413793103448278,
#             0.01810344827586207,
#             0.0189795918367,
#             0.0195918367347,
#             0.0202040816327,
#             0.020862068965517244,
#             0.021551724137931036,
#             0.02224137931034483,
#             0.0232258064516,
#             0.0241935483871,
#             0.0251612903226,
             0.03
             ]


#Get signals for one x mass

genXs = [200,300,400,500,600,750,1000,1500,2000,3000]

xmass = 1000
if( len(sys.argv) >= 1):
  if("X" in sys.argv[1]):
    xmass = sys.argv[1]
    xmass = int(xmass[1:])

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

def getNearestAlpha(in_a):
  global g_alphas

  minDiff = 999
  ng = 0
  for ga in g_alphas:
    diff = abs(ga-in_a)
    if(diff < minDiff): 
      minDiff = diff
      ng = ga
  
  return ng


for abin_num in range(0,len(AlphaBins)-1):
  #if(abin_num > 0): break

  lA = AlphaBins[abin_num]
  hA = AlphaBins[abin_num+1]
  print("alpha bin: ")
  print("{}: {} - {}".format(abin_num, lA, hA))
  saveTree = False
  newd = "{}/../inputs/Shapes_fromGen/alphaBinning/{}/".format(dir_path,abin_num)
  PL.MakeFolder(newd)

  nearestAlpha = getNearestAlpha((lA+hA)/2)
  whichSig = SignalsGenerated[nearestAlpha][0].split("/")[-1]
  whichSig = whichSig[0 : whichSig.find("_")]
  PL.MakeFolder("{}{}/".format(newd,whichSig))
  rfile = open("{}{}/arange.txt".format(newd,whichSig),"w")
  rfile.write("{},{}".format(lA,hA))

  (sXr, sX1r, sXvAr) = PL.GetDiphoShapeAnalysis(SignalsGenerated[nearestAlpha], "pico_nom", str(abin_num), CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
  print("Signal Entries: {}".format(sX1r.GetEntries()))

  (sXpu, sX1pu, sXvApu) = PL.GetDiphoShapeAnalysis(SignalsGenerated[nearestAlpha], "pico_nom", str(abin_num), CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeightUp*weight*10.*5.99")
  (sXpd, sX1pd, sXvApd) = PL.GetDiphoShapeAnalysis(SignalsGenerated[nearestAlpha], "pico_nom", str(abin_num), CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeightDown*weight*10.*5.99")
  (sX, sX1, sXvA) = PL.GetDiphoShapeAnalysis(SignalsGenerated[nearestAlpha], "pico_nom", str(abin_num), CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
  (sXsu, sX1su, sXvAsu) = PL.GetDiphoShapeAnalysis(SignalsGenerated[nearestAlpha], "pico_scale_up", str(abin_num), CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "weight*10.*5.99")
  (sXsd, sX1sd, sXvAsd) = PL.GetDiphoShapeAnalysis(SignalsGenerated[nearestAlpha], "pico_scale_down", str(abin_num), CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "weight*10.*5.99")
  (dX, dX1, dXvA) = PL.GetDiphoShapeAnalysis(DATA, "pico_skim", "data", CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "1.", saveTree, year+"/"+str(abin_num))

  print("Data Entries: {}".format(dX1.GetEntries()))

  SaveHists(str(abin_num), whichSig, sXr, sX1r, sXvAr, sX, sX1, dX, dX1, dXvA, sX1pu, sX1pd, sX1su, sX1sd)
