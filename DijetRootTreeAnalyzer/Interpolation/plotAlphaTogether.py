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

kdists = {}
kxmasses = []
kphimasses = []

outFileName = "OutFiles/{}/alpha{}_plots.png".format(year,alpha)

for path, subdirs, files in os.walk(out_dir):
  for name in files:
    if(name[0] != "X"): continue
    if(".png" in name): continue
    if("scale" in name): continue
    File = os.path.join(path, name)
    if("known" in name): 
      xamass = name[:name.find("_nom_known.root")]
      xmass = int(xamass[1 : xamass.find("phi")])
      phimass = float(xamass[xamass.find("phi")+3 :].replace("p",".") )
      if(abs(phimass / xmass - alpha) < 0.00005):
        kdists[xamass]=File
        kxmasses.append(xmass)
        kphimasses.append(phimass)

    else:
      xamass = name[:name.find("_nom.root")]
      xmass = int(xamass[1 : xamass.find("phi")])
      phimass = float(xamass[xamass.find("phi")+3 :].replace("p",".") )
      if(abs(phimass / xmass - alpha) < 0.00005):
        dists[xamass]=File
        xmasses.append(xmass)
        phimasses.append(phimass)

maxx = max(xmasses)
for xphi, kfile in kdists.items():
  #if xphi in dists:
    dists[xphi] = kfile

maxes = []
for xphi, F in dists.items():
  tf = ROOT.TFile(F, "read")
  hist = tf.Get(xphi)
  maxes.append(hist.GetMaximum())
top = 0.11
top = max(maxes)*1.15
linelist={}
allxmasses = set(xmasses + kxmasses)
for xM in allxmasses:
  lin = ROOT.TLine(xM,0,xM,top)
  linelist[str(xM)] = lin

c1 = ROOT.TCanvas()
c1.cd()

legend = ROOT.TLegend(0.70,0.50,0.90,0.90)

ct = 0

for xphi, F in dists.items():
  this_x = xphi[1:xphi.find("phi")]
  if int(this_x) > 1000: continue
  #if ct >= 1: break
  known = False
  print(xphi, F)
  
  if('known' in F):
    known=True

  tf = ROOT.TFile(F, "read")
  hist = tf.Get(xphi)

  #if known: continue
  #if known:
  #  for nx in range(0,hist.GetNbinsX()):
  #    print(nx, hist.GetBinLowEdge(nx), hist.GetBinContent(nx))

  #hist.Scale(1/hist.Integral())
  hist.GetXaxis().SetRangeUser(200, 1200)
  #hist.GetXaxis().SetRangeUser(0, 2000)
  hist.GetYaxis().SetRangeUser(0, top)
  hist.SetTitle("{} DiCluster Mass, alpha = {}".format(year, alpha))
  hist.GetXaxis().SetTitle("DiCluster Mass (GeV)")
  hist.GetYaxis().SetTitle("Entries")
  if known: 
    hist.SetLineColor(ROOT.kBlue)
    hist.SetFillColor(ROOT.kBlue)
    linelist[this_x].SetLineColor(15)
  else: 
    hist.SetLineColor(ROOT.kRed)
    hist.SetFillColor(ROOT.kRed)
    linelist[this_x].SetLineColor(15)
  hist.SetFillStyle(3001)
  hist.GetXaxis().SetTitleSize(0.175/4)
  hist.GetXaxis().SetLabelSize(0.145/4)
  hist.GetXaxis().SetTitleOffset(1)
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

#c1.SetLogy()

c1.Print(outFileName)
print("Saving as {}".format(outFileName))
