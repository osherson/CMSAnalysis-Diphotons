import ROOT
from ROOT import *
from array import array
import os
import numpy
import sys

gROOT.SetBatch()

LUMI = {}
LUMI["2016"] = 3.59
LUMI["2017"] = 4.15
LUMI["2018"] = 5.99
LUMI["RunII"] = sum([LUMI[yy] for yy in LUMI.keys()])

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

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

def AddAlphaRange(pad, sa):
  #sl = "{:.5f}".format(al)
  #sh = "{:.5f}".format(ah)
  #aText     = "%s < #alpha #leq %s"%(sl,sh)
  ssa = "{:.3f}".format(sa)
  aText = "Signal  #alpha = %s"%(ssa)
  lumiTextSize     = 0.45
  lumiTextOffset   = 0.15
  H = pad.GetWh()
  W = pad.GetWw()
  l = pad.GetLeftMargin()
  t = pad.GetTopMargin()
  r = pad.GetRightMargin()
  b = pad.GetBottomMargin()
  e = 0.025
  latex = TLatex()
  latex.SetNDC()
  latex.SetTextAngle(0)
  latex.SetTextColor(kBlack)	
  latex.SetTextFont(62)
  latex.SetTextAlign(31) 
  latex.SetTextSize(lumiTextSize*t)	
  pad.cd()
  latex.SetTextAlign(11)
  latex.DrawLatex(0.1265, 1-t+lumiTextOffset*t, aText)
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


def GetExpLimit(combine_dir, sig_alpha):

  alphas = []
  flist = []
  for ff in os.listdir(combine_dir):
    for xa in ff.split("_"):
      if(xa.startswith("X")):
        if("." in xa): xa = xa[ : xa.rfind(".")]
        this_x = int(xa[1:xa.find("A")])
        this_phi = float(xa[xa.find("A")+1 :].replace("p","."))
        this_alpha = round(this_phi / float(this_x),3)
        if(this_alpha != sig_alpha): continue
        alphas.append(this_alpha)
        flist.append([this_x, this_alpha, os.path.join(combine_dir, ff)])

  alphas = set(alphas)
  print(alphas)
  nflist = numpy.array( [ numpy.array(xi) for xi in flist ] ) #Convert to np array for later selection
  lset = list(alphas)
  useflist = nflist[ nflist[:,1]==str(sig_alpha) ] #select alpha
  useflist = [ (int(xx), float(aa), str(ff)) for (xx,aa,ff) in useflist ] #Convert back to python list, convert x, alpha to int, float
  useflist.sort(key=lambda row: row[0]) #sort by xmass

  x = []
  obs = []
  exp = []
  p1 = []
  m1 = []
  p2 = []
  m2 = []

  print("Num points: {}".format(len(useflist)))

  for [xx,aa,ff] in useflist:
    if(aa != sig_alpha): continue
    #print(xx,aa,ff)

    #F = TFile('combineOutput/{}/X{}.root'.format(year,m))
    F = TFile(ff)
    try:
      T = F.Get("limit")
      n = T.GetEntries()
    except AttributeError:
      print("Trouble with {}, Skipping.".format(F.GetName()))
      continue
    if n == 6:
      x.append(float(xx))
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


  return x, exp, m1, p1

def MakeLimitPlot(x1, exp1, mg1, pg1, x2, exp2, sig_alpha):
  LimitPlot = TH2F("LP", "Expected Limits;Four-Photon Resonance Mass (GeV);(pp #rightarrow X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma)) #sigma #times B (fb)", 100, 300, 3200, 1000, 0.005, 5000.)
  LimitPlot.SetStats(0)
  LimitPlot.GetXaxis().SetMoreLogLabels(ROOT.kTRUE)

  TH1 = GetTH(1)
  TH3 = GetTH(3)
  TH9 = GetTH(9)
  TH1.SetLineStyle(4)
  TH1.SetLineColor(kBlue)
  TH3.SetLineStyle(5)
  TH3.SetLineColor(kBlue)
  TH9.SetLineStyle(6)
  TH9.SetLineColor(kBlue)

  Exp1 = TGraph(len(x1), numpy.array(x1), numpy.array(exp1))
  Exp1.SetLineStyle(1)
  Exp1.SetLineWidth(3)
  Exp1.SetLineColor(kBlack)
  Exp1.SetMarkerStyle(20)
  Exp1.SetMarkerColor(kBlack)

  Onesig = makeAFillGraph(x1,mg1,pg1,kGreen,kGreen, 1001)

  Exp2 = TGraph(len(x2), numpy.array(x2), numpy.array(exp2))
  Exp2.SetLineStyle(kDashed)
  Exp2.SetLineWidth(3)
  Exp2.SetMarkerStyle(21)
  Exp2.SetMarkerColor(6)
  Exp2.SetLineColor(6)

  L = TLegend(0.62,0.62,0.89,0.89)
  L.SetLineColor(0)
  L.SetFillColor(0)
  L.AddEntry(Exp1, "Generated Shapes", "PL")
  L.AddEntry(Onesig, "expected #pm 1#sigma (gen)", "F")
  L.AddEntry(Exp2, "InterpolatedShapes", "PL")

  C = TCanvas()
  C.cd()
  C.SetLogy()
  C.SetLogx()
  LimitPlot.Draw()
  #TH1.Draw("Lsame")
  #TH3.Draw("Lsame")
  #TH9.Draw("Lsame")
  Onesig.Draw("Fsame")
  Exp1.Draw("LPsame")
  Exp2.Draw("LPsame")
  L.Draw("same")
  AddCMSLumi(gPad, str(LUMI["RunII"]), "Preliminary")
  AddAlphaRange(gPad,  sig_alpha)
  MakeFolder("LimitPlots/")
  savename="LimitPlots/Compare/Lim_RunII_alpha{}.png".format(str(sig_alpha).replace(".","p"))
  #print("Saving plot as: {}".format(savename))
  C.Print(savename)

  for (xx1, ex1, xx2, ex2) in zip(x1,exp1,x2,exp2):
    print(xx1, ex1, xx2, ex2)

  return

gen_dir = "combineOutput/gen_norm/"
int_dir = "combineOutput/int_Jan31_Full/"
for sa in [0.005, 0.01, 0.015, 0.02, 0.025]:
  x1,exp1,m1,p1 = GetExpLimit(gen_dir, sa)
  x2,exp2,_,_ = GetExpLimit(int_dir, sa)
  MakeLimitPlot(x1,exp1,m1,p1,x2,exp2, sa)
