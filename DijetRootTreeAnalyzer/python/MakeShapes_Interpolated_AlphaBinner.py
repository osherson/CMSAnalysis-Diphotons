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

effThreshold = 0.05 #Only save signals with x% efficiency or greater

Interp_Dir = "{}/../inputs/Shapes_fromInterpo/unBinned/".format(dir_path)
OUTDIR = "{}/../inputs/Shapes_fromInterpo/alphaBinning/".format(dir_path)

def doOneInput(N, sig, h, H, S, norm = False):

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

def GetXPhiAlpha(signal):
  x = int(signal[signal.find("X") + 1 : signal.find("A")])
  phi = float(signal[signal.find("A") + 1 : ].replace("p","."))
  alpha = phi / x
  return x,phi,alpha


AlphaBins = [0.003, 0.00347, 0.00395, 0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.00872, 0.0093, 0.00989, 0.01049, 0.0111, 0.01173, 0.01237, 0.01302, 0.01368, 0.01436,0.01505, 0.01575, 0.01647, 0.0172, 0.01794, 0.0187, 0.01947, 0.02026, 0.02106, 0.02188, 0.02271, 0.02356, 0.02443, 0.02531, 0.02621, 0.02713, 0.02806, 0.02901, 0.03]

def GetAlphaIndices(mean, rms):
  ww = 4
  low,hi = mean - ww*rms, mean + ww*rms

  lowidx,hidx = 0, len(AlphaBins)
  for ii in range(0,len(AlphaBins)):
    if(AlphaBins[ii] > low):
      lowidx = ii-1
      break
  for ii in range(len(AlphaBins)-1,0,-1):
    if(AlphaBins[ii] < hi):
      hidx = ii-1
      break

  return lowidx, hidx

def CopyHists(sig, odir):
  for fil in os.listdir(os.path.join(Interp_Dir, sig)):
    if(fil.endswith(".root")):
      os.system("cp {} {}/.".format(os.path.join(Interp_Dir,sig,fil), odir))
  return

def WriteEff(sig, eff, odir):

   effFile= open("{}/{}.txt".format(odir,sig),"w")
   effFile.write(str(eff))
   effFile.close()
   return

SignalsGenerated = {}
for ff in os.listdir(Interp_Dir):
    if(ff.startswith("X")):thisxa=ff
    else: continue
    if(thisxa != "X570A10p83"):continue
    this_x = int(thisxa[1:thisxa.find("A")])
    this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
    if(os.path.exists("{}/{}/Sig_nominal.root".format(Interp_Dir,ff))): 
      SignalsGenerated[thisxa] = os.path.join(Interp_Dir, ff)

SignalsGenerated.keys()
print(SignalsGenerated)

for sig,fil in SignalsGenerated.items():

  if(sig[-1]=="p"): sig = sig[:-1]
  print("Beginning Signal {}".format(sig))

  thisx, thisphi, thisalpha = GetXPhiAlpha(sig)

  fname = fil + "/Sig_nominal.root"
  effFile = fil + "/{}.txt".format(sig)
  
  sigFile = ROOT.TFile(fname, "read")
  aHist = sigFile.Get("h_alpha_fine")
  eF = open(effFile,"r").readlines()
  eff = float(eF[0])

  amean,arms = aHist.GetMean(), aHist.GetRMS()

  astart, astop = GetAlphaIndices(amean,arms)

  for abin_num in range(astart,astop):
    #if(abin_num != 3): continue

    lA = AlphaBins[abin_num]
    hA = AlphaBins[abin_num+1]
    #print("---------------------------------------------------------------------------")
    #print("Alpha bin: ")
    #print("{}: {} - {}".format(abin_num, lA, hA))

    lBin,hBin = aHist.FindBin(lA), aHist.FindBin(hA)
    zbin,tbin = aHist.FindBin(0.0), aHist.FindBin(0.03)

    frac = aHist.Integral(lBin,hBin) / aHist.Integral(zbin, tbin)
    newEff = eff * frac

    if(newEff < effThreshold): continue
    newd = "{}/../inputs/Shapes_fromInterpo/alphaBinning/{}/{}".format(dir_path,abin_num,sig)
    PL.MakeFolder(newd)

    newFolder = OUTDIR +  str(abin_num) + "/" + sig
    PL.MakeFolder(newFolder)

    CopyHists(sig, newd)
    WriteEff(sig, newEff, newd)
    rfile = open("{}/arange.txt".format(newd),"w")
    rfile.write("{},{}".format(lA,hA))

#Todo: Change alpha binning in the Gen Signals. Copy PLOTS_0.root and the data

