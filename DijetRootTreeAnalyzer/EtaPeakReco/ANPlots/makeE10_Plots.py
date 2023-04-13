#
import ROOT
from ROOT import *
import sys,os
import glob
import numpy
import time

RDF = ROOT.ROOT.RDataFrame
#ROOT.gROOT.SetBatch(ROOT.kTRUE)

def FindAndSetMax(*args):
  if len(args) == 1: args = args[0]
  maximum = 0.0
  for i in args:
    i.SetStats(0)
    t = i.GetMaximum()
    if t > maximum:
      maximum = t
  for j in args:
    j.GetYaxis().SetRangeUser(0,maximum*1.35)#should be 1.35 (below as well)
    j.SetLineWidth(2)
  return maximum*1.35

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

dscore = "09"
dpscore = 0.9

dgq = "data"

nbins_dipho = 400*4/10
dipho_low = 0
dipho_high = 4

ts = time.time()

#chain = ROOT.TChain("pico_skim")
chain = ROOT.TChain("pico_full")
xaastorage = "/cms/sclark-2/DiPhotonsTrees/etaReco/"
#chain.Add("/cms/sclark-2/DiPhotonsTrees/etaReco/Run_B_2017.root")

ct=0
for fil in os.listdir(xaastorage):
  #if(fil.startswith("Run") and fil.endswith(".root") and "2016" in fil):
  if(fil.startswith("Run") and fil.endswith(".root")):
    print(fil)
    if('q' in sys.argv and ct > 4): break
    chain.Add(os.path.join(xaastorage,fil))
    ct += 1

rdf = RDF(chain)

print(rdf.Count().GetValue())

rdf = rdf.Define("pass_mass","ruclu_mass[diphoScores > 0.9]")
rdf = rdf.Define("pass_energy","ruclu_energy[diphoScores > 0.9]")
rdf = rdf.Define("pass_dr","nj_dr[diphoScores > 0.9]")
rdf = rdf.Define("pass_iso","pass_energy/nj_energy[diphoScores>0.9]")
rdf = rdf.Define("fail_mass","ruclu_mass[diphoScores <= 0.9]")
rdf = rdf.Define("fail_energy","ruclu_energy[diphoScores <= 0.9]")
rdf = rdf.Define("fail_dr","nj_dr[diphoScores <= 0.9]")
rdf = rdf.Define("fail_iso","fail_energy/nj_energy[diphoScores<=0.9]")
rdf = rdf.Define("m_epi","pass_mass[pass_energy >= 2 && pass_energy < 27]")
rdf = rdf.Define("m_eeta","pass_mass[pass_energy >= 8 && pass_energy < 110]")
rdf = rdf.Define("m_eetap","pass_mass[pass_energy >= 14 && pass_energy < 190]")
rdf = rdf.Define("m_ej","pass_mass[pass_energy >= 44 && pass_energy < 620]")

rdf = rdf.Define("m_ecut","pass_mass[pass_energy >= 30 && pass_energy < 60]")
rdf = rdf.Define("dr_ecut","pass_dr[pass_energy >= 30 && pass_energy < 60]")
rdf = rdf.Define("f_ecut","fail_mass[fail_energy >= 30 && fail_energy < 60]")
rdf = rdf.Define("dr_f_ecut","fail_mass[fail_energy >= 30 && fail_energy < 60]")

rdf = rdf.Define("m_edr","pass_mass[pass_energy >= 30 && pass_energy < 60 && pass_dr < 0.15]")
rdf = rdf.Define("f_edr","fail_mass[fail_energy >= 30 && fail_energy < 60 && fail_dr < 0.15]")
rdf = rdf.Define("iso_edr","pass_iso[pass_energy >= 30 && pass_energy < 60 && pass_dr < 0.15]")
rdf = rdf.Define("iso_f_edr","fail_iso[fail_energy >= 30 && fail_energy < 60 && fail_dr < 0.15]")

rdf = rdf.Define("m_final","pass_mass[pass_energy >= 30 && pass_energy < 60 && pass_dr < 0.15 && pass_iso > 0.5 && pass_iso < 1]")
rdf = rdf.Define("f_final","fail_mass[fail_energy >= 30 && fail_energy < 60 && fail_dr < 0.15 && fail_iso > 0.5 && fail_iso < 1]")

rdf = rdf.Define("m_e30","pass_mass[pass_energy >= 30 && pass_energy < 40 && pass_dr < 0.15 && pass_iso > 0.5 && pass_iso < 1]")
rdf = rdf.Define("m_e40","pass_mass[pass_energy >= 40 && pass_energy < 50 && pass_dr < 0.15 && pass_iso > 0.5 && pass_iso < 1]")
rdf = rdf.Define("m_e50","pass_mass[pass_energy >= 50 && pass_energy < 60 && pass_dr < 0.15 && pass_iso > 0.5 && pass_iso < 1]")
rdf = rdf.Define("m_e60","pass_mass[pass_energy >= 60 && pass_energy < 70 && pass_dr < 0.15 && pass_iso > 0.5 && pass_iso < 1]")
rdf = rdf.Define("m_e70","pass_mass[pass_energy >= 70 && pass_energy < 80 && pass_dr < 0.15 && pass_iso > 0.5 && pass_iso < 1]")
rdf = rdf.Define("m_e80","pass_mass[pass_energy >= 80 && pass_energy < 90 && pass_dr < 0.15 && pass_iso > 0.5 && pass_iso < 1]")

m_30_hist = rdf.Histo1D(("mass_30_e_40","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_e30')
m_40_hist = rdf.Histo1D(("mass_40_e_50","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_e40')
m_50_hist = rdf.Histo1D(("mass_50_e_60","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_e50')
m_60_hist = rdf.Histo1D(("mass_60_e_70","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_e60')
m_70_hist = rdf.Histo1D(("mass_70_e_80","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_e70')
m_80_hist = rdf.Histo1D(("mass_80_e_90","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_e80')
m30_hist = m_30_hist.GetValue().Clone()
m40_hist = m_40_hist.GetValue().Clone()
m50_hist = m_50_hist.GetValue().Clone()
m60_hist = m_60_hist.GetValue().Clone()
m70_hist = m_70_hist.GetValue().Clone()
m80_hist = m_80_hist.GetValue().Clone()

def makeMassHistWithLine(hist, partmass, elow, ehigh):

  etamass = 0.548
  lheight = hist.GetBinContent(hist.FindBin(etamass))
  #lheight=0.1
  L = TLine(etamass, 0, etamass, lheight)
  L.SetLineColor(4)
  L.SetLineStyle(2)
  L.SetLineWidth(2)

  lpheight = hist.GetBinContent(hist.FindBin(partmass))
  Lp = TLine(partmass, 0, partmass, lpheight)
  Lp.SetLineColor(4)
  Lp.SetLineStyle(2)
  Lp.SetLineWidth(2)

  hist.SetLineWidth(3)
  hist.SetStats(0)

  cpi = ROOT.TCanvas()
  cpi.cd()
  hist.Draw("hist")
  L.Draw("same")
  Lp.Draw("same")
  AddCMSLumi(cpi, dataScale, "Preliminary")
  cpi.Print("Plots/massplot_{}_e_{}_dataRun2.png".format(elow, ehigh))

makeMassHistWithLine(m30_hist, 0.548, 30, 40)
makeMassHistWithLine(m40_hist, 0.548, 40, 50)
makeMassHistWithLine(m50_hist, 0.548, 50, 60)
makeMassHistWithLine(m60_hist, 0.548, 60, 70)
makeMassHistWithLine(m70_hist, 0.548, 70, 80)
makeMassHistWithLine(m80_hist, 0.548, 80, 90)

hfile = ROOT.TFile("Plots/massplot_e10windows_dataRun2.root","recreate")
hfile.cd()
m30_hist.Write()
m40_hist.Write()
m50_hist.Write()
m60_hist.Write()
m70_hist.Write()
m80_hist.Write()
hfile.Write()
hfile.Close()

tf = time.time()
print("Elapsed time: {:.1f} min".format((tf-ts)/60.))
