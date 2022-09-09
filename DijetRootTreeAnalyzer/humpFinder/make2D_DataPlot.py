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

#year = sys.argv[1]
year='2018'

sample="Data"

################################################
DATA = []
if(sample=="Data"):
  DATA.append("FemtoTrees/Data_trigger.root")
  TreeName="femtotree"

elif(sample=="GJets"):
  DATA.append("FemtoTrees/GJets_trigger.root")
  TreeName="femtotree"

print(DATA)

#Analysis Cuts
# masym, eta, dipho, iso
masym,deta,dipho,iso = 0.25, 1.5, 0.9, 0.8

def Make1BinsFromMinToMax(Min,Max):
    BINS = []
    for i in range(int(Max-Min)+1):
        BINS.append(Min+i)
    return numpy.array(BINS)
def Make2BinsFromMinToMax(Min,Max):
    BINS = []
    for i in range(int(Max-Min)+1,2):
        BINS.append(Min+i)
    return numpy.array(BINS)

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)


#AlphaBins = [ 0.0, 0.00428, 0.00467, 0.00506, 0.00568, 0.00637, 0.00706, 0.00775, 0.00844, 0.00935, 0.00974, 0.01012, 0.01120, 0.01189, 0.01285, 0.01392, 0.03 ]
#AlphaBins = [ 0.0, 0.00637, 0.00706, 0.00775, 0.00844, 0.00935, 0.00974, 0.01012, 0.01120, 0.01189, 0.01285, 0.01392, 0.03 ]
AlphaBins = [ 0.0, 0.3]
#XlB = Make1BinsFromMinToMax(0.,249.)
XlB = numpy.linspace(0,248,248/2+1)
XhB = [250.0, 255.0, 261.0, 267.0, 273.0, 279.0, 285.0, 291.0, 297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0,
526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0,
940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0,
1564.0, 1596.0, 1629.0, 1662.0, 1696.0]
XB = numpy.concatenate((XlB,XhB))
X1B = Make1BinsFromMinToMax(297., 1696.)
AB = [0.0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.011, 0.012, 0.013, 0.014, 0.015, 0.016, 0.017, 0.018, 0.019, 0.02, 0.021, 0.022, 0.023, 0.024, 0.025, 0.027, 0.029,0.031, 0.033, 0.035]

PTB = numpy.linspace(0,500,501)

N=sample

# Load files:
Chain = ROOT.TChain(TreeName)
for f in DATA:
    Chain.Add(f)
Rdf = RDF(Chain)
# Make cuts:
#Rdf = Rdf.Filter(trigger+" > 0.","trigger")
#Rdf = Rdf.Filter("clu1_pt > 90. && clu2_pt > 90.", "pt > 90")

Rdf = Rdf.Filter("masym < " + str(masym),"masym < {}".format(masym))
Rdf = Rdf.Filter("deta < " + str(deta),"deta < {}".format(deta))
Rdf = Rdf.Filter("clu1_dipho > " + str(dipho) + " && clu2_dipho > " + str(dipho),"dipho > {}".format(dipho))
Rdf = Rdf.Filter("clu1_iso > " + str(iso) + " && clu2_iso > " + str(iso),"iso > {}".format(iso))
Rdf =	Rdf.Define("fW", "1")
rep = Rdf.Report()
rep.Print()
# Book plots:
b_XM = Rdf.Histo1D(("XM", ";di-cluster mass (GeV); events / bin", len(XB)-1, numpy.array(XB)), "XM", "fW")
b_X1M = Rdf.Histo1D(("XM1", ";di-cluster mass (GeV); events / bin", len(X1B)-1, numpy.array(X1B)), "XM", "fW")
b_XMvA = Rdf.Histo2D(("XMvA", ";di-cluster mass (GeV);#alpha; events / bin", len(XB)-1, numpy.array(XB), len(AB)-1, numpy.array(AB)), "XM", "alpha", "fW")

pt_mass1_r = Rdf.Histo2D(("XMvPt1",";di-cluster mass (GeV);pT (GeV); events/bin",len(XB)-1, numpy.array(XB), len(PTB)-1, PTB), "XM","clu1_pt","fW")
pt_mass2_r = Rdf.Histo2D(("XMvPt2",";di-cluster mass (GeV);pT (GeV); events/bin",len(XB)-1, numpy.array(XB), len(PTB)-1, PTB), "XM","clu2_pt","fW")

# Fill plots:
c_XM = b_XM.GetValue()
c_X1M = b_X1M.GetValue()
c_XMvA = b_XMvA.GetValue()
# Clone plots:
XM = c_XM.Clone(N+"_"+c_XM.GetName())
X1M = c_X1M.Clone(N+"_"+c_X1M.GetName())
for h in [XM, X1M]:
    h.SetFillColor(2)
    h.SetLineColor(2)
    h.SetFillStyle(3001)
XMvA = c_XMvA.Clone(N+"_"+c_XMvA.GetName())

pt_mass1 = pt_mass1_r.GetValue().Clone()
pt_mass2 = pt_mass2_r.GetValue().Clone()

pt_mass1.Scale(1,"width")
pt_mass2.Scale(1,"width")

saveFile = TFile("NPlots/twoDPlots.root","RECREATE")
saveFile.cd()
XMvA.Write()
pt_mass1.Write()
pt_mass2.Write()

c1 = ROOT.TCanvas()
c1.cd()
pt_mass1.GetXaxis().SetRangeUser(0,1000)
pt_mass1.GetXaxis().SetTitleSize(0.05)
pt_mass1.GetYaxis().SetTitleSize(0.05)
pt_mass1.Draw("colz")
c1.Print("NPlots/TwoD/pt1.png")

c2 = ROOT.TCanvas()
c2.cd()
pt_mass2.GetXaxis().SetRangeUser(0,1000)
pt_mass2.GetXaxis().SetTitleSize(0.05)
pt_mass2.GetYaxis().SetTitleSize(0.05)
pt_mass2.Draw("colz")
c2.Print("NPlots/TwoD/pt2.png")
