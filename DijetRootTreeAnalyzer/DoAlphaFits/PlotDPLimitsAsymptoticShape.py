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


def MakeLimitPlots(function, doAll):
  if(doAll==True): combine_dir = "combineOutput/alphaALL/"
  else: combine_dir = "shapeCombineOutput/"

  alphas = [0.005,0.01,0.015,0.02,0.025]
  #alphas = [0.01]

  for alpha in alphas:
    flist = []

    #if(alpha != 0.015 or function != "dijet"): continue

    print("Starting {} function, alpha = {}".format(function,alpha))

    for ff in os.listdir(combine_dir):
      if("_{}_".format(function) not in ff): continue
      sf = ff.split("_")
      if(doAll==True):
        xa = sf[2]
      else:
        xa = sf[1]
      this_x = int(xa[1:xa.find("A")])
      this_phi = float(xa[xa.find("A")+1 : ].replace("p","."))
      this_alpha = this_phi / float(this_x)
      if(this_alpha != alpha): continue
      flist.append([this_x, this_alpha, os.path.join(combine_dir, ff)])

    flist.sort(key=lambda row: row[0])
    for x,a,f in flist:
      print(x,a,f)

    ct = 0
    #for xm,alpha,fil in nflist:
    ct += 1
    #if (ct > 1) : break
    x = []
    obs = []
    exp = []
    p1 = []
    m1 = []
    p2 = []
    m2 = []

    for [xx,aa,ff] in flist:
      #if(aa != alpha): continue

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
        if(xx==1000):
            print(T.limit)
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
    #LimitPlot = TH2F("LP", ";Four-Photon Resonance Mass (GeV);(pp #rightarrow X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma)) #sigma #times B (fb)", 100, 300, 2000, 1000, 0.005, 50.)
    LimitPlot = TH2F("LP", ";Four-Photon Resonance Mass (GeV);(pp #rightarrow X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma)) #sigma #times B (fb)", 100, 300, 2000, 1000, 0.000005, 50.)
    LimitPlot.SetStats(0)

    LimitPlot.GetXaxis().SetMoreLogLabels(ROOT.kTRUE)

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

#   L = TLegend(0.52,0.52,0.89,0.89)
#   L.SetLineColor(0)
#   L.SetFillColor(0)
#   L.SetHeader("95% CL Limits")
#   L.AddEntry(Obs, "observed", "PL")
#   L.AddEntry(Exp, "expected", "PL")
#   L.AddEntry(Onesig, "expected #pm 1#sigma", "F")
#   L.AddEntry(Twosig, "expected #pm 2#sigma", "F")
#   L.AddEntry(TH1, "X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma) [f/N = 1]", "L")
#   L.AddEntry(TH3, "X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma) [f/N = 3]", "L")
#   L.AddEntry(TH9, "X #rightarrow #phi#phi #rightarrow (#gamma#gamma)(#gamma#gamma) [f/N = 9]", "L")

    C = TCanvas()
    C.cd()
    C.SetLogy()
    C.SetLogx()
    LimitPlot.Draw()
    Twosig.Draw("Fsames")
    Onesig.Draw("Fsames")
    TH1.Draw("Lsame")
    TH3.Draw("Lsame")
    TH9.Draw("Lsame")
    Exp.Draw("Lsame")
    Obs.Draw("LPsame")
    #L.Draw("same")
    AddCMSLumi(gPad, str(LUMI["RunII"]), "Preliminary")
    if(doAll==True):
      MakeFolder("LimitPlotsShape/ALL/{}".format(function))
      savename="LimitPlotsShape/ALL/{}/Lim_RunII_alpha{}_{}.png".format(function, str(alpha).replace(".","p"), function)
    else:
      MakeFolder("LimitPlotsShape/{}".format(function))
      savename="LimitPlotsShape/{}/Lim_RunII_alpha{}_{}.png".format(function, str(alpha).replace(".","p"), function)
    #print("Saving plot as: {}".format(savename))
    C.Print(savename)

  return

if("ALL" in sys.argv):
  functions=["dijet","atlas","dipho","moddijet"]
  for function in functions:
    MakeLimitPlots(function, True)

else:
  #function="dijet"
  functions=["dijet","atlas","dipho","moddijet","myexp"]
  for function in functions:
    MakeLimitPlots(function, False)


