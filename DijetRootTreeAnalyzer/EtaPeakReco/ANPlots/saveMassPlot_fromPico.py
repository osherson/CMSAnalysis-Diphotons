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
#chain.Add("/cms/sclark-2/DiPhotonsTrees/etaReco/sample.root")
#chain.Add("/cms/sclark-2/DiPhotonsTrees/etaReco/Run_B_2017.root")

ct=0
for fil in os.listdir(xaastorage):
  #if(fil.startswith("Run") and fil.endswith(".root") and "2016" in fil):
  #if(fil.startswith("Run") and fil.endswith(".root") and "Run_D_2018" not in fil):
  if(fil.startswith("Run") and fil.endswith(".root")):
    print(fil)
    if('q' in sys.argv and ct > 4): break
    chain.Add(os.path.join(xaastorage,fil))
    ct += 1

rdf = RDF(chain)

print(rdf.Count().GetValue())

#rdf = rdf.Define("pass_mass","ruclu_mass[diphoScores > 0.9]")
rdf = rdf.Define("pass_mass","ruclu_mass[diphoScores > -999]")
#rep = rdf.Report()
#rep.Print()

mhist = rdf.Histo1D(("mass","Diphoton Mass; Mass(GeV); Events",nbins_dipho, dipho_low, dipho_high), 'pass_mass')
hist = mhist.GetValue().Clone()

c1 = ROOT.TCanvas()
c1.cd()
legend = TLegend(0.65,0.55,0.90,0.80)

hist.SetLineWidth(3)
hist.SetStats(0)
hist.Draw("hist")

etamass = 0.548
lheight = hist.GetBinContent(hist.FindBin(etamass))
#lheight=0.1
L = TLine(etamass, 0, etamass, lheight)
L.SetLineColor(4)
L.SetLineStyle(2)
L.SetLineWidth(2)
L.Draw("same")
legend.AddEntry(L,"#eta","L")

etapmass = 0.957
lpheight = hist.GetBinContent(hist.FindBin(etapmass))
#lheight=0.1
Lep = TLine(etapmass, 0, etapmass, lpheight)
Lep.SetLineColor(6)
Lep.SetLineStyle(2)
Lep.SetLineWidth(2)
Lep.Draw("same")
legend.AddEntry(Lep,"#eta'","L")

pimass = 0.134
lheight = hist.GetBinContent(hist.FindBin(pimass))
#lheight=0.1
Lpi = TLine(pimass, 0, pimass, lheight)
Lpi.SetLineColor(4)
Lpi.SetLineStyle(2)
Lpi.SetLineWidth(2)
Lpi.Draw("same")
legend.AddEntry(Lpi,"#pi^0","L")

jpmass = 3.097
ljheight = hist.GetBinContent(hist.FindBin(jpmass))
#lheight=0.1
Ljp = TLine(jpmass, 0, jpmass, ljheight)
Ljp.SetLineColor(8)
Ljp.SetLineStyle(2)
Ljp.SetLineWidth(2)
Ljp.Draw("same")
legend.AddEntry(Ljp,"J/#psi","L")

legend.Draw("same")

gStyle.SetLegendTextSize(0.05)
AddCMSLumi(c1, dataScale, "Preliminary")
c1.SetLogy()
c1.Print("Plots/massplot_nocuts_dataRun2.png")
hfile = ROOT.TFile("Plots/massplot_nocuts_dataRun2.root","recreate")
hfile.cd()
hist.Write()
hfile.Write()
hfile.Close()

tf = time.time()
print("Elapsed time: {:.1f} min".format((tf-ts)/60.))
