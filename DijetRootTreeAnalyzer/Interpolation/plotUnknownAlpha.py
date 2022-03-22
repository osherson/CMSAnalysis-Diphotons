import ROOT
import numpy
import os
import math
import sys
sys.path.append("../.")
#import PlottingPayload as PL

#ROOT.gROOT.SetBatch()

infile = sys.argv[1]
year = infile[infile.find("201") : infile.find("201")+4]

out_dir = "OutFiles/{}".format(year)

xphi = infile[infile.rfind("/")+1 : infile.find(".root") ]
xmass = float(xphi[1:xphi.find("phi")])
phimass = float(xphi[xphi.find("phi")+3 :])
if xmass.is_integer(): xmass = int(xmass)
if phimass.is_integer(): phimass = int(phimass)
print(xphi)

outFileName = "OutFiles/{}/X{}phi{}_compareplots.png".format(year, xmass, phimass)

myfile = ROOT.TFile(infile, "read")
hists = []
hists.append(myfile.Get(xphi))

histnames = []
for key in myfile.GetListOfKeys():
  if "original" in key.GetName() and key.GetName() not in histnames: 
    hists.append(myfile.Get(key.GetName()))
    histnames.append(key.GetName())


hmaxes = [h.GetMaximum() for h in hists]
top = max(hmaxes) * 1.15

lin = ROOT.TLine(xmass,0,xmass,top)

c1 = ROOT.TCanvas()
c1.cd()

legend = ROOT.TLegend(0.70,0.50,0.90,0.90)

ct = 0
for hist in hists:
  known = False
  
  if('original' in hist.GetName()):
    known=True

  hist.GetXaxis().SetRangeUser(0.75*xmass, 1.25*xmass)
  hist.GetYaxis().SetRangeUser(0.01, top)
  hist.SetTitle("{} DiCluster Mass, X {} phi {}".format(year, xmass, phimass))
  hist.GetXaxis().SetTitle("DiCluster Mass (GeV)")
  hist.GetYaxis().SetTitle("Entries")
  if known: 
    hist.SetLineColor(ROOT.kBlue)
    hist.SetFillColor(ROOT.kBlue)
    hist.SetFillStyle(3001)
    legend.AddEntry(hist, "Generated")
  else: 
    hist.SetLineColor(ROOT.kRed)
    hist.SetFillColor(ROOT.kRed)
    hist.SetFillStyle(0)
    hist.SetLineWidth(2)
    legend.AddEntry(hist, "Interpolated")
  hist.GetXaxis().SetLabelSize(0.145/4)
  hist.GetXaxis().SetTitleOffset(0.75)
  hist.GetYaxis().SetTitleSize(0.175/4)
  hist.GetYaxis().SetLabelSize(0.145/4)
  hist.GetYaxis().SetTitleOffset(1)
  hist.SetStats(0)

  hist.SetDirectory(ROOT.gROOT)

  if(ct==0): hist.Draw("hist")
  else: hist.Draw("histsame")
  ct+=1

lin.SetLineStyle(9)
lin.SetLineColor(15)
lin.SetLineWidth(1)
lin.Draw("same")

legend.SetBorderSize(0)
legend.Draw("same")
ROOT.gStyle.SetLegendTextSize(0.035)

#c1.SetLogy()

c1.Print(outFileName)
print("Saving as {}".format(outFileName))
