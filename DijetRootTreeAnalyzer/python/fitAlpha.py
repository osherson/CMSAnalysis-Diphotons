import ROOT
from ROOT import *

afile = TFile("alphaplot.root","READ")

ahist = afile.Get("alph")

ahist.Fit("pol2")

#c1 = TCanvas()
#c1.cd()
#ahist.Draw("e")
