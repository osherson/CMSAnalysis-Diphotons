import FUNCTIONS
from FUNCTIONS import *
import ROOT
from ROOT import *
from array import array
import os

ROOT.gStyle.SetPadRightMargin(0.08);
ROOT.gStyle.SetPadLeftMargin(0.11);
ROOT.gStyle.SetPadTopMargin(0.10);
ROOT.gStyle.SetPalette(1);

ROOT.gROOT.SetBatch()

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
	latex.DrawLatex(0.1265, 0.825, cmsText)
	pad.Update()

def makeAFillGraph(listx,listy1,listy2,linecolor, fillcolor, fillstyle):

	a_m = array('f', []);
	a_g = array('f', []);

	for i in range(len(listx)):
		a_m.append(listx[i]);
		a_g.append(listy1[i]);
	
	for i in range(len(listx)-1,-1,-1):
		a_m.append(listx[i]);
		a_g.append(listy2[i]);

	gr = ROOT.TGraph(2*len(listx),a_m,a_g);

	gr.SetLineColor(linecolor)
	gr.SetFillColor(fillcolor)
	gr.SetFillStyle(fillstyle)

	return gr
	  


Th, Thu, Thd = PlotTheoryStop()

x = []
obs = []
exp = []
p1 = []
m1 = []
p2 = []
m2 = []

obsANCH = []

def PlotLimits(o):
	funcName = ""
	if o.f is "atlas": funcName = "Atlas 3-par"
	elif o.f is "dijet": funcName = "Dijet 3-par"
	elif o.f is "moddijet": funcName = "Modified Dijet 3-par"
	elif o.f is "envelope": funcName = "Envelope Method"

	os.chdir("/users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer")
	# for m in [500,600,700,800,900,1000,1250,1500,1750,2000,2500,3000]:
	MANCH = [500,600,700,800,900,1000,1250,1500,1750,2000,2500,3000]
	STEPARR = []
	if o.massrange != None:
		MIN, MAX, STEP = o.massrange
		STEPARR = range(MIN, MAX + STEP, STEP)
	elif o.massvarbins:
		BinEdges = [526., 565., 606., 649., 693., 740., 788., 838., 890., 944., 1000., 1058., 1118., 1181., 1246., 1313., 1383., 1455., 1530., 1607., 1687., 1770., 1856., 1945., 2037., 2132., 2231., 2332., 2438., 2546., 2659., 2775., 2895.]
		TempH = ROOT.TH1F("binedge_temp_H", ";Average Dijet Mass [GeV];Events", len(BinEdges)-1, numpy.array(BinEdges))
		STEPARR = [TempH.GetBinCenter(n) for n in range(1, TempH.GetNbinsX()+1)]
		STEPARR.extend(MANCH)
		STEPARR = sorted(STEPARR)
	else: STEPARR = o.mass

	for m in STEPARR:
		if type(m)==float and m.is_integer(): m = int(m)
		print "\n\n\n  " + str(m).replace(".", "_")
		# os.system("combine output/dijet_combine_gg_gg_"+str(m)+"_750_lumi-137.500_PFJetHT_RunII_asl0.txt -M AsymptoticLimits -n _" + o.f + "_M"+str(m))
		os.system("combine output/Full_" + o.f + "_M"+str(m).replace(".", "_")+".txt -M AsymptoticLimits -n _" + o.f + "_M"+str(m).replace(".", "_"))
		# os.system("combine output/Full_" + o.f + "_M"+str(m)+".txt -M AsymptoticLimits -n _" + o.f + "_M"+str(m) + " --setParameterRanges r=0,0.2 --saveWorkspace --cminDefaultMinimizerTolerance 0.00100 --cminDefaultMinimizerStrategy 2 --strictBounds")
		F_output = "higgsCombine_" + o.f + "_M"+str(m).replace(".", "_")+".AsymptoticLimits.mH120.root"
		F = TFile(F_output)
		T = F.Get("limit")
		n = T.GetEntries()
		if n == 6:
			x.append(float(m))
			T.GetEntry(5)
			obs.append(T.limit*0.1)
			if m in MANCH: obsANCH.append(T.limit*0.1)
			T.GetEntry(0)
			m2.append(T.limit*0.1)
			T.GetEntry(1)
			m1.append(T.limit*0.1)
			T.GetEntry(2)
			exp.append(T.limit*0.1)
			T.GetEntry(3)
			p1.append(T.limit*0.1)
			T.GetEntry(4)
			p2.append(T.limit*0.1)
			
	THEMAX = 1.25 * max(obs + p2) * 5.
	THEMIN = 0.75 * min(obs + m2)
	LimitPlot = TH2F("LP", ";Dijet Resonance Mass (GeV);(pp #rightarrow #tilde{t}#tilde{t}, #tilde{t}#rightarrow qq) #sigma #times B (pb)", 100, 0, 3500, 100, THEMIN, THEMAX)
	LimitPlot.SetStats(0)
			
	Obs = TGraph(len(x), numpy.array(x), numpy.array(obs))
	ObsAnch = TGraph(len(MANCH), numpy.array(MANCH, float), numpy.array(obsANCH))
	Exp = TGraph(len(x), numpy.array(x), numpy.array(exp))
	Exp.SetLineStyle(2)
	# Obs.SetMarkerStyle(20)
	Obs.SetLineColor(kBlack)
	ObsAnch.SetMarkerStyle(20)
	ObsAnch.SetMarkerColor(kRed)
	Onesig = makeAFillGraph(x,m1,p1,kGreen,kGreen, 1001)
	Twosig = makeAFillGraph(x,m2,p2,kYellow,kYellow, 1001)

	L = TLegend(0.5,0.5,0.89,0.89)
	L.SetLineColor(0)
	L.SetFillColor(0)
	L.SetHeader("95% CL Limits, " + funcName)
	L.AddEntry(Obs, "observed", "PL")
	L.AddEntry(Exp, "expected", "PL")
	L.AddEntry(Onesig, "expected #pm 1#sigma", "F")
	L.AddEntry(Twosig, "expected #pm 2#sigma", "F")
	L.AddEntry(Th, "#tilde{t}#tilde{t} production #lambda_{312}, #tilde{t}#rightarrow q#bar{q}", "L")

	C = TCanvas()
	C.cd()
	C.SetLogy()
	LimitPlot.Draw()
	Twosig.Draw("Fsames")
	Onesig.Draw("Fsames")
	Exp.Draw("Lsame")
	Obs.Draw("Csame")
	ObsAnch.Draw("Psame")
	Th.Draw("Csame")
	Thu.Draw("Csame")
	Thd.Draw("Csame")
	L.Draw("same")
	AddCMSLumi(gPad, 137.5, "Preliminary")
	C.Print("/users/h2/th544/CMSSW_11_0_0_pre2/src/PairedPairs2D/data_analysis/combineHelper/limits/" + o.f + "_LimitPlot" + ("_varbins" if o.massvarbins else "") + ".png")
	C.Print("/users/h2/th544/CMSSW_11_0_0_pre2/src/PairedPairs2D/data_analysis/combineHelper/limits/" + o.f + "_LimitPlot" + ("_varbins" if o.massvarbins else "") + ".root")

if __name__ == "__main__":
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument("-f", type=str, help="What is the functional form being used here? Choices: dijet, moddijet, atlas, envelope.", metavar = 'FUNC' )

	mass_parse = parser.add_mutually_exclusive_group(required=True)
	mass_parse.add_argument("--mass", type=int, nargs = '*', default = 1000, help="Mass can be specified as a single value or a whitespace separated list (default: %(default)s)" )
	mass_parse.add_argument("--massrange", type=int, nargs = 3, help="Define a range of masses to be produced. Format: min max step", metavar = ('MIN', 'MAX', 'STEP') )
	mass_parse.add_argument("--massvarbins", action="store_true", help="Compute limits for` RPV signals with masses equal to the bin centers of the dijet binning.")

	o = parser.parse_args()
	PlotLimits(o)