import ROOT
from ROOT import *
from array import array
import os
import numpy

def GetTH(fN):
	
	TH = TGraph()
	TH.SetPoint(TH.GetN(),100., 335515./fN/fN)
	TH.SetPoint(TH.GetN(),150., 69155./fN/fN)
	TH.SetPoint(TH.GetN(),200., 21362.1/fN/fN)
	TH.SetPoint(TH.GetN(),250., 8304.88/fN/fN)
	TH.SetPoint(TH.GetN(),300., 3746.96/fN/fN)
	TH.SetPoint(TH.GetN(),350., 1878.15/fN/fN)
	TH.SetPoint(TH.GetN(),400., 1017.87/fN/fN)
	TH.SetPoint(TH.GetN(),450., 585.983/fN/fN)
	TH.SetPoint(TH.GetN(),500., 353.898/fN/fN)
	TH.SetPoint(TH.GetN(),625., 117.508/fN/fN)
	TH.SetPoint(TH.GetN(),750., 45.9397/fN/fN)
	TH.SetPoint(TH.GetN(),875., 20.1308/fN/fN)
	TH.SetPoint(TH.GetN(),1000., 9.59447/fN/fN)
	TH.SetPoint(TH.GetN(),1125., 4.88278/fN/fN)
	TH.SetPoint(TH.GetN(),1250., 2.61745/fN/fN)
	TH.SetPoint(TH.GetN(),1375., 1.46371/fN/fN)
	TH.SetPoint(TH.GetN(),1500., 0.847454/fN/fN)
	TH.SetPoint(TH.GetN(),1625., 0.505322/fN/fN)
	TH.SetPoint(TH.GetN(),1750., 0.309008/fN/fN)
	TH.SetPoint(TH.GetN(),1875., 0.192939/fN/fN)
	TH.SetPoint(TH.GetN(),2000., 0.122826/fN/fN)
	TH.SetPoint(TH.GetN(),2125., 0.0795248/fN/fN)
	TH.SetPoint(TH.GetN(),2250., 0.0522742/fN/fN)
	TH.SetPoint(TH.GetN(),2375., 0.0348093/fN/fN)
	TH.SetPoint(TH.GetN(),2500., 0.0235639/fN/fN)
	TH.SetPoint(TH.GetN(),2625., 0.0161926/fN/fN)
	TH.SetPoint(TH.GetN(),2750., 0.0109283/fN/fN)
	TH.SetPoint(TH.GetN(),2875., 0.00759881/fN/fN)
	TH.SetPoint(TH.GetN(),3000., 0.00531361/fN/fN)
	return TH

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


x = []
obs = []
exp = []
p1 = []
m1 = []
p2 = []
m2 = []

xmlist = numpy.linspace(250,3000,(3000-250)//10 + 1)
xmlist = [int(xx) for xx in xmlist]

xmlist_have = []
for xx in xmlist:
  if(os.path.exists("combineOutput/2018/X{}.root".format(xx))):
    xmlist_have.append(xx)

#for m in ['300', '400', '500', '600', '750', '1000', '1500', '2000', '3000']:
for m in xmlist_have:
	F = TFile('combineOutput/2018/X{}.root'.format(m))
	T = F.Get("limit")
	n = T.GetEntries()
	if n == 6:
		x.append(float(m))
		T.GetEntry(5)
		obs.append(T.limit)
		T.GetEntry(0)
		m2.append(T.limit)
		T.GetEntry(1)
		m1.append(T.limit)
		T.GetEntry(2)
		exp.append(T.limit)
		T.GetEntry(3)
		p1.append(T.limit)
		T.GetEntry(4)
		p2.append(T.limit)

#LimitPlot = TH2F("LP", ";Four-Photon Resonance Mass (GeV);(pp #rightarrow X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma)) #sigma #times B (fb)", 100, 300, 3000, 100, 0.005, 50.)
LimitPlot = TH2F("LP", ";Four-Photon Resonance Mass (GeV);(pp #rightarrow X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma)) #sigma #times B (fb)", 100, 300, 2000, 100, 0.05, 50.)
LimitPlot.SetStats(0)

TH1 = GetTH(1)
TH3 = GetTH(3)
TH9 = GetTH(9)

Obs = TGraph(len(x), numpy.array(x), numpy.array(obs))
Exp = TGraph(len(x), numpy.array(x), numpy.array(exp))
Exp.SetLineStyle(2)
TH1.SetLineStyle(4)
TH1.SetLineColor(kBlue)
TH3.SetLineStyle(5)
TH3.SetLineColor(kBlue)
TH9.SetLineStyle(6)
TH9.SetLineColor(kBlue)
Obs.SetLineColor(kBlack)
Obs.SetMarkerStyle(20)
Obs.SetMarkerSize(0.6666)
Onesig = makeAFillGraph(x,m1,p1,kGreen,kGreen, 1001)
Twosig = makeAFillGraph(x,m2,p2,kYellow,kYellow, 1001)

L = TLegend(0.5,0.5,0.89,0.89)
L.SetLineColor(0)
L.SetFillColor(0)
L.SetHeader("95% CL Limits")
L.AddEntry(Obs, "observed", "PL")
L.AddEntry(Exp, "expected", "PL")
L.AddEntry(Onesig, "expected #pm 1#sigma", "F")
L.AddEntry(Twosig, "expected #pm 2#sigma", "F")
L.AddEntry(TH1, "X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma) [f/N = 1]", "L")
L.AddEntry(TH3, "X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma) [f/N = 3]", "L")
L.AddEntry(TH9, "X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma) [f/N = 9]", "L")

C = TCanvas()
C.cd()
C.SetLogy()
LimitPlot.Draw()
Twosig.Draw("Fsames")
Onesig.Draw("Fsames")
TH1.Draw("Lsame")
TH3.Draw("Lsame")
TH9.Draw("Lsame")
Exp.Draw("Lsame")
Obs.Draw("LPsame")
#L.Draw("same")
AddCMSLumi(gPad, 5.99, "Preliminary")
C.Print("LIM.png")
