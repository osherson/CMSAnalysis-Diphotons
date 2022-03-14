import ROOT
import numpy
import os
import math
import sys
sys.path.append("../.")
#import PlottingPayload as PL

#ROOT.gROOT.SetBatch()

year = sys.argv[1]
alpha = float(sys.argv[2])


out_dir = "OutFiles/{}".format(year)

dists = {}
xmasses = []
phimasses = []

outFileName = "OutFiles/{}/alpha{}_plots.png".format(year,alpha)

for path, subdirs, files in os.walk(out_dir):
  for name in files:
    if(name[0] != "X"): continue
    File = os.path.join(path, name)
    xamass = name[:name.find(".root")]
    xmass = int(xamass[1 : xamass.find("phi")])
    phimass = float(xamass[xamass.find("phi")+3 :].replace("p",".") )
  
    if (phimass / float(xmass) == alpha):
      dists[xamass]=File
      xmasses.append(xmass)
      phimasses.append(phimass)

maxx = max(xmasses)

linelist={}
for xM  in xmasses:
  lin = ROOT.TLine(xM,0,xM,0.2)
  linelist[str(xM)] = lin


c1 = ROOT.TCanvas()
c1.cd()

legend = ROOT.TLegend(0.70,0.50,0.90,0.90)

ct = 0
for xphi, F in dists.items():
  this_x = xphi[1:xphi.find("phi")]
  #if ct >= 1: break
  known = False
  print(xphi)

  tf = ROOT.TFile(F, "read")
  hist = tf.Get(xphi)

  #ohist = tf.Get(xphi)
  #hist = ROOT.TH1F("{}hist","",500,200,1200)
  #for bb in range(0, hist.GetNbinsX()):
  #  pos = hist.GetBinLowEdge(bb)
  #  ob = ohist.GetBinContent(ohist.FindBin(pos))
  #  hist.SetBinContent(bb, ob)

  if("Known" in hist.GetTitle()): known=True

  hist.Scale(1/hist.Integral())
  hist.GetXaxis().SetRangeUser(200, 1200)
  hist.GetYaxis().SetRangeUser(0, 0.2)
  hist.SetTitle("DiCluster Mass")
  hist.GetXaxis().SetTitle("DiCluster Mass (GeV)")
  hist.GetYaxis().SetTitle("Entries")
  if known: 
    hist.SetLineColor(ROOT.kBlue)
    hist.SetFillColor(ROOT.kBlue)
    linelist[this_x].SetLineColor(ROOT.kBlue)
  else: 
    hist.SetLineColor(ROOT.kRed)
    hist.SetFillColor(ROOT.kRed)
    linelist[this_x].SetLineColor(ROOT.kRed)
  hist.SetFillStyle(3001)
  hist.GetXaxis().SetLabelSize(0.145/4)
  hist.GetXaxis().SetTitleOffset(0.75)
  hist.GetYaxis().SetTitleSize(0.175/4)
  hist.GetYaxis().SetLabelSize(0.145/4)
  hist.GetYaxis().SetTitleOffset(1)
  hist.SetStats(0)

  hist.SetDirectory(ROOT.gROOT)

  legend.AddEntry(hist, xphi)
  linelist[this_x].SetLineStyle(9)
  linelist[this_x].SetLineWidth(1)

  if(ct==0): hist.Draw("hist")
  else: hist.Draw("histsame")
  linelist[this_x].Draw("same")
  ct+=1

legend.SetBorderSize(0)
#legend.Draw("same")
ROOT.gStyle.SetLegendTextSize(0.035)

c1.Print(outFileName)
print("Saving as {}".format(outFileName))
