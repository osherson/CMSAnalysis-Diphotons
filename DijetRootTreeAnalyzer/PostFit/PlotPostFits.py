
import ROOT
from ROOT import *
import numpy
import math
import sys
import array
import os

gROOT.SetBatch()

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

infile = sys.argv[1]
cps = infile[infile.rfind("/"):]
cps = cps.split("_")
an = cps[1]
mm = cps[2]
fit = cps[3]
fit = fit[ :fit.find(".")]
print(an, mm, fit)

newDir = "combineOutput/{}_{}_{}".format(an,mm,fit)
os.system("mkdir {}".format(newDir))

os.system("combine "+sys.argv[1]+" -M Significance")
os.system("combine "+sys.argv[1]+" -M AsymptoticLimits")
F = ROOT.TFile("higgsCombineTest.AsymptoticLimits.mH120.root")
T = F.Get("limit")
T.GetEntry(2)
exp = T.limit
T.GetEntry(4)
p2 = T.limit - exp
Lc = [0., exp, exp+p2, exp+2*p2]
Ln = ["null", "exp", "sig2", "sig4"]
os.system("combine "+sys.argv[1]+" -M FitDiagnostics --saveShapes --saveWithUncertainties")
print Lc

F = TFile("higgsCombineTest.Significance.mH120.root")
T = F.Get("limit")
T.GetEntry(0)
significance = T.limit

F = TFile("fitDiagnostics.root")
data = convertAsymGraph(F.Get("shapes_prefit/"+sys.argv[2]+"/data"), Template, "data")
b = convertBinNHist(F.Get("shapes_fit_b/"+sys.argv[2]+"/total_background"), Template, "b")
s = convertBinNHist(F.Get("shapes_fit_s/"+sys.argv[2]+"/total_background"), Template, "splusb")
sig = convertBinNHist(F.Get("shapes_fit_s/"+sys.argv[2]+"/total"), Template, "sig")

data.SetMarkerStyle(20)
data.SetMarkerSize(0.65)
data.SetLineColor(kBlack)
data.SetLineWidth(1)
b.SetLineColor(kBlue)
b.SetLineWidth(3)
s.SetLineColor(kRed)
s.SetLineWidth(3)
sig.SetLineWidth(3)
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
L.AddEntry(sig, "Total in S+B fit (S = %.2f #sigma)"%significance, "L")

for h in [data, b, s, sig]:
	h = DBBW(h)
FindAndSetMax(data,b,s,sig,Template)

C = TCanvas("T", "", 500, 500)
C.cd()
p12 = TPad("pad1", "tall",0,0.165,1,1)
p22 = TPad("pad2", "short",0,0.0,1.0,0.235)
p22.SetBottomMargin(0.35)
p12.Draw()
p22.Draw()
p12.cd()
p12.SetLogx()
Template.Draw()
b.Draw("histsame")
s.Draw("histsame")
sig.Draw("histsame")
data.Draw("e0same")
L.Draw("same")
gPad.SetTicks(1,1)
gPad.RedrawAxis()
p22.cd()
p22.SetLogx()
PullTemplate.Draw()
PullTemplate.GetXaxis().SetMoreLogLabels()
bP.Draw("histsame")
sP.Draw("histsame")
gPad.SetTicks(1,1)
gPad.RedrawAxis()
C.Print("{}/PostFits_{}_{}_{}.png".format(newDir,an,mm,fit))
C.Print("{}/PostFits_{}_{}_{}.root".format(newDir,an,mm,fit))

os.system("combine "+sys.argv[1]+" -M GoodnessOfFit --algo=saturated")
KS_Fs = TFile("higgsCombineTest.GoodnessOfFit.mH120.root")
KS_Ts = KS_Fs.Get("limit")
KS_Vs = []
for i in range(0,KS_Ts.GetEntries()):
	KS_Ts.GetEntry(i)
	KS_Vs.append(KS_Ts.limit)
os.system("combine "+sys.argv[1]+" -M GoodnessOfFit --algo=saturated -t 500")
KS_F = TFile("higgsCombineTest.GoodnessOfFit.mH120.123456.root")	
KS_T = KS_F.Get("limit")
KS_V = []
for i in range(0,KS_T.GetEntries()):
	KS_T.GetEntry(i)
	KS_V.append(KS_T.limit)
minKS = min(min(KS_V),min(KS_Vs))
maxKS = max(max(KS_V),max(KS_Vs))
rangeKS = maxKS - minKS
KS_plot = TH1F("KS_plot", ";Goodness Of Fit Statistic (Saturated);toys", 50, minKS-(rangeKS/7.), maxKS+(rangeKS/7.))
KS_plot.SetStats(0)
for i in KS_V: KS_plot.Fill(i)

KS_plot.SetMarkerStyle(20)
KS_plot.SetLineColor(kBlack)

KS_mk = TLine(KS_Vs[0], 0., KS_Vs[0], KS_plot.GetMaximum()*0.4)
KS_mk.SetLineColor(ROOT.kBlue)
KS_mk.SetLineWidth(3)

FitFunc = TF1("FitFunc", "gaus", minKS-(rangeKS/7.), maxKS+(rangeKS/7.))
KS_plot.Fit(FitFunc, "EMR0")
FitFunc.SetLineStyle(2)

sigma = (KS_Vs[0] - FitFunc.GetParameter(1))/FitFunc.GetParameter(2)
L2 = TLegend(0.667,0.75,0.89,0.89)
L2.SetLineColor(0)
L2.SetFillColor(0)
L2.AddEntry(KS_mk, "GOF: %.2f #sigma"%sigma, "L")

C_KS = TCanvas()
C_KS.cd()
KS_plot.Draw("e")
FitFunc.Draw("same")
KS_mk.Draw("same")
L2.Draw("same")
gPad.SetTicks(1,1)
gPad.RedrawAxis()
C_KS.Print("{}/GoF_{}_{}_{}.png".format(newDir,an,mm,fit))
C_KS.Print("{}/GoF_{}_{}_{}.root".format(newDir,an,mm,fit))

for i,j in zip(Lc,Ln):
	os.system("combine "+sys.argv[1]+" -M GenerateOnly -t 500 --saveToys --toysFrequentist  --expectSignal "+str(i)+" -n "+j+" --bypassFrequentistFit")
	os.system("combine "+sys.argv[1]+" -M FitDiagnostics --bypassFrequentistFit --skipBOnlyFit -t 500 --toysFile higgsCombine"+j+".GenerateOnly.mH120.123456.root --rMin -10 --rMax 10 --saveWorkspace -n "+j)
	F = ROOT.TFile("fitDiagnostics"+j+".root")
	T = F.Get("tree_fit_sb")
	H = ROOT.TH1F("Bias Test, injected r="+j, ";(#mu_{measured} - #mu_{injected})/#sigma_{#mu};toys", 50, -5., 5.)
	T.Draw("(r-%f)"%i+"/rErr>>Bias Test, injected r=" + j)
	#T.Draw("(r-%f)"%i+"/rErr>>Bias Test, injected r=" + j, "fit_status == 0")
	G = ROOT.TF1("f", "gaus(0)", -5.,5.)
	H.Fit(G)
	ROOT.gStyle.SetOptFit(1111)
	C_B = ROOT.TCanvas()
	C_B.cd()
	H.Draw("e0")
	C_B.Print(newDir+"/"+j+"_{}_{}_{}.png".format(an,mm,fit))
	C_B.Print(newDir+"/"+j+"_{}_{}_{}.root".format(an,mm,fit))

#os.system("mv *.png {}/.".format(newDir))
