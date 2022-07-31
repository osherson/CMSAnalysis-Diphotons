
import ROOT
from ROOT import *
import numpy
import math
import sys
import array
import os

os.system("combine "+sys.argv[1]+" -M Significance")
os.system("combine "+sys.argv[1]+" -M FitDiagnostics --saveShapes --saveWithUncertainties")


GoodBins = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0]
Template = TH1F("temp", ";;Events / GeV", len(GoodBins)-1, numpy.array(GoodBins))
Template.GetXaxis().SetLabelSize(0.)
PullTemplate = TH1F("tempP", ";Di-cluster mass [GeV];#frac{data - bkg}{#sigma_{data}}", len(GoodBins)-1, numpy.array(GoodBins))
PullTemplate.GetYaxis().SetTitleSize(0.15);
PullTemplate.GetYaxis().SetNdivisions(6);
PullTemplate.GetYaxis().SetTitleOffset(0.225);
PullTemplate.GetXaxis().SetTitleSize(0.15);
PullTemplate.GetXaxis().SetLabelSize(0.15);
PullTemplate.GetYaxis().SetLabelSize(0.1);
PullTemplate.GetXaxis().SetTitleOffset(1.155);
PullTemplate.GetYaxis().CenterTitle(True)
PullTemplate.GetYaxis().SetRangeUser(-5.,5.)
PullTemplate.SetStats(0)
PullTemplate.SetLineColor(kBlack)

def MakePull(D, F, c, N):
	P = D.Clone(N)
	for i in range(1,D.GetNbinsX()+1):
		Err = max(math.sqrt(D.GetBinContent(i)), 1.4)
		P.SetBinContent(i, (D.GetBinContent(i) - F.GetBinContent(i))/Err)
	P.SetLineColor(c)
	return P

	
def MakeSigPull(D, F, c, N):
	P = D.Clone(N)
	for i in range(1,D.GetNbinsX()+1):
		Err = max(math.sqrt(D.GetBinContent(i)), 1.4)
		P.SetBinContent(i, (F.GetBinContent(i))/Err)
	P.SetLineColor(c)
	return P


def convertAsymGraph(TG, template, name):
	Hist = template.Clone(name)
	for i in range(1,Hist.GetNbinsX()+1):
		Hist.SetBinContent(i,0.)
	for i in range(TG.GetN()):
		Hist.SetBinContent(i+1,TG.GetY()[i]*(TG.GetErrorXlow(i)+TG.GetErrorXhigh(i)))
		Hist.SetBinError(i+1, TG.GetErrorY(i))
	return Hist
def convertBinNHist(H, template, name):
	Hist = template.Clone(name)
	for i in range(1,Hist.GetNbinsX()+1):
		Hist.SetBinContent(i,H.GetBinContent(i))
		Hist.SetBinError(i,H.GetBinError(i))
	return Hist

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

def DBBW(H):
	for i in range(1,H.GetNbinsX()+1):
		C = H.GetBinContent(i)
		E = H.GetBinError(i)
		W = H.GetBinWidth(i)
		H.SetBinContent(i, C/W)
		H.SetBinError(i, E/W)	
	return H

F = TFile("higgsCombineTest.Significance.mH120.root")
T = F.Get("limit")
T.GetEntry(0)
significance = T.limit

F = TFile("fitDiagnostics.root")
data = convertAsymGraph(F.Get("shapes_prefit/diphoton_dijet/data"), Template, "data")
b = convertBinNHist(F.Get("shapes_fit_b/diphoton_dijet/total_background"), Template, "b")
s = convertBinNHist(F.Get("shapes_fit_s/diphoton_dijet/total_background"), Template, "splusb")
sig = convertBinNHist(F.Get("shapes_fit_s/diphoton_dijet/total"), Template, "sig")

data.SetMarkerStyle(20)
data.SetMarkerSize(0.65)
data.SetLineColor(kBlack)
data.SetLineWidth(1)
b.SetLineColor(kBlue)
b.SetLineWidth(3)
s.SetLineColor(kRed)
s.SetLineWidth(1)
s.SetLineStyle(2)
sig.SetLineColor(kRed)

bP = MakePull(data, b, kBlue, "BP")
sP = MakePull(data, sig, kRed, "SP")


L = TLegend(0.6,0.7,0.89,0.89)
L.SetFillColor(0)
L.SetLineColor(0)
L.AddEntry(data, "Data", "PL")
L.AddEntry(b, "Bkg in B fit", "L")
L.AddEntry(s, "Bkg in S+B fit", "L")
L.AddEntry(sig, "Total in S+B fit (S = %.2f#sigma)"%significance, "L")

for h in [data, b, s, sig]:
	h = DBBW(h)
FindAndSetMax(data,b,s,sig,Template)

C = TCanvas("T", "", 500, 500)
C.cd()
p12 = ROOT.TPad("pad1", "tall",0,0.165,1,1)
p22 = ROOT.TPad("pad2", "short",0,0.0,1.0,0.235)
p22.SetBottomMargin(0.35)
p12.Draw()
p22.Draw()
p12.cd()
p12.SetLogx()
Template.Draw()
data.Draw("e0same")
b.Draw("histsame")
s.Draw("histsame")
sig.Draw("histsame")
L.Draw("same")
p22.cd()
p22.SetLogx()
PullTemplate.Draw()
PullTemplate.GetXaxis().SetMoreLogLabels()
bP.Draw("histsame")
sP.Draw("histsame")
C.Print("PostFits.png")