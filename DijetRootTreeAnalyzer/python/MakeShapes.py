import ROOT
from ROOT import *
import numpy
import os
import math
import sys
sys.path.append("../../.")
import PlottingPayload as PL
#gROOT.SetBatch()

def SaveHists(N, sXr, sX1r, sXvAr, sX, sX1):
    AE = str(sX.Integral()/sXr.Integral())
    for h in [sXr, sX1r]:
        h.SetTitle("efficiency = " + AE)
        h.SetFillColor(0)
        h.SetLineColor(1)
    PL.MakeFolder("../inputs/"+N)
    oF = TFile("../inputs/"+N+"/PLOTS_"+N+".root", "recreate")
    sX.Write()
    sX1.Write()
    sXvAr.Write()

    C = TCanvas()
    C.cd()
    C.SetLogy(1)
    sXr.Draw("hist")
    sX.Draw("samehist")
    C.Print("../inputs/"+N+"/sX.png")
    sX1r.Draw("hist")
    sX1.Draw("samehist")
    C.Print("../inputs/"+N+"/sX1M.png")
    C.SetLogy(0)
    sXvAr.Draw("col")
    C.Print("../inputs/"+N+"/sXvA.png")
    oF.Write()
    oF.Save()
    oF.Close()

### PICOTREE DIRECTORIES ###
SignalsGenerated = {}
SignalsGenerated["X600A3"] = "/cms/xaastorage-2/DiPhotonsTrees/X600A3_2018.root"

for s in SignalsGenerated:
    (sXr, sX1r, sXvAr) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, 0.25, 3.5, 0.9, 0.8, [0.,0.5], "HLT_DoublePhoton")
    lA = sXvAr.GetMean(2) - 3.*sXvAr.GetRMS(2)
    hA = sXvAr.GetMean(2) + 3.*sXvAr.GetRMS(2)
    (sX, sX1, sXvA) = PL.GetDiphoShapeAnalysis(SignalsGenerated[s], "pico_nom", s, 0.25, 3.5, 0.9, 0.8, [lA,hA], "HLT_DoublePhoton")
    SaveHists(s, sXr, sX1r, sXvAr, sX, sX1)