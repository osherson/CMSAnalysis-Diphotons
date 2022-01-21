import ROOT
from ROOT import *
import numpy
import os
import math
import sys
sys.path.append("../../.")
import PlottingPayload as PL
#gROOT.SetBatch()

def SaveHists(N, sXr, sX1r, sXvAr, sX, sX1, dX, dX1, dXvA):
    AE = str(sX.Integral()/sXr.Integral())
    for h in [sXr, sX1r]:
        h.SetFillColor(0)
        h.SetLineColor(1)
    PL.MakeFolder("../inputs/"+N)
    oF = TFile("../inputs/"+N+"/PLOTS_"+N+".root", "recreate")
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
    C.Print("../inputs/"+N+"/sX.png")
    dX1.Draw("e")
    sX1r.Draw("samehist")
    sX1.Draw("samehist")
    L.Draw("same")
    C.Print("../inputs/"+N+"/sX1M.png")
    C.SetLogy(0)
    sXvAr.Draw("col")
    C.Print("../inputs/"+N+"/sXvA.png")
    dXvA.Draw("col")
    C.Print("../inputs/"+N+"/dXvA.png")
    oF.Write()
    oF.Save()
    oF.Close()

### PICOTREE DIRECTORIES ###
DATA = ["/cms/xaastorage-2/DiPhotonsTrees/Run_D_2018.root", "/cms/xaastorage-2/DiPhotonsTrees/Run_C_2018.root","/cms/xaastorage-2/DiPhotonsTrees/Run_B_2018.root", "/cms/xaastorage-2/DiPhotonsTrees/Run_A_2018.root"]
SignalsGenerated = {}
SignalsGenerated["X600A3"] = ["/cms/xaastorage-2/DiPhotonsTrees/X600A3_2018.root"]
CUTS = [0.25, 3.5, 0.0, 0.5] # masym eta dipho iso
for s in SignalsGenerated:
    (sXr, sX1r, sXvAr) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [0.,0.5], "HLT_DoublePhoton", 10.*5.99)
    lA = sXvAr.GetMean(2) - 3.*sXvAr.GetRMS(2)
    hA = sXvAr.GetMean(2) + 3.*sXvAr.GetRMS(2)
    (sX, sX1, sXvA) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", 10.*5.99)
    (dX, dX1, dXvA) = PL.GetDiphoShapeAnalysis(DATA, "pico_skim", "data", CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", 1)
    SaveHists(s, sXr, sX1r, sXvAr, sX, sX1, dX, dX1, dXvA)