import ROOT
from ROOT import *
import numpy
import math
import sys
import array
import os
import time
import PlotDataSigTogether as PT

#gROOT.SetBatch()

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

def GetUnbinnedData():
  data_hist = TH1F('data','data',len(GoodBins)-1, numpy.array(GoodBins))
  for (ii,ab) in enumerate(os.listdir("../inputs/Shapes_DATA/alphaBinning/")):
    hfile = TFile("../inputs/Shapes_DATA/alphaBinning/{}/DATA.root".format(ab), "read")
    dhist = hfile.Get("data_XM")
    data_hist.Add(dhist)
    hfile.Close()
  return data_hist

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

def getFracEff(anum, mm, gi):
  ffile = open("../inputs/Shapes_from{}/alphaBinning/{}/{}/alphaFraction_alpha{}_{}.txt".format(gi,anum,mm,anum,mm), "r")
  frac = float(ffile.readline())
  ffile.close()
  eff_file = open("../inputs/Shapes_from{}/alphaBinning/{}/{}/{}.txt".format(gi,anum,mm,mm), "r")
  eff = float(eff_file.readline())
  eff_file.close()
  return frac,eff

def getAlphaRange(anum, mm, gi):
  afile = open("../inputs/Shapes_from{}/alphaBinning/{}/{}/arange.txt".format(gi,anum,mm), "r")
  rr = afile.readline().rstrip()
  la = float(rr.split(",")[0])
  ha = float(rr.split(",")[-1])
  return la,ha

def getNChannel(f):
  F = open(f,"r")
  for lin in F.readlines():
    if(lin.startswith("bin")):
      var = list(set(lin.split(" ")))
  ch = []
  for v in var:
    if("ch" in v): ch.append(v)
  return len(ch)

infile = sys.argv[1]
print(infile)
cps = infile[infile.rfind("/"):]
cps = cps.split("_")
an = "alphaAll"
mm = cps[0][1:]
print(an, mm)
anum = an


comName = "_{}_{}".format(an,mm)

newDir = "combineOutputEnvelope/{}".format(mm)
os.system("mkdir -p {}".format(newDir))

#PT.PlotTogether(infile, False)

os.system("combine "+sys.argv[1]+" -M Significance --name {}".format(comName))
os.system("combine "+sys.argv[1]+" -M AsymptoticLimits --name {}".format(comName))
F = ROOT.TFile("higgsCombine{}.AsymptoticLimits.mH120.root".format(comName))
T = F.Get("limit")
T.GetEntry(2)
exp = T.limit
T.GetEntry(4)
p2 = T.limit - exp
Lc = [0., exp, exp+p2, exp+2*p2]
Ln = ["null", "exp", "sig2", "sig4"]
os.system("combine "+sys.argv[1]+" -M FitDiagnostics --saveShapes --saveWithUncertainties --name {}".format(comName))

#Lc = [0.,1.]
#Ln = ["null","one"]
print Lc

#F = TFile("higgsCombine{}.Significance.mH120.root".format(comName))
#T = F.Get("limit")
#T.GetEntry(0)
#significance = T.limit

################################################################################
#This doesnt work

#F = TFile("fitDiagnostics{}.root".format(comName))
#print("Reading {}".format(F.GetName()))
#nchan = getNChannel(infile)
#for nc in range(1,nchan+1):
#  data = F.Get("shapes_prefit/data")
#  data = convertAsymGraph(F.Get("shapes_prefit/ch{}/data".format(nc)), Template, "data")
#  b = convertBinNHist(F.Get("shapes_fit_b/ch{}/total_background".format(nc)), Template, "b")
#  s = convertBinNHist(F.Get("shapes_fit_s/ch{}/total_background".format(nc)), Template, "splusb")
#  sig = convertBinNHist(F.Get("shapes_fit_s/ch{}/total".format(nc)), Template, "sig")
#
#  data.SetMarkerStyle(20)
#  data.SetMarkerSize(0.65)
#  data.SetLineColor(kBlack)
#  data.SetLineWidth(1)
#  b.SetLineColor(kBlue)
#  b.SetLineWidth(3)
#  s.SetLineColor(kRed)
#  s.SetLineWidth(3)
#  sig.SetLineWidth(3)
#  s.SetLineStyle(2)
#  sig.SetLineColor(kRed)
#
#  bP = MakePull(data, b, kBlue, "BP")
#  sP = MakePull(data, sig, kRed, "SP")
#
#
#  L = TLegend(0.6,0.7,0.89,0.89)
#  L.SetFillColor(0)
#  L.SetLineColor(0)
#  L.AddEntry(data, "Data", "PL")
#  L.AddEntry(b, "Bkg in B fit", "L")
#  L.AddEntry(s, "Bkg in S+B fit", "L")
#  L.AddEntry(sig, "Total in S+B fit (S = %.2f #sigma)"%significance, "L")
#
#  for h in [data, b, s, sig]:
#	  h = DBBW(h)
#  FindAndSetMax(data,b,s,sig,Template)
#
#  C = TCanvas("T", "", 500, 500)
#  C.cd()
#  p12 = TPad("pad1", "tall",0,0.165,1,1)
#  p22 = TPad("pad2", "short",0,0.0,1.0,0.235)
#  p22.SetBottomMargin(0.35)
#  p12.Draw()
#  p22.Draw()
#  p12.cd()
#  p12.SetLogx()
#  Template.Draw()
#  b.Draw("histsame")
#  s.Draw("histsame")
#  sig.Draw("histsame")
#  data.Draw("e0same")
#  L.Draw("same")
#  gPad.SetTicks(1,1)
#  gPad.RedrawAxis()
#  p22.cd()
#  p22.SetLogx()
#  PullTemplate.Draw()
#  PullTemplate.GetXaxis().SetMoreLogLabels()
#  bP.Draw("histsame")
#  sP.Draw("histsame")
#  gPad.SetTicks(1,1)
#  gPad.RedrawAxis()
#  C.Print("{}/PostFits_{}_{}_ch{}.png".format(newDir,an,mm,nc))
#  C.Print("{}/PostFits_{}_{}_ch{}.root".format(newDir,an,mm,nc))

################################################################################

################################################################################
#This works, comment to save time
#os.system("combine "+sys.argv[1]+" -M GoodnessOfFit --algo=saturated --name {}".format(comName))
#KS_Fs = TFile("higgsCombine{}.GoodnessOfFit.mH120.root".format(comName))
#KS_Ts = KS_Fs.Get("limit")
#KS_Vs = []
#for i in range(0,KS_Ts.GetEntries()):
#	KS_Ts.GetEntry(i)
#	KS_Vs.append(KS_Ts.limit)
#os.system("combine "+sys.argv[1]+" -M GoodnessOfFit --algo=saturated -t 500 --name {}".format(comName))
#KS_F = TFile("higgsCombine{}.GoodnessOfFit.mH120.123456.root".format(comName))	
#KS_T = KS_F.Get("limit")
#KS_V = []
#for i in range(0,KS_T.GetEntries()):
#	KS_T.GetEntry(i)
#	KS_V.append(KS_T.limit)
#minKS = min(min(KS_V),min(KS_Vs))
#maxKS = max(max(KS_V),max(KS_Vs))
#rangeKS = maxKS - minKS
#KS_plot = TH1F("KS_plot", ";Goodness Of Fit Statistic (Saturated);toys", 50, minKS-(rangeKS/7.), maxKS+(rangeKS/7.))
#KS_plot.SetStats(0)
#for i in KS_V: KS_plot.Fill(i)
#
#KS_plot.SetMarkerStyle(20)
#KS_plot.SetLineColor(kBlack)
#
#KS_mk = TLine(KS_Vs[0], 0., KS_Vs[0], KS_plot.GetMaximum()*0.4)
#KS_mk.SetLineColor(ROOT.kBlue)
#KS_mk.SetLineWidth(3)
#
#FitFunc = TF1("FitFunc", "gaus", minKS-(rangeKS/7.), maxKS+(rangeKS/7.))
#KS_plot.Fit(FitFunc, "EMR0")
#FitFunc.SetLineStyle(2)
#
#sigma = (KS_Vs[0] - FitFunc.GetParameter(1))/FitFunc.GetParameter(2)
#L2 = TLegend(0.667,0.75,0.89,0.89)
#L2.SetLineColor(0)
#L2.SetFillColor(0)
#L2.AddEntry(KS_mk, "GOF: %.2f #sigma"%sigma, "L")
#
#C_KS = TCanvas()
#C_KS.cd()
#KS_plot.Draw("e")
#FitFunc.Draw("same")
#KS_mk.Draw("same")
#L2.Draw("same")
#gPad.SetTicks(1,1)
#gPad.RedrawAxis()
#C_KS.Print("{}/GoF_{}_{}.png".format(newDir,an,mm))
#C_KS.Print("{}/GoF_{}_{}.root".format(newDir,an,mm))

print("Before loop")

for i,j in zip(Lc,Ln):
  import os #it is weird that I have to do this
  print(i,j)
  for pdfi in [0,1,2,3,4,5]:
  #for pdfi in [0]:
    os.system("combine "+sys.argv[1]+" -M GenerateOnly -t 500 --saveToys --toysFrequentist --freezeParameters rgx{pdf_*} --setParameters rgx{pdf_*}=%s --expectSignal %s -n _%s%s --bypassFrequentistFit"% (pdfi, i, j,comName))

  os.system("combine "+sys.argv[1]+" -M FitDiagnostics --cminDefaultMinimizerStrategy=0 --skipBOnlyFit -t 500 --toysFile higgsCombine_%s%s.GenerateOnly.mH120.123456.root --rMin -10 --rMax 10 --saveWorkspace -n _%s%s --bypassFrequentistFit "%(j,comName,j,comName))

#####

  #Works on individual card
  #os.system("combine "+sys.argv[1]+" -M GenerateOnly -t 100 --saveToys --toysFrequentist  --expectSignal "+str(i)+" -n _{}{} --bypassFrequentistFit ".format(j,comName))
  #os.system("combine "+sys.argv[1]+" -M FitDiagnostics --bypassFrequentistFit --skipBOnlyFit -t 100 --toysFile higgsCombine_{}{}.GenerateOnly.mH120.123456.root --rMin -10 --rMax 10 --saveWorkspace -n_{}{} --cminDefaultMinimizerStrategy=0 ".format(j,comName,j,comName))

####

  F = ROOT.TFile("fitDiagnostics_{}{}.root".format(j,comName))
  T = F.Get("tree_fit_sb")
  H = ROOT.TH1F("Bias Test, injected r="+j, ";(#mu_{measured} - #mu_{injected})/#sigma_{#mu};toys", 50, -5., 5.)
  #T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test, injected r=" + j)
  #T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test, injected r=" + j)
  #T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test, injected r=" + j, "fit_status>0")
  #T.Draw("(r-%f)/((rHiErr*(r-%f<0)+rLoErr*(r-%f>0)))"%(i,i,i)+">>Bias Test, injected r=" + j, "fit_status>0")
  T.Draw("(r-%f)/((rHiErr*(r-%f<0)+rLoErr*(r-%f>0)))"%(i,i,i)+">>Bias Test, injected r=" + j, "fit_status>=0")
  #T.Draw("(r)/((rHiErr*(r<0)+rLoErr*(r>0)))>>Bias Test, injected r=" + j, "fit_status>0")
  G = ROOT.TF1("f", "gaus(0)", -5.,5.)
  H.Fit(G)
  ROOT.gStyle.SetOptFit(1111)
  cbb = ROOT.TCanvas()
  cbb.cd()
  H.Draw("e0")
  sname = newDir+"/"+j+"_{}_{}".format(an,mm)
  cbb.Print("{}.png".format(sname))
  cbb.Print("{}.root".format(sname))
  print("Saving as: {}".format(sname))
  os.system("rm higgsCombine*{}*.root".format(comName))
  os.system("mv fitDiagnostics*{}*.root {}/fitDiagnostics_comName_j".format(comName))

#  print("Starting my stuff")
#  Hm1 = ROOT.TH1F("Bias Test,fm1, injected r="+j, ";(#mu_{measured} - #mu_{injected})/#sigma_{#mu};toys", 50, -5., 5.)
#  H0 = ROOT.TH1F("Bias Test,f0, injected r="+j, ";(#mu_{measured} - #mu_{injected})/#sigma_{#mu};toys", 50, -5., 5.)
#  Hp1 = ROOT.TH1F("Bias Test,fp1, injected r="+j, ";(#mu_{measured} - #mu_{injected})/#sigma_{#mu};toys", 50, -5., 5.)
#  T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test,fm1, injected r=" + j, "fit_status == -1")
#  T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test,f0, injected r=" + j, "fit_status == 0")
#  T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test,fp1, injected r=" + j, "fit_status == 1")
#  Hm1.SetMarkerColor(ROOT.kRed)
#  Hm1.SetMarkerStyle(20)
#  H0.SetMarkerColor(ROOT.kBlue)
#  H0.SetMarkerStyle(21)
#  Hp1.SetMarkerColor(ROOT.kBlack)
#  Hp1.SetMarkerStyle(22)
#
#  cfm1 = ROOT.TCanvas()
#  cfm1.cd()
#  Gm1 = ROOT.TF1("fm1", "gaus(0)", -5.,5.)
#  Hm1.Fit(Gm1)
#  ROOT.gStyle.SetOptFit(1111)
#  Hm1.Draw("e0")
#  fname = newDir+"/{}_fitstatusm1_{}_{}".format(j,an,mm)
#  cfm1.Print("{}.png".format(fname))
#  cfm1.Print("{}.root".format(fname))
#
#  cfp1 = ROOT.TCanvas()
#  cfp1.cd()
#  Gp1 = ROOT.TF1("fp1", "gaus(0)", -5.,5.)
#  Hp1.Fit(Gp1)
#  ROOT.gStyle.SetOptFit(1111)
#  Hp1.Draw("e0")
#  fname = newDir+"/{}_fitstatusp1_{}_{}".format(j,an,mm)
#  cfp1.Print("{}.png".format(fname))
#  cfp1.Print("{}.root".format(fname))
#
#  cf0 = ROOT.TCanvas()
#  cf0.cd()
#  G0 = ROOT.TF1("f0", "gaus(0)", -5.,5.)
#  H0.Fit(G0)
#  ROOT.gStyle.SetOptFit(1111)
#  H0.Draw("e0")
#  fname = newDir+"/{}_fitstatus0_{}_{}".format(j,an,mm)
#  cf0.Print("{}.png".format(fname))
#  cf0.Print("{}.root".format(fname))
#
#  Leg = ROOT.TLegend(0.1,0.65,0.4,0.88)
#  cff = ROOT.TCanvas()
#  cff.cd()
#  Leg.AddEntry(Hm1, "fit_status==-1")
#  Leg.AddEntry(H0, "fit_status==0")
#  Leg.AddEntry(Hp1, "fit_status==+1")
#  Hm1.SetStats(0)
#  H0.SetStats(0)
#  Hp1.SetStats(0)
#  Hm1.Draw("e0")
#  Hp1.Draw("e0same")
#  H0.Draw("e0same")
#  Leg.Draw("same")
#  fname = newDir+"/{}_fitstatus_{}_{}".format(j,an,mm)
#  cff.Print("{}.png".format(fname))

  #break

print("\nhere\n")

#os.system("mv *.png {}/.".format(newDir))
