import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time
from array import array

RDF = ROOT.RDataFrame.RDataFrame
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../../.")
import PlottingPayload as PL
#gROOT.SetBatch()

year='2018'

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"
const_alpha = False #Use this to get signals at one alpha val
this_alpha = 0.005 #Set this to the alpha you want. If const_alpha = False, this does nothing

def Make1BinsFromMinToMax(Min,Max):
    BINS = []
    for i in range(int(Max-Min)+1):
        BINS.append(Min+i)
    return numpy.array(BINS)

XB = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0, 2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0]

X1B = Make1BinsFromMinToMax(297., 3110.)
AB = [0.0, 0.001, 0.002, 0.003, 0.004, 0.005, 0.006, 0.007, 0.008, 0.009, 0.01, 0.011, 0.012, 0.013, 0.014, 0.015, 0.016, 0.017, 0.018, 0.019, 0.02, 0.021, 0.022, 0.023, 0.024, 0.025, 0.027, 0.029, 0.031, 0.033, 0.035]
AlphaBins = [
               0.003,
               0.00347, 
               0.00395,   
               0.00444, 
               0.00494, 
               0.00545, 
               0.00597, 
               0.0065, 
               0.00704, 
               0.00759, 
               0.00815, 
               0.00872, 
               0.0093, 
               #0.00989, 
               0.01049, 
               #0.0111, 
               #0.01173, 
               #0.01237, 
               #0.01302, 
               #0.01368, 
               #0.01436,
               0.01505, 
               #0.01575, 
               #0.01647, 
               #0.0172, 
               #0.01794, 
               #0.0187, 
               #0.01947, 
               #0.02026, 
               #0.02106, 
               #0.02188, 
               #0.02271, 
               #0.02356, 
               #0.02443, 
               #0.02531, 
               #0.02621, 
               #0.02713, 
               #0.02806, 
               #0.02901, 
               0.03]

AfineB = numpy.linspace(0.0,0.03, 10000)
#AfineB = AlphaBins
def lookup(N):
  ysum = 0
  for year in [2016, 2017, 2018]:
    LH = []
    f = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/Diphoton-Treemaker/HelperFiles/Signal_NEvents_{}.csv".format(year)
    r = open(f)
    for i in r.readlines():
      #print i
      LH.append(i.split(','))

    X = N.split('A')[0].split('X')[1]
    A = N.split('A')[1].replace('p', '.')
    for r in LH:
      if r[0] == X and r[1] == A:
        ysum += int(r[2].rstrip())
  return ysum


#Analysis Cuts
# masym, eta, dipho, iso
#CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [1.0, 3.5, 0.9, 0.8] #Loose
#CUTS = [0.25, 1.5, 0.9, 0.8] #Analysis Cuts
CUTS = [0.25, 1.5, 0.9, 0.1] #Loose Analysis Cuts

#################################################

#AlphaBins = [0.003, 0.00347, 0.00395, 0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.00872, 0.0093, 0.00989, 0.01049, 0.0111, 0.01173, 0.01237, 0.01302, 0.01368, 0.01436, 0.01505, 0.01575, 0.01647, 0.0172, 0.01794, 0.0187, 0.01947, 0.02026, 0.02106, 0.02188, 0.02271, 0.02356, 0.02443, 0.02531, 0.02621, 0.02713, 0.02806, 0.02901, 0.03]


print("Doing Generated Signals")

#Get signals for one x mass
genXs = [200,300,400,500,600,750,1000,1500,2000,3000]

SignalsGenerated = {}
for ff in os.listdir(xaastorage):
  if(ff[0]=="X"  ):
    thisxa = ff[ : ff.find("_")]
    this_x = int(thisxa[1:thisxa.find("A")])
    if(this_x < 300): continue
    this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
    if(this_phi / this_x > 0.031): continue
    if(thisxa in SignalsGenerated.keys()):
      SignalsGenerated[thisxa].append(os.path.join(xaastorage, ff))
    else:
      SignalsGenerated[thisxa] = [os.path.join(xaastorage, ff)]

fracs = array("d")
alphaeffs = array("d")

alphamin, alphamax = 0, 0.031
nalphas = int((alphamax - alphamin)//0.001 + 2)
alphalist = numpy.linspace(alphamin, alphamax, nalphas)

#xmin, xmax = 300, 3000
#nxs = int((xmax-xmin)//10 + 1)
#xlist = numpy.linspace(xmin, xmax, nxs)
#alphalist = numpy.array([0.005, 0.01, 0.015, 0.02, 0.025, 0.03])
xlist = numpy.array([300.,400.,500.,600.,750.,1000.,1500.,2000.,3000.])

pdiffhist = ROOT.TH2D("pdif","% Difference; DiCluster Mass (GeV); alpha", len(xlist)-1, xlist, len(alphalist)-1, alphalist)

fracs.append(0)
alphaeffs.append(0)

for abin_num in range(3,len(AlphaBins)-1):
  #if(abin_num > 3): continue
  d_path = os.path.dirname(os.path.realpath(__file__))

  lA = AlphaBins[abin_num]
  hA = AlphaBins[abin_num+1]


  for thisSigIndex, oneSig in SignalsGenerated.items():
    whichSig = oneSig[0][0 : oneSig[0].find("_")]
    whichSig = whichSig.split("/")[-1]
    thisX = int(whichSig[whichSig.find("X")+1 : whichSig.find("A")])
    thisPhi = float(whichSig[whichSig.find("A")+1 : ].replace("p","."))
    thisAlpha = thisPhi/thisX
    #if(whichSig != "X600A15"):continue
    saveTree = False

    if(not os.path.exists("../inputs/Shapes_fromGen/alphaBinning/{}/{}/PLOTS_{}.root".format(abin_num,whichSig,abin_num))):
      continue
    print("---------------------------------------------------------------------------")
    print("\nSignal: {}".format(whichSig))

    ufile = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/unBinned/"
    uf = ROOT.TFile(ufile + whichSig + "/Sig_nominal.root", "read")
    aHist = uf.Get("h_alpha_fine")
    print("aHistBins before rebin: {}".format(aHist.GetNbinsX()))
    aHist = aHist.Rebin(len(AlphaBins)-1,aHist.GetName()+"_rebin",numpy.array(AlphaBins))
    print("aHistBins after rebin: {}".format(aHist.GetNbinsX()))

    (sXr_ub, sX1r_ub, sA_ub, sXvAr_ub) = GetDiphoShapeAnalysisPlusAlpha(SignalsGenerated[thisSigIndex],thisAlpha, "pico_nom", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [0.,0.03], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
    (sXr, sX1r, sA, sXvAr) = GetDiphoShapeAnalysisPlusAlpha(SignalsGenerated[thisSigIndex], thisAlpha,"pico_nom", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
    
    alpha_denom = sX1r_ub.GetEntries()
    alpha_num = sX1r.GetEntries()
    alpha_eff = alpha_num / alpha_denom

    lBin,hBin = aHist.FindBin(lA), aHist.FindBin(hA)
    zbin,tbin = aHist.FindBin(0.0), aHist.FindBin(0.03)
    frac = aHist.Integral(lBin,hBin-1) / aHist.Integral(zbin, tbin)
    
    if(alpha_eff > 0.1 or (abin_num < 4 and thisAlpha==0.005)):
    #if(alpha_eff >= 0.33 or (abin_num < 4 and thisAlpha==0.005)):
      print("Alpha bin: ")
      print("{}: {} - {}".format(abin_num, lA, hA))

      print("Alpha: {} / {} = {}".format(alpha_num, alpha_denom, alpha_eff))

      n_postcut = float(sX1r.GetEntries())
      n_gen = float(lookup(whichSig))
      eff = n_postcut / n_gen * 100

      pdiff = abs(frac - alpha_eff) / frac * 100
      print("frac: {:.4f}, alpha: {:.4f}, {:.4f}% diff".format(frac, alpha_eff, pdiff))
      fracs.append(frac)
      alphaeffs.append(alpha_eff)
      pdiffhist.Fill(thisX, thisAlpha, pdiff)
      #if(len(fracs) > 1): break

    else:
      print("Not enough signal in Alpha Window. Skipping")
      continue

mx = max([max(fracs),max(alphaeffs)])
lin = ROOT.TLine(0,0,mx,mx)

c1 = ROOT.TCanvas()
c1.cd()
gr = TGraph(len(fracs), fracs, alphaeffs)
gr.SetLineColor( 2 )
gr.SetLineWidth( 4 )
gr.SetMarkerColor( 4 )
gr.SetMarkerStyle( 21 )
gr.SetTitle( "Efficiency in alpha bins")
gr.GetXaxis().SetTitle( "Computed from Integral" )
gr.GetYaxis().SetTitle( 'Computed from events' )
gr.GetXaxis().SetRangeUser(0, mx*1.1)
gr.GetYaxis().SetRangeUser(0, mx*1.1)
gr.Draw( 'AP' )
lin.Draw("same")
c1.Print("EffPlots/compare_known.png")

c2 = ROOT.TCanvas()
c2.cd()
pdiffhist.SetStats(0)
pdiffhist.Draw("colz")
c2.Print("EffPlots/compare_pdiff.png")

