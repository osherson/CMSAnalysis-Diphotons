import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../../.")
import PlottingPayload as PL
gROOT.SetBatch()

year='2018'

#xmass = 1000
if( len(sys.argv) >= 1):
  if("X" in sys.argv[1]):
    xmass = sys.argv[1]
    xmass = int(xmass[1:])

#print(xmass)

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"
const_alpha = False #Use this to get signals at one alpha val
this_alpha = 0.005 #Set this to the alpha you want. If const_alpha = False, this does nothing

def doOneInput(N, sig, h, H, S, norm = False):
    dir_path = os.path.dirname(os.path.realpath(__file__))

    toF = TFile("{}/../inputs/Shapes_fromGen/alphaBinning/{}/{}/{}.root".format(dir_path,N,sig,S), "recreate")
    if norm:
        try:
          h.Scale(1./h.Integral())
        except ZeroDivisionError:
          print("Not normalizing")

    toF.cd()
    h.SetName(H)
    h.Write()
    toF.Write()
    toF.Save()
    toF.Close()

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

def SaveHists(N, sig, sXr, sX1r, sXvAr, sX, sX1, dX, dX1, dXvA, sX1pu, sX1pd, sX1su, sX1sd):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    header = "{}/../inputs/Shapes_fromGen/alphaBinning/{}/{}/".format(dir_path,N,sig)
    PL.MakeFolder(header)
    with open(sig+".txt", 'w') as eff:
        E = sX1.GetEntries()
        G = lookup(sig)
        print "eff ("+sig+")---> " + str(float(E)/float(G))
        eff.write(str(float(E)/float(G)))
    os.system('mv ' + sig + '.txt {}/.'.format(header))
    doOneInput(N, sig, sX1, "h_AveDijetMass_1GeV", "Sig_nominal", True)
    doOneInput(N, sig, sX1pu, "h_AveDijetMass_1GeV", "Sig_PU", True)
    doOneInput(N, sig, sX1pd, "h_AveDijetMass_1GeV", "Sig_PD", True)
    doOneInput(N, sig, sX1su, "h_AveDijetMass_1GeV", "Sig_SU", True)
    doOneInput(N, sig, sX1sd, "h_AveDijetMass_1GeV", "Sig_SD", True)
    doOneInput(N, sig, dX1, "data_XM1", "DATA")
    AE = str(sX.Integral()/sXr.Integral())
    for h in [sXr, sX1r]:
        h.SetFillColor(0)
        h.SetLineColor(1)
    oF = TFile(header+"/PLOTS_"+N+".root", "recreate")
    sX.Write()
    sX1.Write()
    dX.Write()
    dX1.Write()
    PL.FindAndSetLogMax(sXr, dX)
    PL.FindAndSetLogMax(sX1r, dX1)
    for d in [dX, dX1]:
        d.SetTitle("#alpha window signal efficiency = " + AE)
        d.SetMarkerStyle(20)
        d.SetMarkerColor(1)
        d.SetLineColor(1)
        d.SetLineWidth(1)
        d.SetMarkerSize(0.4)
    L = TLegend(0.11,0.8,0.89,0.89)
    L.SetFillColor(0)
    L.SetLineColor(0)
    L.SetNColumns(2)
    L.AddEntry(dX, "data ("+str(dX.Integral())+" events)", "PL")
    L.AddEntry(sX, sig + " (10 fb)", "FL")
    C = TCanvas()
    C.cd()
    C.SetLogy(1)
    dX.Draw("e")
    sXr.Draw("samehist")
    sX.Draw("samehist")
    L.Draw("same")
    C.Print(header+"/sX.png")
    dX1.Draw("e")
    sX1r.Draw("samehist")
    sX1.Draw("samehist")
    L.Draw("same")
    C.Print(header+"/sX1M.png")
########### 
    lA = sXvAr.GetMean(2) - 3.*sXvAr.GetRMS(2)
    hA = sXvAr.GetMean(2) + 3.*sXvAr.GetRMS(2)

    xmin = 250
    xmax = sX1.GetBinLowEdge(sX1.GetNbinsX()-1)

    lLine = TLine(xmin, lA, xmax, lA)
    lLine.SetLineColor(ROOT.kRed)
    lLine.SetLineStyle(ROOT.kDashed)
    lLine.SetLineWidth(2)
    hLine = TLine(xmin, hA, xmax, hA)
    hLine.SetLineColor(ROOT.kRed)
    hLine.SetLineStyle(ROOT.kDashed)
    hLine.SetLineWidth(2)

    C.SetLogy(0)
    sXvAr.Draw("col")
    lLine.Draw("same")
    hLine.Draw("same")
    C.Print(header+"/sXvA.png")
############
    dXvA.Draw("col")
    lLine.Draw("same")
    hLine.Draw("same")
    C.Print(header+"/dXvA.png")
    oF.Write()
    oF.Save()
    oF.Close()

#############################
#Get DATA
DATA = []
for ff in os.listdir(xaastorage):
  #if("Run" in ff and year in ff): #one year data
  if("Run" in ff and "20" in ff): #All Run II Data
    DATA.append(os.path.join(xaastorage,ff))

#DATA = [DATA[-1]]
#print(DATA)
#time.sleep(1)

#Analysis Cuts
# masym, eta, dipho, iso
#CUTS = [1.0, 3.5, 0.9, 0.5] #Loose
#CUTS = [1.0, 3.5, 0.9, 0.8] #Loose
#CUTS = [0.25, 1.5, 0.9, 0.8] #Analysis Cuts
CUTS = [0.25, 1.5, 0.9, 0.1] #Loose Analysis Cuts

#################################################

#AlphaBins = [0.003, 0.00347, 0.00395, 0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.00872, 0.0093, 0.00989, 0.01049, 0.0111, 0.01173, 0.01237, 0.01302, 0.01368, 0.01436, 0.01505, 0.01575, 0.01647, 0.0172, 0.01794, 0.0187, 0.01947, 0.02026, 0.02106, 0.02188, 0.02271, 0.02356, 0.02443, 0.02531, 0.02621, 0.02713, 0.02806, 0.02901, 0.03]

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

print("Doing Generated Signals")

#Get signals for one x mass
genXs = [200,300,400,500,600,750,1000,1500,2000,3000]

if(xmass not in genXs):
  print("Not a generated X Mass. Quitting")
  exit()

print("Using X = {} GeV Signals".format(xmass))

SignalsGenerated = {}
for ff in os.listdir(xaastorage):
  if(ff[0]=="X" and "X{}A".format(xmass) in ff ):
    thisxa = ff[ : ff.find("_")]
    this_x = int(thisxa[1:thisxa.find("A")])
    this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
    if(this_phi / this_x > 0.031): continue
    if(this_phi/this_x in SignalsGenerated.keys()):
      SignalsGenerated[this_phi/this_x].append(os.path.join(xaastorage, ff))
    else:
      SignalsGenerated[this_phi/this_x] = [os.path.join(xaastorage, ff)]

for aa,fi in SignalsGenerated.items():
  print(aa, fi)

g_alphas = SignalsGenerated.keys()

for abin_num in range(0,len(AlphaBins)-1):
  #if(abin_num > 3): continue
  d_path = os.path.dirname(os.path.realpath(__file__))

  lA = AlphaBins[abin_num]
  hA = AlphaBins[abin_num+1]
  print("---------------------------------------------------------------------------")
  print("Alpha bin: ")
  print("{}: {} - {}".format(abin_num, lA, hA))
  saveTree = False
  newd = "{}/../inputs/Shapes_fromGen/alphaBinning/{}/".format(d_path,abin_num)
  PL.MakeFolder(newd)

  dataFile = ROOT.TFile("{}/../inputs/Shapes_DATA/alphaBinning/{}/DATA.root".format(d_path,abin_num))
  dX = dataFile.Get("data_XM")
  dX1 = dataFile.Get("data_XM1")
  dXvA = dataFile.Get("data_XvA")

  print("Data Entries: {}".format(dX1.GetEntries()))

  for thisSigIndex, oneSig in SignalsGenerated.items():
    whichSig = oneSig[0][0 : oneSig[0].find("_")]
    whichSig = whichSig.split("/")[-1]
    thisX = int(whichSig[whichSig.find("X")+1 : whichSig.find("A")])
    thisPhi = float(whichSig[whichSig.find("A")+1 : ].replace("p","."))
    thisAlpha = thisPhi/thisX
    #if(whichSig != "X200A1"):continue

    print("\nSignal: {}".format(whichSig))

    (sXr_ub, sX1r_ub, sXvAr_ub) = PL.GetDiphoShapeAnalysis(SignalsGenerated[thisSigIndex], "pico_nom", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [0,0.03], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
    (sXr, sX1r, sXvAr) = PL.GetDiphoShapeAnalysis(SignalsGenerated[thisSigIndex], "pico_nom", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
    print("Signal sX1r Entries, Integral: {}, {}".format(sX1r.GetEntries(), sX1r.Integral()))

    alpha_denom = sX1r_ub.GetEntries()
    alpha_num = sX1r.GetEntries()
    alpha_eff = alpha_num / alpha_denom

    #if(alpha_eff < 0.1): 
    #  print("Not enough signal in Alpha Window. Skipping")
    #  continue
    #else:
    #  print("Efficiency in this alpha window: {:.2f}%".format(alpha_eff * 100))
    
    if(alpha_eff > 0.1 or (abin_num < 4 and thisAlpha==0.005)):
      print("Efficiency in this alpha window: {:.2f}%".format(alpha_eff * 100))

      if(sX1r.GetEntries()<1 or sXr.GetEntries() < 1): 
        print("skipping, too few events")
        continue
      if(sX1r.Integral()<0.00001 or sXr.Integral() < 0.00001): 
        print("Skipping, Integral = 0")
        continue

      print("\nSignal: {}".format(whichSig))
      PL.MakeFolder("{}{}/".format(newd,whichSig))
      rfile = open("{}{}/arange.txt".format(newd,whichSig),"w")
      rfile.write("{},{}".format(lA,hA))
      rfile.close()

      aeffFile= open("{}{}/alphaFraction_alpha{}_{}.txt".format(newd,whichSig,abin_num,whichSig),"w")
      aeffFile.write(str(alpha_eff))
      aeffFile.close()

      (sXpu, sX1pu, sXvApu) = PL.GetDiphoShapeAnalysis(SignalsGenerated[thisSigIndex], "pico_nom", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeightUp*weight*10.*5.99")
      (sXpd, sX1pd, sXvApd) = PL.GetDiphoShapeAnalysis(SignalsGenerated[thisSigIndex], "pico_nom", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeightDown*weight*10.*5.99")
      (sX, sX1, sXvA) = PL.GetDiphoShapeAnalysis(SignalsGenerated[thisSigIndex], "pico_nom", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "puWeight*weight*10.*5.99")
      (sXsu, sX1su, sXvAsu) = PL.GetDiphoShapeAnalysis(SignalsGenerated[thisSigIndex], "pico_scale_up", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "weight*10.*5.99")
      (sXsd, sX1sd, sXvAsd) = PL.GetDiphoShapeAnalysis(SignalsGenerated[thisSigIndex], "pico_scale_down", whichSig, CUTS[0], CUTS[1], CUTS[2], CUTS[3], [lA,hA], "HLT_DoublePhoton", "weight*10.*5.99")
      n_postcut = float(sX1r.GetEntries())
      n_gen = float(lookup(whichSig))
      eff = n_postcut / n_gen * 100
      print("Total Efficiency: {:.3f} %".format(eff))

      SaveHists(str(abin_num), whichSig, sXr, sX1r, sXvAr, sX, sX1, dX, dX1, dXvA, sX1pu, sX1pd, sX1su, sX1sd)

    else:
      print("Not enough signal in Alpha Window. Skipping")
      continue


