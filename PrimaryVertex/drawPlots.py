#
import ROOT
from ROOT import *
import sys,os
import glob
import numpy


year = sys.argv[1]
nFile = TFile("outFiles/{}/vertices.root".format(year), "read")

dhist = nFile.Get("npv_data")
shist = nFile.Get("npv_signal")

dhist.Scale(1/dhist.Integral())
shist.Scale(1/shist.Integral())

dhist.SetTitle("NPvtx, {}; npvtx; entries".format(year))
shist.SetTitle("NPvtx, {}; npvtx; entries".format(year))

amax = max(dhist.GetMaximum(), shist.GetMaximum())
dhist.GetYaxis().SetRangeUser(0, 1.15*amax)
shist.GetYaxis().SetRangeUser(0, 1.15*amax)

c1 = ROOT.TCanvas()
c1.cd()
legend = TLegend(0.75,0.75,0.90,0.90)

dhist.SetLineColor(4)
dhist.SetLineWidth(2)
dhist.SetStats(0)
legend.AddEntry(dhist, "Data")

shist.SetLineColor(46)
shist.SetLineWidth(2)
shist.SetStats(0)
legend.AddEntry(shist, "Signal")

dhist.SetDirectory(gROOT)
shist.SetDirectory(gROOT)
dhist.Draw("hist")
shist.Draw("histsame")

legend.SetTextSize(0.035)
legend.Draw("same")

c1.Print("Plots/{}/together.png".format(year))

