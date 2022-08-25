import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time

RDF = ROOT.RDataFrame.RDataFrame
xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"

################################################
#Get DATA
DATA = []
for ff in os.listdir(xaastorage):
  #if("Run" in ff and year in ff): #one year data
  if("Run" in ff and "20" in ff): #All Run II Data
    DATA.append(os.path.join(xaastorage,ff))

if("quick" in sys.argv):
  DATA = [DATA[-1]]
print(DATA)
time.sleep(1)

#Analysis Cuts
# masym, eta, dipho, iso
CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [0.25, 3.5, 0.9, 0.8] #Analysis Cuts

#################################################

AB = [
             0.0,
             0.00428571428571,
             0.00467532467532,
             0.00506493506494,
             0.005689655172413793,
             0.006379310344827587,
             0.00706896551724138,
             0.007758620689655172,
             0.008448275862068966,
             0.00935064935065,
             0.00974025974026,
             0.0101298701299,
             0.01120689655172414,
             0.011896551724137932,
             0.0128571428571,
             0.0139285714286,
             0.03
             ]
XB = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0,     1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0]

chain = ROOT.TChain("pico_skim")
for dd in DATA:
  chain.Add(dd)

Rdf = RDF(chain)

Rdf = Rdf.Filter("clu1_pt > 90. && clu2_pt > 90.  && masym < " + str(CUTS[0]) + " && deta <     " + str(CUTS[1]) + " && clu1_dipho > " + str(CUTS[2]) + " && clu2_dipho > " + str(CUTS[2]) + " && clu1_iso > " + str(CUTS[3]) + " && clu2_iso > " + str(CUTS[3]))

hist = Rdf.Histo2D(("XMvA", ";DiCluster mass (GeV);#alpha; events / bin", len(XB)-1, numpy.array(XB), len(AB)-1, numpy.array(AB)), "XM", "alpha")
mhist = Rdf.Histo2D(("phiVX", ";DiCluster mass (GeV); #phi Mass ", len(XB)-1, numpy.array(XB), 100, 0, 20),"XM","aM")

hh = hist.GetValue().Clone()
hh.GetXaxis().SetTitleSize(0.05)
hh.GetYaxis().SetTitleSize(0.05)

hm = mhist.GetValue().Clone()
hm.GetXaxis().SetTitleSize(0.05)
hm.GetYaxis().SetTitleSize(0.05)

c1 = ROOT.TCanvas()
c1.cd()
hh.Draw("COLZ")

outfile = TFile("plots.root","RECREATE")
outfile.cd()
hh.Write()
hm.Write()
