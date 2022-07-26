import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time

RDF = ROOT.RDataFrame.RDataFrame

bcounts = [80,70,60,50,40]
alphas = [0.005, 0.01, 0.015, 0.02, 0.025]
AlphaBins = [0]

for (aa, bc) in zip(alphas,bcounts):
  bins = numpy.linspace(0,0.03,bc)
  for ii in range(0, len(bins)):
      if bins[ii] < aa: continue
      else:
        AlphaBins.append(bins[ii-2])
        AlphaBins.append(bins[ii-1])
        AlphaBins.append(bins[ii])
        AlphaBins.append(bins[ii+1])
        break
AlphaBins.append(0.03)


#AlphaBins = [
#  0.00455696, 0.00493671,0.00531646,0.0056962,0.00607595,0.0064557,
#  0.00913043, 0.00956522, 0.01, 0.01043478, 0.01086957, 0.01130435, 
#  0.01423729, 0.01474576, 0.01525424, 0.01576271, 0.01627119, 
#  0.01897959, 0.01959184, 0.02020408, 0.02081633, 0.02142857,
#  0.02384615, 0.02461538, 0.02538462, 0.02615385, 0.02692308,0.03
#  ]

AlphaBins = [0., 0.0015, 0.003, 0.0045, 0.006, 0.0075, 0.01, 0.0125, 0.015, 0.0175, 0.020, 0.025, 0.03]
AlphaBins = [0., 0.003, 0.0035, 0.004, 0.0045, 0.005, 0.0055, 0.006, 0.007, 0.008, 0.009, 0.01, 0.0115, 0.013, 0.0145, 0.016, 0.0175, 0.020, 0.0225, 0.025, 0.0275, 0.03]

AlphaBins = [0., 0.00422263, 0.00469758, 0.00517253, 0.00605263,
             0.00710526, 0.00815789, 0.0093758 , 0.00978903, 0.01020225,
             0.01131579, 0.01236842, 0.01334154, 0.01417077, 0.015,
             0.01552632, 0.01657895, 0.01763158, 0.01901665, 0.01963444,
             0.02025223, 0.02078947, 0.02184211, 0.0231082 , 0.02414009,
             0.02517198, 0.03]

print("BINNING: ")
print(AlphaBins)

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../../.")
import PlottingPayload as PL
#gROOT.SetBatch()

year = 2018
igen = "g"

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"
const_alpha = False #Use this to get signals at one alpha val

################################################

#Analysis Cuts
# masym, eta, dipho, iso
CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [0.25, 3.5, 0.9, 0.8] #Analysis Cuts

aa = TH2D("twod","N Sig Events vs. #alpha", 31,0,0.03, len(AlphaBins)-1, numpy.array(AlphaBins))
alpha = TH1D("alph","#alpha_{RMS} per alpha",31,0,0.03)
nSigBins = TH1D("nSigBins", "Number of \'Significant Bins\'; #alpha; N Significant Bins", 31, 0, 0.03)

sigDic = {0.005:0, 0.01:0, 0.015:0, 0.02:0, 0.025:0}

#################################################
#Generated Signals 
if(igen == "g"):

  SignalsGenerated = {}
  #SignalsGenerated["X300A1p5"] = ["/cms/xaastorage-2/DiPhotonsTrees/X300A1p5_{}.root".format(year)]

  #Get all signals
  for ff in os.listdir(xaastorage):
    if(ff[0]=="X" and str(year) in ff and "X200A" not in ff):
      thisxa = ff[ : ff.find("_")]
      this_x = int(thisxa[1:thisxa.find("A")])
      this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
      if(const_alpha and this_phi / this_x != this_alpha): continue
      SignalsGenerated[thisxa] = [os.path.join(xaastorage, ff)]

  fcount = 0
  tcount = 0

  ct = 0
  for s in SignalsGenerated:
    ct += 1
    saveTree = False
    thisx = int(s[1 : s.find("A")])
    thisphi = float(s[s.find("A")+1 :].replace("p","."))

    if(thisphi / thisx > 0.029): continue
    #if(int(thisphi) != 3): continue
    #if(thisx !=  600 ): continue

    if(thisphi / thisx == 0.005): fcount += 1
    if(thisphi / thisx == 0.01): tcount += 1

    print(thisx, thisphi)

    masym, deta, dipho, iso = CUTS[0], CUTS[1], CUTS[2], CUTS[3]
    trigger = "HLT_DoublePhoton"

    Chain = ROOT.TChain("pico_nom")
    for f in SignalsGenerated[s]:
        Chain.Add(f)
    Rdf = RDF(Chain)
    Rdf = Rdf.Filter(trigger+" > 0.")
    Rdf = Rdf.Filter("clu1_pt > 90. && clu2_pt > 90. && masym < " + str(masym) + " && deta <     " + str(deta) + " && clu1_dipho > " + str(dipho) + " && clu2_dipho > " + str(dipho) + " && clu1_iso > " + str(iso) + " && clu2_iso > " + str(iso))

    aHist = Rdf.Histo1D(("alpha","alpha", len(AlphaBins)-1, numpy.array(AlphaBins)), "alpha")
    useHist = aHist.GetValue().Clone()
    NTot = useHist.GetEntries()

    for ii in range(0,len(AlphaBins)-1):
      #if(ii % (len(alphabins) // 4) == 0): print("{}/{}".format(ii,len(alphabins)))
      lA=AlphaBins[ii]
      hA=AlphaBins[ii+1]

      myBin = aHist.FindBin(lA)
      myCount = aHist.GetBinContent(myBin)

      aa.Fill(thisphi/thisx, (lA+hA)/2, myCount)
    
      sigBins = 0
      if(float(myCount) / float(NTot) > 0.15):
        sigBins += 1
      #print("N SIG: ", sigBins)
      sigDic[thisphi/thisx] += sigBins
      #nSigBins.Fill(thisphi/thisx, sigBins)

print(fcount, tcount)
for av,sv in sigDic.items():
  nSigBins.Fill(av,float(sv)/float(fcount))


outfile = TFile("alphaplotbinned.root","RECREATE")
outfile.cd()
#alpha.GetXaxis().SetTitle("#alpha")
#alpha.GetYaxis().SetTitle("#alpha_{RMS}")
#alpha.Write()
aa.GetXaxis().SetTitle("#alpha")
aa.GetYaxis().SetTitle("Alpha Slice Window")
aa.Write()

profy = aa.ProfileY()
profy.Write()

profx = aa.ProfileX()
profx.Write()

nSigBins.Write()

outfile.Close()

c1 = TCanvas("c","c",800,600)
c1.cd()
nSigBins.SetStats(0)
nSigBins.Draw("COLZ")
c1.Print("alphaplotbinned.png")
 
