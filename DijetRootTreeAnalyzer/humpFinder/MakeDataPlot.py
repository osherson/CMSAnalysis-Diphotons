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
  DATA.append("FemtoTrees/Data_trigger_pt90.root")

elif(sample=="GJets"):
  DATA.append("FemtoTrees/GJets_trigger_pt90.root")

print(DATA)

#Analysis Cuts
# masym, eta, dipho, iso
#CUTS =  [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [1.0, 3.5, 0.9, 0.8] #Loose
#CUTS = [1.0, 3.5, 0.0, 0.0] #Loose
#CUTS = [0.25, 3.5, 0.9, 0.8] #Analysis Cuts

CutList = [
          #[0.25, 1.5, 0.9, 0.8],
          #[0.25, 1.5, 0.9, 0.1],
          [0.25, 2.5, 0.9, 0.1],
          #[0.25, 3.5, 0.9, 0.5],
          #[0.25, 2, 0.0, 0.0],
          #[0.25, 2, 0.25, 0.0],
          #[0.25, 2, 0.5, 0.0],
          #[0.25, 2, 0.9, 0.0],
          #[0.25, 2, 0.9, 0.25],
          #[0.25, 2, 0.9, 0.5],
          #[0.25, 2, 0.9, 0.8],
          ]

etalow, etahigh = 1.,1.4
EtaList = [
          (0.,1.5),
          (0.,1.),
          (1.,1.5),
          #(0.0,0.1),
          #(0.1,0.2),
          #(0.2,0.3),
          #(0.3,0.4),
          #(0.4,0.5),
          #(0.5,0.6),
          #(0.6,0.7),
          #(0.7,0.8),
          #(0.8,0.9),
          #(0.9,1.0),
          #(1.0,1.1),
          #(1.1,1.2),
          #(1.2,1.3),
          #(1.3,1.4),
          ]

#################################################

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

def GetDiphoShapeAnalysis(F, T, N, masym, deta, dipho, iso, alpha, trigger, scale, saveTree=False, saveSignal=""):
    global etalow,etahigh
    # Load files:
    Chain = ROOT.TChain(T)
    for f in F:
        Chain.Add(f)
    Rdf         =   RDF(Chain)
    # Make cuts:
    #Rdf = Rdf.Filter(trigger+" > 0.","trigger")
    #Rdf = Rdf.Filter("clu1_pt > 90. && clu2_pt > 90.", "pt > 90")
    Rdf = Rdf.Filter("abs(clu1_eta) > {} && abs(clu1_eta) <= {} && abs(clu2_eta) > {} && abs(clu2_eta) <= {}".format(etalow,etahigh,etalow,etahigh), "{} < eta < {}".format(etalow,etahigh))
    Rdf = Rdf.Filter("alpha > "+ str(alpha[0]) + " && alpha < " + str(alpha[1]),"Alpha bin")
    Rdf = Rdf.Filter("masym < " + str(masym),"masym < {}".format(masym))
    Rdf = Rdf.Filter("deta < " + str(deta),"deta < {}".format(deta))
    Rdf = Rdf.Filter("clu1_dipho > " + str(dipho) + " && clu2_dipho > " + str(dipho),"dipho > {}".format(dipho))
    #Rdf = Rdf.Filter("clu1_hadron > " + str(dipho) + " && clu2_hadron > " + str(dipho),"hadron > {}".format(dipho))
    Rdf = Rdf.Filter("clu1_iso > " + str(iso) + " && clu2_iso > " + str(iso),"iso > {}".format(iso))
    Rdf =	Rdf.Define("fW", scale)
    rep = Rdf.Report()
    rep.Print()
    # Book plots:
    b_XM = Rdf.Histo1D(("XM", ";di-cluster mass (GeV); events / bin", len(XB)-1, numpy.array(XB)), "XM", "fW")
    b_X1M = Rdf.Histo1D(("XM1", ";di-cluster mass (GeV); events / bin", len(X1B)-1, numpy.array(X1B)), "XM", "fW")
    b_XMvA = Rdf.Histo2D(("XMvA", ";di-cluster mass (GeV);#alpha; events / bin", len(XB)-1, numpy.array(XB), len(AB)-1, numpy.array(AB)), "XM", "alpha", "fW")
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

    if saveTree:
      keeplist = ["run","lumiSec","id","clu1_phi","clu2_phi","clu1_moe","clu2_moe","XM"]
      branchList = ROOT.std.vector('std::string')()
      for k in keeplist: branchList.push_back(k)
      savename = "{}/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/{}/DATATREE.root".format(dir_path,saveSignal)
      print("Saving Data Tree As: {}".format(savename))
      Rdf.Snapshot("datatree", savename, branchList)

    # Return plots:
    return (XM, X1M, XMvA, int(Rdf.Count().GetValue()))


#for abin_num in range(0,len(AlphaBins)-1):
for (etalow,etahigh) in EtaList:
  for abin_num in [0,1,15]:
    if(abin_num != 0): continue

    for CUTS in CutList:

      lA = AlphaBins[abin_num]
      hA = AlphaBins[abin_num+1]
      print("alpha bin: ")
      print("{}: {} - {}".format(abin_num, lA, hA))
      saveTree = False

      treename="femtotree"
      (dX, dX1, dXvA,count) = GetDiphoShapeAnalysis(DATA, treename, "data", CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "1.", saveTree, year+"/"+str(abin_num))

      txt1 = "{} < #alpha < {}, pt > 90".format(lA,hA)
      txt2 = "masym < {}, deta < {}".format(CUTS[0], CUTS[1])
      txt3 = "dipho > {}, iso > {}".format(CUTS[2], CUTS[3])
      #txt3 = "hadron > {}, iso > {}".format(CUTS[2], CUTS[3])
      txt4 = "{} < |#eta| < {}".format(etalow, etahigh)

      c1 = TCanvas()
      c1.cd()

      latex = TLatex()
      latex.SetNDC()

      latex.SetTextAngle(0)
      latex.SetTextColor(ROOT.kRed)
      latex.SetTextFont(42)
      latex.SetTextAlign(12)
      latex.SetTextSize(0.035)

      #t = TLatex (.1,.1,"TLatex at (.1,.1)");  
      #t.SetNDC(kTRUE);
      #t.Draw();

      dX.Scale(1, "width") #Divide by bin width
      dX.SetMarkerStyle(20)
      dX.SetMarkerSize(0.9)
      dX.SetLineColor(kBlack)
      #dX.GetXaxis().SetRangeUser(297,1000)
      #dX.GetXaxis().SetRangeUser(0,1500)
      dX.GetXaxis().SetRangeUser(280,1500)
      dX.GetXaxis().SetTitle("DiCluster Mass (GeV)")
      dX.GetXaxis().SetTitleSize(0.05)
      dX.SetStats(0)

      dX.Draw("e")
      c1.SetLogy()
      #c1.SetLogx()
      if(sample=="GJets"):
        pname = "Plots/GJets/eta{}_{}/alpha{}_masym{}_deta{}_dipho{}_iso{}".format(etalow,etahigh,abin_num, CUTS[0], CUTS[1], CUTS[2], CUTS[3])
        #pname = "Plots/GJets/eta{}_{}/alpha{}_masym{}_deta{}_hadron{}_iso{}".format(etalow,etahigh,abin_num, CUTS[0], CUTS[1], CUTS[2], CUTS[3])
      else:
        pname = "Plots/eta{}_{}/alpha{}_masym{}_deta{}_dipho{}_iso{}".format(etalow, etahigh, abin_num,CUTS[0], CUTS[1], CUTS[2], CUTS[3])
        #pname = "Plots/eta{}_{}/alpha{}_masym{}_deta{}_hadron{}_iso{}".format(etalow, etahigh, abin_num,CUTS[0], CUTS[1], CUTS[2], CUTS[3])
      MakeFolder(pname[ : pname.find("alpha")-1])
      print("Saving as {}".format(pname))
      latex.DrawLatex(0.65,0.85+0.02,txt1)
      latex.DrawLatex(0.65,0.80+0.02,txt2)
      latex.DrawLatex(0.65,0.75+0.02,txt3)
      latex.DrawLatex(0.65,0.70+0.02,txt4)
      latex.DrawLatex(0.65,0.65+0.02,"{} Clusters".format(count))
      c1.Print("{}.png".format(pname))
      #c1.Print("{}.root".format(pname))
