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

def Make1BinsFromMinToMax(Min,Max):
    BINS = []
    for i in range(int(Max-Min)+1):
        BINS.append(Min+i)
    return numpy.array(BINS)

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

#AlphaBins = [ 0.0, 0.00428, 0.00467, 0.00506, 0.00568, 0.00637, 0.00706, 0.00775, 0.00844, 0.00935, 0.00974, 0.01012, 0.01120, 0.01189, 0.01285, 0.01392, 0.03 ]
#AlphaBins = [ 0.0, 0.00637, 0.00706, 0.00775, 0.00844, 0.00935, 0.00974, 0.01012, 0.01120, 0.01189, 0.01285, 0.01392, 0.03 ]
AlphaBins = [ 0.0, 0.3]
XlB = Make1BinsFromMinToMax(0.,296.)
XhB = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0,
526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0,
940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0,
1564.0, 1596.0, 1629.0, 1662.0, 1696.0]
XB = numpy.concatenate((XlB,XhB))
X1B = Make1BinsFromMinToMax(297., 1696.)
AB = [0.0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.011, 0.012, 0.013, 0.014, 0.015, 0.016, 0.017, 0.018, 0.019, 0.02, 0.021, 0.022, 0.023, 0.024, 0.025, 0.027, 0.029,0.031, 0.033, 0.035]

year='2018'

sample=sys.argv[1]

################################################

DATA = "FemtoTrees/{}_trigger.root".format(sample)

TName="femtotree"
print("Getting File: {}".format(DATA))

Chain = ROOT.TChain(TName)
Chain.Add(DATA)
Rdf = RDF(Chain)

#CUTS = {"pt":90,
#        "masym":0.25,
#        "deta":1.5,
#        "dipho":0.9,
#        "iso":0.8,
#        }

pt=90
masym=0.25
deta=1.5
dipho=0.9
iso=0.8

CUTS = {
        "pt":"clu1_pt > {} && clu2_pt > {}".format(pt,pt),
        "masym":"masym < {} ".format(masym,masym),
        "deta":"deta < {} ".format(deta,deta),
        "dipho":"clu1_dipho > {} && clu2_dipho > {}".format(dipho,dipho),
        "iso":"clu1_iso > {} && clu2_iso > {}".format(iso,iso),
      }

BINS = {
      "pt":    numpy.linspace(0,1000,1000),
      "masym": numpy.linspace(0,1.,100),
      "deta":  numpy.linspace(0,3.5,100),
      "dipho": numpy.linspace(0,1.,100),
      "iso":   numpy.linspace(0,1.,100),
      }

titles = {
      "pt":    "pT",
      "masym": "Mass Asymmetry",
      "deta":  "#Delta #eta",
      "dipho": "Diphoton Score",
      "iso":   "Isolation",
      }

histlist = []
for var,cut in CUTS.items():
  print(var, cut)

  ii=0
  for iv,ic in CUTS.items():
    if(var==iv): continue

    if(ii==0): cutString = ic
    else:
      cutString += " && "
      cutString +=  ic

    ii+=1

  print(cutString)
  thisRdf = Rdf.Filter(cutString)
  rep = thisRdf.Report()
  rep.Print()

  bb = BINS[var]
  if(var in ["pt","dipho","iso"]):
    var1 = "clu1_{}".format(var)
    var2 = "clu2_{}".format(var)
    hist1 = thisRdf.Histo1D((var1,"{} with All Other Cuts;{};entries".format(var1,titles[var]),len(bb)-1,bb),var1)
    hist2 = thisRdf.Histo1D((var2,"{} with All Other Cuts;{};entries".format(var2,titles[var]),len(bb)-1,bb),var2)
    histlist.append(hist1.GetValue().Clone())
    histlist.append(hist2.GetValue().Clone())
  else:
    hist = thisRdf.Histo1D((var,"{} with All Other Cuts;{};entries".format(var,titles[var]),len(bb)-1,bb),var)
    histlist.append(hist.GetValue().Clone())

outfile = TFile("NPlots/{}_Plots.root".format(sample),"RECREATE")
outfile.cd()
for hh in histlist:
  hh.Write()
outfile.Close()


