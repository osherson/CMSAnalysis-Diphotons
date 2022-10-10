
import ROOT
from ROOT import *
import numpy
import math
import sys
import array
import os

#gROOT.SetBatch()

NEVENTS_TOGEN = 10000

GoodBins = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0, 2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0]

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
anum = an[5:]


fList = []

comName = "_{}_{}".format(an,mm)

newDir = "combineOutput/{}_{}_{}".format(an,mm,fit)
os.system("mkdir {}".format(newDir))

sig_file = "../inputs/Shapes_fromGen/alphaBinning/{}/{}/PLOTS_{}.root".format(anum, mm, anum)
print(sig_file)
if(os.path.exists(sig_file)):
  sfile = ROOT.TFile(sig_file, "READ")
  sig_hist = sfile.Get("{}_XM".format(mm))
elif(os.path.exists(sig_file.replace("Gen","Interpo"))):
  print(sig_file.replace("Gen","Interpo"))
  sfile = ROOT.TFile(sig_file.replace("Gen","Interpo"), "READ")
  #sig_hist = sfile.Get("{}_XM".format(mm))
  sig_hist1 = sfile.Get("h_AveDijetMass_1GeV")

  ffile = open("../inputs/Shapes_fromInterpo/alphaBinning/{}/{}/alphaFracion_alpha{}_{}.txt".format(anum,mm,anum,mm), "r")
  frac = float(ffile.readline())
  ffile.close()
  eff_file = open("../inputs/Shapes_fromInterpo/alphaBinning/{}/{}/{}.txt".format(anum,mm,mm), "r")
  eff = float(eff_file.readline())
  eff_file.close()
  
  sig_hist1.Scale(NEVENTS_TOGEN * frac * eff)
  sig_hist = sig_hist1.Rebin(len(GoodBins)-1, "{}_XM".format(mm), numpy.array(GoodBins))

try:
  sig_hist.SetLineColor(2)
  sig_hist.SetFillColor(ROOT.kRed-10)
  data_hist = sfile.Get("data_XM")
  
  data_hist.SetMarkerStyle(20)
  data_hist.SetMarkerSize(0.65)
  data_hist.SetLineColor(kBlack)
  data_hist.SetLineWidth(1)

  print(data_hist.Integral())
  print(sig_hist.Integral())

  for h in [sig_hist, data_hist]:
    h.SetTitle("{} Signal".format(mm))
    h.GetXaxis().SetTitle("Dicluster Mass (GeV)")
    h.GetYaxis().SetTitle("Events")

  L = TLegend(0.11,0.8,0.89,0.89)
  L.SetFillColor(0)
  L.SetLineColor(0)
  L.AddEntry(sig_hist, "Signal")
  L.AddEntry(data_hist, "Data")

  c1=ROOT.TCanvas()
  c1.cd()
  FindAndSetMax([data_hist,sig_hist])
  sig_hist.Draw("hist")
  data_hist.Draw("E0same")
  c1.SetLogx()
  c1.Print("{}/signal.png".format(newDir))

  sig_hist = sfile.Get("{}_XM".format(mm))

except AttributeError:
  print("Error getting signal file")

exit()
os.system("combine "+sys.argv[1]+" -M Significance --name {}".format(comName))
os.system("combine "+sys.argv[1]+" -M AsymptoticLimits --name {}".format(comName))
F = ROOT.TFile("higgsCombine{}.AsymptoticLimits.mH120.root".format(comName))
fList.append("higgsCombine{}.AsymptoticLimits.mH120.root".format(comName))
T = F.Get("limit")
T.GetEntry(2)
exp = T.limit
T.GetEntry(4)
p2 = T.limit - exp
Lc = [0., exp, exp+p2, exp+2*p2]
Ln = ["null", "exp", "sig2", "sig4"]
os.system("combine "+sys.argv[1]+" -M FitDiagnostics --saveShapes --saveWithUncertainties --name {}".format(comName))
print Lc

F = TFile("higgsCombine{}.Significance.mH120.root".format(comName))
fList.append("higgsCombine{}.Significance.mH120.root".format(comName))
T = F.Get("limit")
T.GetEntry(0)
significance = T.limit

F = TFile("fitDiagnostics{}.root".format(comName))
print("Reading {}".format(F.GetName()))
fList.append("fitDiagnostics{}.root".format(comName))
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

os.system("combine "+sys.argv[1]+" -M GoodnessOfFit --algo=saturated --name {}".format(comName))
KS_Fs = TFile("higgsCombine{}.GoodnessOfFit.mH120.root".format(comName))
fList.append("higgsCombine{}.GoodnessOfFit.mH120.root".format(comName))
KS_Ts = KS_Fs.Get("limit")
KS_Vs = []
for i in range(0,KS_Ts.GetEntries()):
	KS_Ts.GetEntry(i)
	KS_Vs.append(KS_Ts.limit)
os.system("combine "+sys.argv[1]+" -M GoodnessOfFit --algo=saturated -t 500 --name {}".format(comName))
KS_F = TFile("higgsCombine{}.GoodnessOfFit.mH120.123456.root".format(comName))	
fList.append("higgsCombine{}.GoodnessOfFit.mH120.123456.root".format(comName))	
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
	os.system("combine "+sys.argv[1]+" -M GenerateOnly -t 500 --saveToys --toysFrequentist  --expectSignal "+str(i)+" -n _{}{} --bypassFrequentistFit ".format(j,comName))
	os.system("combine "+sys.argv[1]+" -M FitDiagnostics --bypassFrequentistFit --skipBOnlyFit -t 500 --toysFile higgsCombine_{}{}.GenerateOnly.mH120.123456.root --rMin -10 --rMax 10 --saveWorkspace -n _{}{}".format(j,comName,j,comName))
	F = ROOT.TFile("fitDiagnostics_{}{}.root".format(j,comName))
	fList.append("fitDiagnostics_{}{}.root".format(j,comName))
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

os.system("rm higgsCombine*{}*.root".format(comName))
os.system("rm fitDiagnostics*{}*.root".format(comName))

#os.system("mv *.png {}/.".format(newDir))
