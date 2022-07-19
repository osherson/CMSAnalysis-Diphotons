#
import ROOT
from ROOT import *
import numpy as np

def MakeNLL(F, c, m):
	F = TFile(F)
	point = []
	r = []
	T = F.Get("limit")
	for i in range(T.GetEntries()):
		T.GetEntry(i)
		NLL = T.nll0+T.deltaNLL+T.nll
		point.append(NLL)
		r.append(T.r)
	G = TGraph(len(r), np.array(r), np.array(point))
	G.SetMarkerColor(c)
	G.SetMarkerStyle(m)
	return G
	

#e = MakeNLL("higgsCombineenv.MultiDimFit.mH120.root", 1, 22)
#p = MakeNLL("higgsCombinep2.MultiDimFit.mH120.root", 2, 23)
#a = MakeNLL("higgsCombinea2.MultiDimFit.mH120.root", 3, 21)
#m = MakeNLL("higgsCombinem2.MultiDimFit.mH120.root", 4, 20)


#e = MakeNLL("/cms/osherson/DIJETCODE/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/higgsCombineENV.MultiDimFit.mH120.root", 1, 22)
#p = MakeNLL("/cms/osherson/DIJETCODE/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/higgsCombineIdx0.MultiDimFit.mH120.root", 2, 23)
#a = MakeNLL("/cms/osherson/DIJETCODE/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/higgsCombineIdx1.MultiDimFit.mH120.root", 3, 21)
#m = MakeNLL("/cms/osherson/DIJETCODE/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/higgsCombineIdx2.MultiDimFit.mH120.root", 4, 20)

e = MakeNLL("higgsCombineENV.MultiDimFit.mH120.root", 1, 22)
dj = MakeNLL("higgsCombineIdx0.MultiDimFit.mH120.root", 2, 23)
mdj = MakeNLL("higgsCombineIdx1.MultiDimFit.mH120.root", 3, 21)
atl = MakeNLL("higgsCombineIdx2.MultiDimFit.mH120.root", 4, 20)
dp = MakeNLL("higgsCombineIdx3.MultiDimFit.mH120.root", 5, 24)
p = MakeNLL("higgsCombineIdx4.MultiDimFit.mH120.root", 6, 25)
 
L = TLegend(0.65,0.11,0.89,0.3)
L.SetLineColor(0)
L.SetFillColor(0)
L.AddEntry(e, "full envelope", "P")
L.AddEntry(dj, "dijet", "P")
L.AddEntry(mdj, "moddijet", "P")
L.AddEntry(atl, "atlas", "P")
L.AddEntry(dp, "dipho", "P")
L.AddEntry(p, "power", "P")

p.SetTitle(";signal strength (1 TeV stops); NLL")

C = TCanvas("c", "", 900, 500)
C.cd()
dj.Draw("AP")
mdj.Draw("Psame")
atl.Draw("Psame")
dp.Draw("Psame")
p.Draw("Psame")
e.Draw("Psame")
L.Draw("same")
C.Print("NLLenv.png")

