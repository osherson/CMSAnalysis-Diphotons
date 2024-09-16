import numpy as np
import ROOT
import sys,os

ROOT.gROOT.SetBatch()

dir_path = os.path.dirname(os.path.realpath(__file__))

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = phi/x
  return x,phi,alpha

def MakeFolder(N):
   import os
   if not os.path.exists(N):
    os.makedirs(N)

int_dir = "../../inputs/Shapes_fromInterpo/unBinned"

oFile = open("integralInfo.csv","w")
oFile.write("X,Phi,alpha,Integral,low_center_int,hi_center_int,low_max_int,hi_max_int,nzero\n")

def getNearestZero(hist, startbin, goUp):
  if(goUp):
    for bb in range(startbin, hist.GetNbinsX()):
      if(hist.GetBinContent(bb)==0):
        return (bb-startbin)
  else:
    for bb in range(startbin, 0, -1):
      if(hist.GetBinContent(bb)==0):
        return (startbin-bb)
  return -999

count=0
for xaa in os.listdir(int_dir):
  #if(count > 10): break
  count += 1
  xm,phim,alpha = getXPhiAlpha(xaa)
  intpath = os.path.join(int_dir,xaa)
  #if(xaa != "X1710A8p55"): continue

  infname = "Sig_nominal"
  if (os.path.exists("{}/{}.root".format(intpath,infname))):
    intfil = ROOT.TFile("{}/{}.root".format(intpath,infname),"read")
    rinthist = intfil.Get("h_alpha_fine")
    #genhist.Rebin(5)
    #inthist.Rebin(5)
  else:
    print("BAD: ",xaa)

  try:
    rinthist.SetLineColor(ROOT.kRed)
    rinthist.SetFillColor(ROOT.kRed)
  except AttributeError:
    print("Bad mass point: {}".format(xaa))
    continue

  ti = rinthist.Integral()
  cbin = rinthist.FindBin(alpha)
  li = rinthist.Integral(0,cbin)
  hi = rinthist.Integral(cbin, rinthist.GetNbinsX())

  mbin = rinthist.GetMaximumBin()
  lmi = rinthist.Integral(0,mbin)
  hmi = rinthist.Integral(mbin, rinthist.GetNbinsX())

  nzero_up = getNearestZero(rinthist, mbin, 1)
  #nzero_down = getNearestZero(rinthist, mbin, 0)
  #nzero = min(nzero_up, nzero_down)

  oFile.write("{},{},{},{:.4f},{:.4f},{:.4f},{:.4f},{:.4f},{}".format(xm, phim, alpha, ti, li, hi, lmi, hmi, nzero_up))
  oFile.write("\n")



