import ROOT
import numpy
import os
import math
import sys
sys.path.append("../.")
#import PlottingPayload as PL

#ROOT.gROOT.SetBatch()

year = sys.argv[1]
xmass = 600

out_dir = "../inputs/Interpolations/{}/".format(year)

dists = {}
alphas = []
phimasses = []

kdists = {}
kalphas = []
kphimasses = []

outFileName = "OutFiles/{}/X{}_plots.png".format(year,xmass)

dirs = []

for path, subdirs, files in os.walk(out_dir):
  for dd in subdirs:
    if("X{}A".format(xmass) not in dd): continue
    dirs.append(os.path.join(out_dir, dd))

for dd in dirs:
  for path, subs, files in os.walk(dd):
    for name in files:
      if("nom.root" not in name): continue
      File = os.path.join(path, name)
      xamass = name[:name.find("_nom.root")]
      xmass = int(xamass[1 : xamass.find("phi")])
      phimass = float(xamass[xamass.find("phi")+3 :].replace("p",".") )
      alpha = phimass / xmass
      if(alpha < 0.005 or alpha > 0.015): continue
      if(alpha in [0.005, 0.01, 0.015]):
          kdists[xamass]=File
          kalphas.append(alpha)
          kphimasses.append(phimass)

      else:
          dists[xamass]=File
          alphas.append(alpha)
          phimasses.append(phimass)

maxx = max(alphas)
for xphi, kfile in kdists.items():
  #if xphi in dists:
    dists[xphi] = kfile

maxes = []
for xphi, F in dists.items():
  tf = ROOT.TFile(F, "read")
  hname = "{}_alpha".format(xphi)
  hist = tf.Get(hname)
  maxes.append(hist.GetMaximum())

top = 0.11
top = max(maxes)*1.15
linelist={}
allalphas = set(alphas + kalphas)
for alp in allalphas:
  lin = ROOT.TLine(alp,0,alp,top)
  linelist[str(alp)] = lin
print(linelist.keys())

c1 = ROOT.TCanvas()
c1.cd()

legend = ROOT.TLegend(0.70,0.50,0.90,0.90)

ct = 0

for xphi, F in dists.items():
  this_x = int(xphi[1:xphi.find("phi")])
  this_phi = float(xphi[xphi.find("phi")+3 :])
  this_alpha = this_phi / this_x
  #if ct >= 1: break
  known = False
  print(xphi, F)
  
  if(this_alpha in [0.005, 0.01, 0.015]):
    known=True

  tf = ROOT.TFile(F, "read")
  hname = "{}_alpha".format(xphi)
  hist = tf.Get(hname)

  #if known: continue
  #if known:
  #  for nx in range(0,hist.GetNbinsX()):
  #    print(nx, hist.GetBinLowEdge(nx), hist.GetBinContent(nx))

  #hist.Scale(1/hist.Integral())
  hist.GetXaxis().SetRangeUser(0, 0.02)
  hist.GetYaxis().SetRangeUser(0, top)
  hist.SetTitle("{} alpha shape, X Mass = {}".format(year, xmass))
  hist.GetXaxis().SetTitle("#alpha")
  hist.GetYaxis().SetTitle("Entries")
  if known: 
    hist.SetLineColor(ROOT.kBlue)
    hist.SetFillColor(ROOT.kBlue)
  else: 
    hist.SetLineColor(ROOT.kRed)
    hist.SetFillColor(ROOT.kRed)
  hist.SetFillStyle(3001)
  hist.GetXaxis().SetTitleSize(0.175/4)
  hist.GetXaxis().SetLabelSize(0.145/4)
  hist.GetXaxis().SetTitleOffset(1)
  hist.GetYaxis().SetTitleSize(0.175/4)
  hist.GetYaxis().SetLabelSize(0.145/4)
  hist.GetYaxis().SetTitleOffset(1)
  hist.SetStats(0)

  hist.SetDirectory(ROOT.gROOT)

  linelist[str(this_alpha)].SetLineColor(15)
  linelist[str(this_alpha)].SetLineStyle(9)
  linelist[str(this_alpha)].SetLineWidth(1)

  if(ct==0): hist.Draw("hist")
  else: hist.Draw("histsame")
  linelist[str(this_alpha)].Draw("same")
  ct+=1

legend.SetBorderSize(0)
#legend.Draw("same")
ROOT.gStyle.SetLegendTextSize(0.035)

#c1.SetLogy()

c1.Print(outFileName)
print("Saving as {}".format(outFileName))
