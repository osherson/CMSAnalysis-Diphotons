import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time
import os
RDF = ROOT.RDataFrame.RDataFrame

dir_path = os.path.dirname(os.path.realpath(__file__))
#gROOT.SetBatch()

sample=sys.argv[1]

################################################

plotFile=TFile("NPlots/{}_Plots.root".format(sample))

pt=90
masym=0.25
deta=1.5
dipho=0.9
iso=0.8


hnames = []
hnames = [hn.GetName() for hn in plotFile.GetListOfKeys()]

for hn in hnames:
  hist = plotFile.Get(hn)

  hist.GetXaxis().SetTitleSize(0.175/4)
  #hist.GetXaxis().SetLabelSize(0.145)
  hist.GetXaxis().SetLabelSize(0.145/4)
  hist.GetXaxis().SetTitleOffset(0.75)
  hist.GetYaxis().SetTitleSize(0.175/4)
  hist.GetYaxis().SetLabelSize(0.145/4)
  #hist.GetYaxis().SetTitleOffset(0.75)
  hist.GetYaxis().SetTitleOffset(1)
  hist.SetMarkerStyle(8)
  
  if(sample=="Data"):
    hist.SetLineColor(1)
  if(sample=="GJets"):
    hist.SetLineColor(8)
  #hist.SetStats(0)
  hist.SetLineWidth(2)
  #hist.SetDirectory(gROOT)

  c1 = TCanvas()
  c1.cd()
  hist.Draw("hist")
  c1.Print("NPlots/Pretty/{}/{}_{}.png".format(sample,sample,hn))


