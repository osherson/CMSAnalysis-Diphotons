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


hist2 = rdf.Histo2D(("m_v_e","Cluster Energy vs. Mass, Pass; Mass(GeV); Energy (GeV)", nbins_dipho, dipho_low, dipho_high, 200, 0, 100), "pass_mass","pass_energy")
h2 = hist2.GetValue().Clone()

dr_hist = rdf.Histo1D(("deltaR","#Delta R to Nearest Jet, Pass; #Delta R; Events",nbins_dipho, 0, 1.0), 'dr_ecut')
dr_2hist = rdf.Histo2D(("mass_v_deltaR","Nearest Jet #Delta R vs. Diphoton Mass, Pass; Mass (GeV); #Delta R",nbins_dipho, dipho_low, dipho_high, nbins_dipho, 0, 1.0), 'm_ecut','dr_ecut')
iso_hist = rdf.Histo1D(("iso","Cluster Energy / Jet Energy, Pass; Energy Ratio; Events",nbins_dipho, 0, 1.5), 'iso_edr')
iso_2hist = rdf.Histo2D(("mass_v_iso","(Clu Energy / Jet Energy) vs. Diphoton Mass, Pass; Mass (GeV); Energy Ratio",nbins_dipho, dipho_low, dipho_high, nbins_dipho, 0, 1.5), 'm_edr','iso_edr')

h_dr = dr_hist.GetValue().Clone()
h_dr2 = dr_2hist.GetValue().Clone()
h_iso = iso_hist.GetValue().Clone()
h_iso2 = iso_2hist.GetValue().Clone()

###iso
ci2 = ROOT.TCanvas()
ci2.cd()
h_iso2.SetStats(0)
h_iso2.Draw("colz")
ci2.SetLogz()
ci2.Print("Plots/2d_mass_iso_dataRun2.png")

ci = ROOT.TCanvas()
ci.cd()
h_iso.SetStats(0)
h_iso.SetLineWidth(3)
h_iso.Draw("hist")
ci.Print("Plots/iso_dataRun2.png")
###

###dr
c2 = ROOT.TCanvas()
c2.cd()
h_dr2.SetStats(0)
h_dr2.Draw("colz")
c2.SetLogz()
c2.Print("Plots/2d_mass_deltaR_dataRun2.png")

c = ROOT.TCanvas()
c.cd()
h_dr.SetStats(0)
h_dr.SetLineWidth(3)
h_dr.Draw("hist")
c.Print("Plots/deltaR_dataRun2.png")
###
exit()

c1 = ROOT.TCanvas()
c1.cd()
h2.SetStats(0)
h2.Draw("colz")
c1.SetLogz()
c1.Print("Plots/2D_mass_energy_dataRun2.png")

m_pi_hist = rdf.Histo1D(("mass_2_e_27","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_epi')
m_eta_hist = rdf.Histo1D(("mass_8_e_110","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_eeta')
m_etap_hist = rdf.Histo1D(("mass_14_e_190","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_eetap')
m_j_hist = rdf.Histo1D(("mass_44_e_620","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_ej')
m_pass_e_hist = rdf.Histo1D(("mass_30_e_60","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_ecut')
m_fail_e_hist = rdf.Histo1D(("mass_fail_30_e_60","Diphoton Mass, Fail; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'f_ecut')
m_pass_edr_hist = rdf.Histo1D(("mass_30_e_60_dr","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_edr')
m_fail_edr_hist = rdf.Histo1D(("mass_fail_30_e_60_dr","Diphoton Mass, Fail; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'f_edr')
m_pass_final_hist = rdf.Histo1D(("mass_final","Diphoton Mass, Pass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'm_final')
m_fail_final_hist = rdf.Histo1D(("mass_fail_final","Diphoton Mass, Fail; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'f_final')
pi_hist = m_pi_hist.GetValue().Clone()
eta_hist = m_eta_hist.GetValue().Clone()
etap_hist = m_etap_hist.GetValue().Clone()
j_hist = m_j_hist.GetValue().Clone()
pass_e_hist = m_pass_e_hist.GetValue().Clone()
fail_e_hist = m_fail_e_hist.GetValue().Clone()
pass_edr_hist = m_pass_edr_hist.GetValue().Clone()
fail_edr_hist = m_fail_edr_hist.GetValue().Clone()
pass_final_hist = m_pass_final_hist.GetValue().Clone()
fail_final_hist = m_fail_final_hist.GetValue().Clone()

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

makeMassHistWithLine(pi_hist, 0.134, 2, 27)
makeMassHistWithLine(eta_hist, 0.548, 8, 110)
makeMassHistWithLine(etap_hist, 0.958, 14, 190)
makeMassHistWithLine(j_hist, 0.548, 44, 620)
makeMassHistWithLine(pass_e_hist, 0.548, "pass_30", 60)
makeMassHistWithLine(fail_e_hist, 0.548, "fail_30", 60)
makeMassHistWithLine(pass_edr_hist, 0.548, "pass_edr_30", 60)
makeMassHistWithLine(fail_edr_hist, 0.548, "fail_edr_30", 60)
makeMassHistWithLine(pass_final_hist, 0.548, "pass_final_30", 60)
makeMassHistWithLine(fail_final_hist, 0.548, "fail_final_30", 60)

hfile = ROOT.TFile("Plots/massplot_ewindows_dataRun2.root","recreate")
hfile.cd()
h2.Write()
pi_hist.Write()
eta_hist.Write()
etap_hist.Write()
j_hist.Write()
pass_e_hist.Write()
fail_e_hist.Write()
pass_edr_hist.Write()
fail_edr_hist.Write()
pass_final_hist.Write()
fail_final_hist.Write()
h_dr.Write()
h_dr2.Write()
h_iso.Write()
h_iso2.Write()
hfile.Write()
hfile.Close()

tf = time.time()
print("Elapsed time: {:.1f} min".format((tf-ts)/60.))
