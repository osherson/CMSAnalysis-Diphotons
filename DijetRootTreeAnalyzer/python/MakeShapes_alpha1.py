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

year = sys.argv[1]
igen = "g"

try: signalMass = sys.argv[3] #signal mass point, XxxxAaaa, only use for interpolated
except IndexError: print("Getting all generated signal shapes")

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"
const_alpha = False #Use this to get signals at one alpha val
this_alpha = 0.01 #Set this to the alpha you want. If const_alpha = False, this does nothing

def doOneInput(N, h, H, S, aidx, norm = False):
    toF = TFile("{}/../inputs/Shapes_fromGen/alpha1/{}{}/".format(dir_path,aidx,N)+S+".root", "recreate")
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

def SaveHists(N, lA, hA, abinidx, sXr, sX1r, sXvAr, sX, sX1, dX, dX1, dXvA, sX1pu, sX1pd, sX1su, sX1sd):
    header = "{}/../inputs/Shapes_fromGen/alpha1/{}".format(dir_path,abinidx)+N
    PL.MakeFolder(header)
    with open(N+".txt", 'w') as eff:
        E = sX1.GetEntries()
        G = lookup(N)
        print "eff ("+N+")---> " + str(float(E)/float(G))
        eff.write(str(float(E)/float(G)))
    with open("range.txt", 'w') as rg:
        rg.write("{},{}".format(lA,hA))
    os.system('mv ' + N + '.txt {}/.'.format(header))
    os.system('mv range.txt {}/.'.format(header))
    doOneInput(N, sX1, "h_AveDijetMass_1GeV", "Sig_nominal", abinidx, True)
    doOneInput(N, sX1pu, "h_AveDijetMass_1GeV", "Sig_PU", abinidx, True)
    doOneInput(N, sX1pd, "h_AveDijetMass_1GeV", "Sig_PD", abinidx, True)
    doOneInput(N, sX1su, "h_AveDijetMass_1GeV", "Sig_SU", abinidx, True)
    doOneInput(N, sX1sd, "h_AveDijetMass_1GeV", "Sig_SD", abinidx, True)
    doOneInput(N, dX1, "data_XM1", "DATA", abinidx,)
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
    L.AddEntry(sX, s + " (10 fb)", "FL")
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

print(DATA)
time.sleep(3)

#Analysis Cuts
# masym, eta, dipho, iso
CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [0.25, 3.5, 0.9, 0.8] #Analysis Cuts

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
    if s=="X600A3": 
    #if s=="X1000A10": 
      saveTree=False
    else: continue
    #if ct > 1: break
    print(s)

    (sXr, sX1r, sXvAr) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [0.,0.5], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
    alphaRMS = sXvAr.GetRMS(2)
    print(alphaRMS)

    lA = 0
    hA = 2*alphaRMS

    alphaBin=0

    while lA < 0.03:
      print("Beginning alpha window {} - {}".format(lA, hA))

      (sXpu, sX1pu, sXvApu) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeightUp*weight*10.*5.99")
      
      (sXpd, sX1pd, sXvApd) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeightDown*weight*10.*5.99")
      (sX, sX1, sXvA) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
      print("SIGNAL N Events: {}".format(sX.GetEntries()))
      print("SIGNAL SX1 Integral : {}".format(sX1.Integral()))
      if(sX.GetEntries() == 0 or sX1.GetEntries() == 0 or sX1.Integral() < 0.001): 
        print("No Signal")
        lA = hA
        hA += 2*alphaRMS
        alphaBin += 1
        continue

      (sXsu, sX1su, sXvAsu) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_scale_up", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "weight*10.*5.99")
      (sXsd, sX1sd, sXvAsd) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_scale_down", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "weight*10.*5.99")
      (dX, dX1, dXvA) = PL.GetDiphoShapeAnalysis(DATA, "pico_skim", "data", CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "1.", saveTree, year+"/"+s)
      print("DATA N Events: {}".format(dX.GetEntries()))
      print("DATA SX1 Integral : {}".format(dX1.Integral()))
      #(dX, dX1, dXvA) = PL.GetDiphoShapeAnalysis(DATA, "pico_skim", "data", CUTS[0], CUTS[1], CUTS[2], CUTS[3], [0.,0.5], "HLT_DoublePhoton", "1.")
      lA = hA
      hA += 2*alphaRMS
      alphaBin += 1

      SaveHists(s, lA, hA, alphaBin, sXr, sX1r, sXvAr, sX, sX1, dX, dX1, dXvA, sX1pu, sX1pd, sX1su, sX1sd)
