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

effThreshold = 0.10 #Only save signals with x% efficiency or greater

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

XB = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0, 1731.0, 1766.0, 1802.0, 1839.0, 1877.0, 1915.0, 1954.0, 1994.0, 2035.0, 2077.0, 2119.0, 2162.0, 2206.0, 2251.0, 2297.0, 2344.0, 2392.0, 2441.0,2491.0, 2542.0, 2594.0, 2647.0, 2701.0, 2756.0, 2812.0, 2869.0, 2927.0, 2987.0, 3048.0, 3110.0]
AlphaBins = [0.003, 0.00347, 0.00395, 0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.00872, 0.0093, 0.00989, 0.01049, 0.0111, 0.01173, 0.01237, 0.01302, 0.01368, 0.01436,0.01505, 0.01575, 0.01647, 0.0172, 0.01794, 0.0187, 0.01947, 0.02026, 0.02106, 0.02188, 0.02271, 0.02356, 0.02443, 0.02531, 0.02621, 0.02713, 0.02806, 0.02901, 0.03]

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


def GetAlphaIndices(mean, rms):
  ww = 4
  low,hi = mean - ww*rms, mean + ww*rms

  lowidx,hidx = 0, len(AlphaBins)
  for ii in range(0,len(AlphaBins)):
    if(AlphaBins[ii] > low):
      lowidx = ii-1
      break
  for ii in range(len(AlphaBins)-1,0,-1):
    #print(AlphaBins[ii])
    if(AlphaBins[ii] < hi):
      hidx = ii+1
      break

  if(hidx == len(AlphaBins)): hidx -= 1
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
    #if(thisxa != "X570A10p83"):continue #Testing
    this_x = int(thisxa[1:thisxa.find("A")])
    this_phi = float(thisxa[thisxa.find("A")+1:].replace("p","."))
    #if(this_x != 600): continue
    if(os.path.exists("{}/{}/Sig_nominal.root".format(Interp_Dir,ff))): 
      SignalsGenerated[thisxa] = os.path.join(Interp_Dir, ff)

SignalsGenerated.keys()
#print(SignalsGenerated)

for sig,fil in SignalsGenerated.items():
  #if("X5" not in sig and "X6" not in sig and "X4" not in sig): continue
  #if("X5" in sig or "X6" in sig or "X4" in sig): continue
  #if("X510A4" not in sig): continue

  if(sig[-1]=="p"): sig = sig[:-1]
  print("\n---------------------------------------------------------------------------")
  print("Beginning Signal {}".format(sig))

  thisx, thisphi, thisalpha = GetXPhiAlpha(sig)
  print("X: {}, Phi: {}, Alpha: {}".format(thisx, thisphi, thisalpha))
  #if(thisalpha != 0.025): continue

  fname = fil + "/Sig_nominal.root"
  effFile = fil + "/{}.txt".format(sig)

  if(not os.path.exists(fname)): 
    print("File does not exist. Skipping Signal")
    print(fname)
    continue
  
  try:
    sigFile = ROOT.TFile(fname, "read")
    sX1 = sigFile.Get("h_AveDijetMass_1GeV")
    sX1.Scale(1/sX1.Integral())
    sX1.SetName("h_AveDijetMass_1GeV")
    sX = sX1.Clone("{}_XM1".format(sig))
    sX.Rebin(len(XB)-1, "{}_XM".format(sig), numpy.array(XB))
    aHist = sigFile.Get("h_alpha_fine")
    eF = open(effFile,"r").readlines()
    eff = float(eF[0])
    amean,arms = aHist.GetMean(), aHist.GetRMS()
  except AttributeError:
    print("Something strange with {}".format(sig))
    continue

  astart, astop = GetAlphaIndices(amean,arms)
  #print(amean-4*arms, amean, amean + 4*arms)
  #print(astart, astop)
  #print(AlphaBins[astart], AlphaBins[astop])

  for abin_num in range(astart,astop):
    #if(abin_num != 3): continue

    lA = AlphaBins[abin_num]
    hA = AlphaBins[abin_num+1]

    lBin,hBin = aHist.FindBin(lA), aHist.FindBin(hA)
    zbin,tbin = aHist.FindBin(0.0), aHist.FindBin(0.03)

    frac = aHist.Integral(lBin,hBin) / aHist.Integral(zbin, tbin)
    newEff = eff * frac

    print("\nAlpha bin: ")
    print("{}: {} - {}".format(abin_num, lA, hA))
    if(frac < effThreshold): 
      print("Only {:.2f}% events in bin. Skipping".format(frac*100))
      continue
    else:
      print("Fraction of events in alpha bin: {:.2f}%".format(frac*100))

    newd = "{}/../inputs/Shapes_fromInterpo/alphaBinning/{}/{}".format(dir_path,abin_num,sig)
    PL.MakeFolder(newd)

    newFolder = OUTDIR +  str(abin_num) + "/" + sig
    PL.MakeFolder(newFolder)

    dataFile = ROOT.TFile("{}/../inputs/Shapes_DATA/alphaBinning/{}/DATA.root".format(dir_path,abin_num))
    os.system("cp {}/../inputs/Shapes_DATA/alphaBinning/{}/DATA.root {}/DATA.root".format(dir_path,abin_num, newd))
    dX = dataFile.Get("data_XM")
    dX1 = dataFile.Get("data_XM1")
    dXvA = dataFile.Get("data_XvA")

    CopyHists(sig, newd)
    WriteEff(sig, newEff, newd)
    rfile = open("{}/arange.txt".format(newd),"w")
    rfile.write("{},{}".format(lA,hA))


    oF = TFile(newd+"/PLOTS_"+str(abin_num)+".root", "recreate")
    sX.Write()
    sX1.Write()
    dX.Write()
    dX1.Write()

    oF.Close()

