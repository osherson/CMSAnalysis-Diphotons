import ROOT
from ROOT import *
from array import array
import PlottingPayload as PL
import numpy

ROOT.gStyle.SetPadRightMargin(0.08)
ROOT.gStyle.SetPadLeftMargin(0.11)
ROOT.gStyle.SetPadTopMargin(0.10)
ROOT.gStyle.SetPalette(1)

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

def PlotLimitsHybridNew(o):
	Th, Thu, Thd = PL.PlotTheoryStop()

	x = []
	obs = []
	exp = []
	p1 = []
	m1 = []
	p2 = []
	m2 = []

	funcName = ""
	if o.f is "atlas": funcName = "Atlas 3-par"
	elif o.f is "dijet": funcName = "Dijet 3-par"
	elif o.f is "moddijet": funcName = "Modified Dijet 3-par"
	elif o.f is "envelope": funcName = "Envelope Method"

	STEPARR = []
	if o.massrange != None:
		MIN, MAX, STEP = o.massrange
		STEPARR = range(MIN, MAX + STEP, STEP) 
	else: STEPARR = o.mass

	for m in STEPARR:
		print "\n\n\n  " + str(m)
		x.append(float(m))
		F_output = "higgsCombinelimits_M"+str(m)+".HybridNew.mH125.root"
		F = TFile(F_output)
		T = F.Get("limit")
		T.GetEntry(0)
		obs.append(T.limit*0.1)


		F_output = "higgsCombinelimits_M"+str(m)+".HybridNew.mH125.quant0.025.root"
		
		F = TFile(F_output)
		T = F.Get("limit")
		T.GetEntry(0)
		m2.append(T.limit*0.1)

		F_output = "higgsCombinelimits_M"+str(m)+".HybridNew.mH125.quant0.160.root"
		
		F = TFile(F_output)
		T = F.Get("limit")
		T.GetEntry(0)
		m1.append(T.limit*0.1)

		F_output = "higgsCombinelimits_M"+str(m)+".HybridNew.mH125.quant0.500.root"
		F = TFile(F_output)
		T = F.Get("limit")
		T.GetEntry(0)
		exp.append(T.limit*0.1)

		F_output = "higgsCombinelimits_M"+str(m)+".HybridNew.mH125.quant0.840.root"
		F = TFile(F_output)
		T = F.Get("limit")
		T.GetEntry(0)
		p1.append(T.limit*0.1)

		F_output = "higgsCombinelimits_M"+str(m)+".HybridNew.mH125.quant0.975.root"
		F = TFile(F_output)
		T = F.Get("limit")
		T.GetEntry(0)
		p2.append(T.limit*0.1)

		print(x, obs, m2, m1, exp, p1, p2)
			
	THEMAX = 1.25 * max(obs + p2)
	THEMIN = 0.75 * min(obs + m2)
	LimitPlot = TH2F("LP", ";Dijet Resonance Mass (GeV);(pp #rightarrow #tilde{t}#tilde{t}, #tilde{t}#rightarrow qq) #sigma #times B (pb)", 100, 0, 3500, 100, THEMIN, THEMAX)
	LimitPlot.SetStats(0)
			
	Obs = TGraph(len(x), numpy.array(x), numpy.array(obs))
	Exp = TGraph(len(x), numpy.array(x), numpy.array(exp))
	Exp.SetLineStyle(2)
	Obs.SetMarkerStyle(20)
	Onesig = makeAFillGraph(x,m1,p1,kGreen,kGreen, 1001)
	Twosig = makeAFillGraph(x,m2,p2,kYellow,kYellow, 1001)

	L = TLegend(0.4,0.55,0.89,0.89)
	L.SetLineColor(0)
	L.SetFillColor(0)
	L.SetHeader("95% HybridNew CL Limits, " + funcName)
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
	Obs.Draw("PLsame")
	Th.Draw("Csame")
	Thu.Draw("Csame")
	Thd.Draw("Csame")
	L.Draw("same")
	PL.AddCMSLumi(gPad, 137.5, "Preliminary")
	C.Print("output/Limits/" + o.f + "_HybridNew_LimitPlot.png")
	C.Print("output/Limits/" + o.f + "_HybridNew_LimitPlot.root")


if __name__ == "__main__":
	from argparse import ArgumentParser
	parser = ArgumentParser()
	parser.add_argument("-f", type=str, help="What is the functional form being used here? Choices: dijet, moddijet, atlas, envelope.", metavar = 'FUNC' )

	mass_parse = parser.add_mutually_exclusive_group(required=True)
	mass_parse.add_argument("--mass", type=int, nargs = '*', default = 1000, help="Mass can be specified as a single value or a whitespace separated list (default: %(default)s)" )
	mass_parse.add_argument("--massrange", type=int, nargs = 3, help="Define a range of masses to be produced. Format: min max step", metavar = ('MIN', 'MAX', 'STEP') )

	o = parser.parse_args()
	PlotLimits(o)