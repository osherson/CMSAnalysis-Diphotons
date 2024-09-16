import ROOT
from ROOT import *
import numpy
import math
import sys
import array
import os
import time

gROOT.SetBatch()

XS = 0.001 #in pb
LUMI = 13.7 * 1000

GoodBins = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0, 2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0]

def getXPhiAlpha(signal):
   x = int(signal[1 : signal.find("A")])
   phi = float(signal[signal.find("A")+1 : ].replace("p","."))
   alpha = phi/x
   return x,phi,alpha

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

def getFracEff(anum, signal, gi):
  ffile = open("../inputs/Shapes_from{}/alphaBinning/{}/{}/alphaFraction_alpha{}_{}.txt".format(gi,anum,signal,anum,signal), "r")
  frac = float(ffile.readline())
  ffile.close()
  eff_file = open("../inputs/Shapes_from{}/alphaBinning/{}/{}/{}.txt".format(gi,anum,signal,signal), "r")
  eff = float(eff_file.readline())
  eff_file.close()
  return frac,eff

def getAlphaRange(anum, signal, gi):
  afile = open("../inputs/Shapes_from{}/alphaBinning/{}/{}/arange.txt".format(gi,anum,signal), "r")
  rr = afile.readline().rstrip()
  la = float(rr.split(",")[0])
  ha = float(rr.split(",")[-1])
  return la,ha

def PlotTogether(signal, anum, newDir):

  xm, phim, alpha = getXPhiAlpha(signal)

  sig_file_name = "../inputs/Shapes_fromInterpo/alphaBinning/{}/{}/PLOTS_{}.root".format(anum, signal, anum)
  sig_file = ROOT.TFile(sig_file_name, "read")

  gi="Interpo"

  sig_hist1 = sig_file.Get("h_AveDijetMass_1GeV")
  #sig_hist1 = sig_file.Get("{}_XM".format(signal))
  print("Initial Integral: {}".format(sig_hist1.Integral()))
  frac, eff = getFracEff(anum, signal, gi)
  lA,hA = getAlphaRange(anum, signal, gi)
  print("eff: ", eff)
  

  ScaleFactor = XS * LUMI * eff
  print("SF: ", ScaleFactor)
  sig_hist1.Scale(ScaleFactor)
  sig_hist = sig_hist1.Rebin(len(GoodBins)-1, "{}_XM".format(signal), numpy.array(GoodBins))

  #try:
  sig_hist.SetLineColor(2)
  sig_hist.SetFillColor(ROOT.kRed-10)
  
  data_hist = sig_file.Get("data_XM")

  data_hist.SetMarkerStyle(20)
  data_hist.SetMarkerSize(0.65)
  data_hist.SetLineColor(kBlack)
  data_hist.SetLineWidth(1)

  print("Data Integral: {}".format(data_hist.Integral()))
  print("Signal Integral: {}".format(sig_hist.Integral()))

  for h in [sig_hist, data_hist]:
    h.SetTitle("{} Signal".format(signal))
    h.GetXaxis().SetTitle("Dicluster Mass (GeV)")
    h.GetYaxis().SetTitle("Events")

  L = TLegend(0.11,0.8,0.89,0.89)
  L.SetFillColor(0)
  L.SetLineColor(0)
  L.AddEntry(sig_hist, "Signal")
  L.AddEntry(data_hist, "Data")

  l=ROOT.TLatex()
  l.SetTextFont(62)
  l.SetTextSize(0.055)
  l.SetNDC()

  c1=ROOT.TCanvas()
  c1.cd()
  FindAndSetMax([data_hist,sig_hist])
  sig_hist.GetYaxis().SetRangeUser(0.1, data_hist.GetMaximum()*1.25)
  data_hist.GetYaxis().SetRangeUser(0.1, data_hist.GetMaximum()*1.25)
  sig_hist.Draw("hist")
  l.DrawLatex(0.55,0.85,"{} #leq #alpha < {}".format(lA, hA))
  l.SetTextFont(42)
  l.DrawLatex(0.55,0.775,"{:.2f}% of Signal".format(frac*100))
  data_hist.Draw("E0same")
  c1.SetLogx()
  c1.SetLogy()
  c1.Print("{}/signal_and_data_{}_alpha{}.png".format(newDir,signal,anum))

  sig_file.Close()

  return

#infile = sys.argv[1]
#PlotTogether(infile, True)

