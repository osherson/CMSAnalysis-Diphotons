import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time
sys.path.append("../../.")
import PlottingPayload as PL
gROOT.SetBatch()

year = sys.argv[1]
xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"
const_alpha = True #Use this to get signals at one alpha val
this_alpha = 0.005 #Set this to the alpha you want. If const_alpha = False, this does nothing

def doOneInput(N, h, H, S, norm = False):
    toF = TFile("../inputs/Shapes_fromGen/{}/".format(year)+N+"/"+S+".root", "recreate")
    if norm:
        h.Scale(1./h.Integral())
    toF.cd()
    h.SetName(H)
    h.Write()
    toF.Write()
    toF.Save()
    toF.Close()

def doOneInputInterpo(N, h, H, S, norm = False):
    toF = TFile("../inputs/Shapes_fromInterpo/{}/".format(year)+N+"/"+S+".root", "recreate")
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

def SaveHists(N, sXr, sX1r, sXvAr, sX, sX1, dX, dX1, dXvA, sX1pu, sX1pd, sX1su, sX1sd):
    header = "../inputs/Shapes_fromGen/{}/".format(year)+N
    PL.MakeFolder(header)
    with open(N+".txt", 'w') as eff:
        E = sX1.GetEntries()
        G = lookup(N)
        print "eff ("+N+")---> " + str(float(E)/float(G))
        eff.write(str(float(E)/float(G)))
    os.system('mv ' + N + '.txt {}/.'.format(header))
    doOneInput(N, sX1, "h_AveDijetMass_1GeV", "Sig_nominal", True)
    doOneInput(N, sX1pu, "h_AveDijetMass_1GeV", "Sig_PU", True)
    doOneInput(N, sX1pd, "h_AveDijetMass_1GeV", "Sig_PD", True)
    doOneInput(N, sX1su, "h_AveDijetMass_1GeV", "Sig_SU", True)
    doOneInput(N, sX1sd, "h_AveDijetMass_1GeV", "Sig_SD", True)
    doOneInput(N, dX1, "data_XM1", "DATA")
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

def SaveHists_Interpo(N, sXr, sX1r, sX, sX1, dX, dX1, sX1pu, sX1pd, sX1su, sX1sd):
    PL.MakeFolder("../inputs/Shapes_fromInterpo/{}/".format(year)+N)
    txtfile = interp_directory + N + "/" + N.replace("A","phi").replace(".","p") + '.txt'
    os.system('cp ' + txtfile +  ' ../inputs/Shapes_fromInterpo/{}/'.format(year)+N+"/" + N.replace(".","p") + ".txt")

    doOneInputInterpo(N, sX1, "h_AveDijetMass_1GeV", "Sig_nominal", True)
    doOneInputInterpo(N, sX1pu, "h_AveDijetMass_1GeV", "Sig_PU", True)
    doOneInputInterpo(N, sX1pd, "h_AveDijetMass_1GeV", "Sig_PD", True)
    doOneInputInterpo(N, sX1su, "h_AveDijetMass_1GeV", "Sig_SU", True)
    doOneInputInterpo(N, sX1sd, "h_AveDijetMass_1GeV", "Sig_SD", True)
    doOneInputInterpo(N, dX1, "data_XM1", "DATA")
    AE = str(sX.Integral()/sXr.Integral())
    for h in [sXr, sX1r]:
        h.SetFillColor(0)
        h.SetLineColor(1)
    oF = TFile("../inputs/Shapes_fromInterpo/{}/".format(year)+N+"/PLOTS_"+N+".root", "recreate")
    sX.SetName(sX.GetName().replace("XrM","XM"))
    sX.Write()
    sX1.Write()
    dX.Write()
    dX1.Write()



################################################
#Get DATA
DATA = []
for ff in os.listdir(xaastorage):
  #if("Run" in ff and year in ff):
  if("Run" in ff and "20" in ff): #All Data
    DATA.append(os.path.join(xaastorage,ff))

print(DATA)
time.sleep(3)

#################################################
#Generated Signals 

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
CUTS = [1.0, 3.5, 0.9, 0.5] # masym eta dipho iso
for s in SignalsGenerated:
    ct += 1
    #if ct > 1: break
    print(s)

    #thisdir = "../inputs/Shapes_fromGen/{}/{}".format(year,s)
    #if(os.path.isdir(thisdir)): 
    #  print("{} already exists. Skipping".format(thisdir))
    #  continue

    (sXr, sX1r, sXvAr) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [0.,0.5], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
    lA = sXvAr.GetMean(2) - 3.*sXvAr.GetRMS(2)
    hA = sXvAr.GetMean(2) + 3.*sXvAr.GetRMS(2)
    (sXpu, sX1pu, sXvApu) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeightUp*weight*10.*5.99")
    (sXpd, sX1pd, sXvApd) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeightDown*weight*10.*5.99")
    (sX, sX1, sXvA) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
    (sXsu, sX1su, sXvAsu) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_scale_up", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "weight*10.*5.99")
    (sXsd, sX1sd, sXvAsd) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_scale_down", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "weight*10.*5.99")
    (dX, dX1, dXvA) = PL.GetDiphoShapeAnalysis(DATA, "pico_skim", "data", CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "1.")
    #(dX, dX1, dXvA) = PL.GetDiphoShapeAnalysis(DATA, "pico_skim", "data", CUTS[0], CUTS[1], CUTS[2], CUTS[3], [0.,0.5], "HLT_DoublePhoton", "1.")
    SaveHists(s, sXr, sX1r, sXvAr, sX, sX1, dX, dX1, dXvA, sX1pu, sX1pd, sX1su, sX1sd)

#Now loop through signals created by interpolater
interp_directory = "../inputs/Interpolations/{}/".format(year)
interp_signals = [dirs for subdir, dirs, files in os.walk(interp_directory)][0]
#interp_signals = ["X600A3"]
#interp_signals = ["X500A7"]
interp_signals = []
for sub, dirs, files in os.walk(interp_directory):
  for dd in dirs:
    thisxa = dd
    this_x = int(thisxa[1:thisxa.find("A")])
    this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
    if(const_alpha and this_phi / this_x != this_alpha or thisxa.replace(".","p") in SignalsGenerated.keys() ): continue
    interp_signals.append(thisxa)

print(interp_signals)
print(len(interp_signals))
ct = 0
for isig in interp_signals:
  if (ct % 100 == 0): print("Beginning Signal {} / {}".format(ct+1, len(interp_signals)))
  print(isig)
  ct += 1
  this_dir = interp_directory + isig +""
  #if(ct > 1): break

  print("{}/{}_nom.root".format(this_dir, isig.replace("A","phi")))

  nom_file = ROOT.TFile("{}/{}_nom.root".format(this_dir, isig.replace("A","phi")), "read")
  puUp_file = ROOT.TFile("{}/{}_nom_puUp.root".format(this_dir, isig.replace("A","phi")), "read")
  puDown_file = ROOT.TFile("{}/{}_nom_puDown.root".format(this_dir, isig.replace("A","phi")), "read")
  scale_up_file = ROOT.TFile("{}/{}_scale_up.root".format(this_dir, isig.replace("A","phi")), "read")
  scale_down_file = ROOT.TFile("{}/{}_scale_down.root".format(this_dir, isig.replace("A","phi")), "read")

  # Before 3 sigma alpha cut:
  sX1r = nom_file.Get("{}_XM_na".format(isig.replace("A","phi")))
  sXr = PL.RebinReso(sX1r)
  #After 3 sigma alpha cut
  sX1 = nom_file.Get("{}_XM".format(isig.replace("A","phi")))
  sX = PL.RebinReso(sX1)
  sX1pu = puUp_file.Get("{}_XM".format(isig.replace("A","phi")))
  sX1pd = puDown_file.Get("{}_XM".format(isig.replace("A","phi")))
  sX1su = scale_up_file.Get("{}_XM".format(isig.replace("A","phi")))
  sX1sd = scale_down_file.Get("{}_XM".format(isig.replace("A","phi")))

  #Before 3 sigma alpha cut
  sA1 = nom_file.Get("{}_alpha_na".format(isig.replace("A","phi")))
  sAr = PL.RebinReso_alpha(sA1)
  #Get alpha mean +/- 3 sigma for making data plots
  lA = sAr.GetMean() - 3.*sAr.GetRMS()
  hA = sAr.GetMean() + 3.*sAr.GetRMS()

  (dX, dX1, dXvA) = PL.GetDiphoShapeAnalysis(DATA, "pico_skim", "data", CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "1.")

  SaveHists_Interpo(isig, sXr, sX1r, sX, sX1, dX, dX1, sX1pu, sX1pd, sX1su, sX1sd)
