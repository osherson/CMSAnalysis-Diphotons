#
import ROOT
RDF = ROOT.ROOT.RDataFrame
ROOT.ROOT.EnableImplicitMT()
##ROOT.gROOT.SetBatch(ROOT.kTRUE)
from ROOT import *
import sys,os
import glob
import time

infile = "GJetsFiles/gjets_Run2_match.root"
inf = ROOT.TFile(infile, "read")

passhist =inf.Get("mass").Clone()
failhist =inf.Get("fail").Clone()

def AddCMSLumi(pad, fb, extra):
  cmsText     = "CMS " + extra
  cmsTextFont   = 61
  lumiTextSize     = 0.45
  lumiTextOffset   = 0.15
  cmsTextSize      = 0.5
  cmsTextOffset    = 0.15
  H = pad.GetWh()
  W = pad.GetWw()
  l = pad.GetLeftMargin()
  t = pad.GetTopMargin()
  r = pad.GetRightMargin()
  b = pad.GetBottomMargin()
  e = 0.025
  pad.cd()
  lumiText = str(fb)+" fb^{-1} (13 TeV)"
  latex = TLatex()
  latex.SetNDC()
  latex.SetTextAngle(0)
  latex.SetTextColor(kBlack)
  extraTextSize = 0.76*cmsTextSize
  latex.SetTextFont(42)
  latex.SetTextAlign(31)
  latex.SetTextSize(lumiTextSize*t)
  latex.DrawLatex(1-r,1-t+lumiTextOffset*t,lumiText)
  pad.cd()
  latex.SetTextFont(cmsTextFont)
  latex.SetTextSize(cmsTextSize*t)
  latex.SetTextAlign(11)
  latex.DrawLatex(0.6265, 0.825, cmsText)
  pad.Update()

dataScale = 136.1
fb = dataScale
fb = round(fb,1)

etamass = 0.548

##
lheight = passhist.GetBinContent(passhist.FindBin(etamass))
L = TLine(etamass, 0, etamass, lheight)
L.SetLineColor(4)
L.SetLineStyle(2)
L.SetLineWidth(2)

passhist.SetLineWidth(3)
passhist.SetLineColor(30)
passhist.SetStats(0)

cp = ROOT.TCanvas()
cp.cd()
passhist.Draw("hist")
L.Draw("same")
AddCMSLumi(cp, dataScale, "Preliminary")
cp.Print("Plots/GJets/massplot_pass_match.png")

##
lheight = failhist.GetBinContent(failhist.FindBin(etamass))
L = TLine(etamass, 0, etamass, lheight)
L.SetLineColor(4)
L.SetLineStyle(2)
L.SetLineWidth(2)

failhist.SetLineWidth(3)
failhist.SetLineColor(30)
failhist.SetStats(0)

cf = ROOT.TCanvas()
cf.cd()
failhist.Draw("hist")
L.Draw("same")
AddCMSLumi(cf, dataScale, "Preliminary")
cf.Print("Plots/GJets/massplot_fail_match.png")

