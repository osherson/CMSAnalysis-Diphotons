import ROOT
from ROOT import *
import sys
import numpy
sys.path.append('/users/h2/th544/CMSSW_11_0_0_pre2/src/PairedPairs2D/data_analysis')
import PlottingPayload as PL

DijetBins = [354., 386., 419., 453., 489., 526., 565., 606., 649., 693., 740., 788., 838., 890., 944., 1000., 1058., 1118., 1181., 1246., 1313., 1383., 1455., 1530., 1607., 1687.,1770., 1856., 1945., 2037., 2132., 2231., 2332., 2438., 2546., 2659., 2775., 2895., 3019., 3147., 3279., 3416., 3558., 3704., 3854., 4010.]

def FillFromH(O, I, s, D,  sig=False):
	b = O.FindBin(s)-1
	for i in range(1,I.GetNbinsX()+1):
		print "-----"
		print i
		x = Double(0.)
		y = Double(0.)
		D.GetPoint(i-1, x, y)
		print x, y
		iy = I.GetBinContent(i)
		print iy
		if not sig:
			if iy > y: e = D.GetErrorYhigh(i-1)
			else: e = D.GetErrorYlow(i-1)
			O.SetBinContent(i+b, (y - iy)/e)
		else:
			e = D.GetErrorYhigh(i-1)
			O.SetBinContent(i+b, iy/e)
		
def Canv(s, B, BS, S):
	n = sys.argv[1].split(".")[0].split("_")[-1]
	S.SetLineColor(1)
	S.SetLineWidth(2)
	BS.SetLineColor(kRed)
	B.SetLineColor(kBlue)
	BS.SetFillColor(kRed)
	B.SetFillColor(kBlue)
	B.GetYaxis().CenterTitle(True)
	BS.SetFillStyle(3004)
	B.SetFillStyle(3005)
	B.GetYaxis().SetRangeUser(-4.,4.)
	B.SetStats(0)
	L = TLegend(0.14,0.11,0.86,0.19)
	L.SetLineColor(0)
	L.SetFillColor(0)
	L.SetNColumns(3)
	L.AddEntry(B, "bkg only fit", "F")
	L.AddEntry(BS, "sig+bkg fit", "F")
	L.AddEntry(S, "stop (m = "+n.split("M")[1]+" GeV)", "L")
 	gStyle.SetCanvasColor(0)
	C = TCanvas()
	C.cd()
	P = TPad()
	P.SetGridy()
 	P.SetFillColor(0)
	P.Draw()
	P.cd()
	B.Draw("hist")
	BS.Draw("histsame")
	S.Draw("histsame")
	L.Draw("same")
	PL.AddCMSLumi(P, 137.5, "Preliminary")
	C.Print("/users/h2/th544/CMSSW_11_0_0_pre2/src/PairedPairs2D/data_analysis/combineHelper/postfit/BvSFit_"+n+"_"+s+".png")
	
B0 = TH1F("B0", "slice 1;Average Dijet Mass (GeV);#frac{data - bkg}{#sigma_{data}}", len(DijetBins) - 1, numpy.array(DijetBins))
B1 = TH1F("B1", "slice 2;Average Dijet Mass (GeV);#frac{data - bkg}{#sigma_{data}}", len(DijetBins) - 1, numpy.array(DijetBins))
B2 = TH1F("B2", "slice 3;Average Dijet Mass (GeV);#frac{data - bkg}{#sigma_{data}}", len(DijetBins) - 1, numpy.array(DijetBins))
BS0 = TH1F("BS0", ";Average Dijet Mass (GeV);", len(DijetBins) - 1, numpy.array(DijetBins))
BS1 = TH1F("BS1", ";Average Dijet Mass (GeV);", len(DijetBins) - 1, numpy.array(DijetBins))
BS2 = TH1F("BS2", ";Average Dijet Mass (GeV);", len(DijetBins) - 1, numpy.array(DijetBins))
S0 = TH1F("S0", ";Average Dijet Mass (GeV);", len(DijetBins) - 1, numpy.array(DijetBins))
S1 = TH1F("S1", ";Average Dijet Mass (GeV);", len(DijetBins) - 1, numpy.array(DijetBins))
S2 = TH1F("S2", ";Average Dijet Mass (GeV);", len(DijetBins) - 1, numpy.array(DijetBins))

F = TFile(sys.argv[1])
Ds0 = F.Get("shapes_prefit/ch1/data")
Ds1 = F.Get("shapes_prefit/ch2/data")
Ds2 = F.Get("shapes_prefit/ch3/data")
Bs0 = F.Get("shapes_fit_b/ch1/total_background")
Bs1 = F.Get("shapes_fit_b/ch2/total_background")
Bs2 = F.Get("shapes_fit_b/ch3/total_background")
BSs0 = F.Get("shapes_fit_s/ch1/total_background")
BSs1 = F.Get("shapes_fit_s/ch2/total_background")
BSs2 = F.Get("shapes_fit_s/ch3/total_background")
Ss0 = F.Get("shapes_fit_s/ch1/total_signal")
Ss1 = F.Get("shapes_fit_s/ch2/total_signal")
Ss2 = F.Get("shapes_fit_s/ch3/total_signal")

FillFromH(B0, Bs0, 354.0, Ds0)
FillFromH(B1, Bs1, 526.0, Ds1)
FillFromH(B2, Bs2, 606.0, Ds2)
FillFromH(BS0, BSs0, 354.0, Ds0)
FillFromH(BS1, BSs1, 526.0, Ds1)
FillFromH(BS2, BSs2, 606.0, Ds2)
FillFromH(S0, Ss0, 354.0, Ds0, True)
FillFromH(S1, Ss1, 526.0, Ds1, True)
FillFromH(S2, Ss2, 606.0, Ds2, True)

Canv("0", B0, BS0, S0)
Canv("1", B1, BS1, S1)
Canv("2", B2, BS2, S2)