import ROOT
import numpy
import os
import math
import sys
import pandas

#ROOT.gROOT.SetBatch()

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../../.")
import PlottingPayload as PL

quick = False
doAll = False

if('quick' in sys.argv): quick=True
if('ALL' in sys.argv): doAll=True

#######################################
#Global Variables
LUMI = {}
LUMI["2016"] = 36.050
LUMI["2017"] = 39.670
LUMI["2018"] = 59.320

GEN_ALPHAS = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03]
GEN_X = [200,300,400,500,600,750,1000,1500,2000,3000]

GEN_SHAPE_DIR = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning"
INTERPO_SHAPE_DIR = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning"

#######################################

def FindAndSetMax(*args):
  if len(args) == 1: args = args[0]
  maximum = 0.0
  for i in args:
    i.SetStats(0)
    t = i.GetMaximum()
    if t > maximum:
      maximum = t
  for j in args:
    j.GetYaxis().SetRangeUser(0,maximum*1.35)#should be 1.35 (below as well)
    j.SetLineWidth(2)
  return maximum*1.35


def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)


def linearInterpolate(x, x1, y1, x2, y2):
  return y1 + ( (x - x1) * (y2 - y1) ) / (x2 - x1)

def GetClosestX(ix, ia):
  for ii in range(len(GEN_X)-1):
    lx,hx = GEN_X[ii],GEN_X[ii+1]
    if(ix > lx and ix < hx):
      return lx,hx

def GetClosestAlpha(ix, ia):
  for ii in range(len(GEN_ALPHAS)-1):
    la,ha = GEN_ALPHAS[ii],GEN_ALPHAS[ii+1]
    if(ia > la and ia < ha):
      return la,ha

def GetSignalString(xx, alph):
  phi = round(xx*alph,2)
  sphi = str(phi).replace(".","p")
  #Problem is string is something like X1000A10p0 . Remove the ending p0
  if(sphi.endswith("p0")):
    sphi = sphi.replace("p0","")
  sig = "X{}A{}".format(xx,sphi)
  return sig

def checkFile(fname):
  if(not os.path.exists(fname)):
      print("Cannot Interpolate, File does not exist")
      print(fname)
      return False
  return True

#FIXME See if this is legal
def TrimHist(hist):
  mean,rms = hist.GetMean(), hist.GetRMS()
  WW = 2
  tHist = hist.Clone()
  for bb in range(hist.GetNbinsX()):
    if(hist.GetBinLowEdge(bb) < (mean - WW*rms) or hist.GetBinLowEdge(bb) > (mean + WW*rms)):
      tHist.SetBinContent(bb,0)
    else: 
      tHist.SetBinContent(bb, hist.GetBinContent(bb))

  return tHist.Clone()

def GetAlphaBinDirectory(alphaBin):
  adir = GEN_SHAPE_DIR+"/"+str(alphaBin)
  for ff in os.listdir(adir):
    ndir = os.path.join(adir,ff)
    for nf in os.listdir(ndir):
      if(alphaBin=="ALL"):
        if(os.path.exists(os.path.join(ndir, "arange.txt")) and os.path.exists(os.path.join(ndir, "PLOTS_0.root"))):
          return ndir
      else:
        if(os.path.exists(os.path.join(ndir, "arange.txt")) and os.path.exists(os.path.join(ndir, "PLOTS_{}.root".format(alphaBin)))):
          return ndir

def CopyRangeData(outFolder, alphaBin):
    abin_dir = GetAlphaBinDirectory(alphaBin)
    os.system("cp {}/arange.txt {}/.".format(abin_dir, outFolder))
    os.system("cp {}/DATA.root {}/.".format(abin_dir, outFolder))
    return

def SaveHists(Hist, inputSignal, alphaBin, fname):
    global outDir
    hname = "h_AveDijetMass_1GeV"

    if(fname=="nom"):
      abin_dir = GetAlphaBinDirectory(alphaBin)
      if(alphaBin=="ALL"):
        alphaBinFile = ROOT.TFile("{}/PLOTS_0.root".format(abin_dir), "read")
        outFile = ROOT.TFile(outDir + "/PLOTS_0.root".format(alphaBin), "RECREATE")
      else:
        alphaBinFile = ROOT.TFile("{}/PLOTS_{}.root".format(abin_dir, alphaBin), "read")
        outFile = ROOT.TFile(outDir + "/PLOTS_{}.root".format(alphaBin), "RECREATE")
      dataXM = alphaBinFile.Get("data_XM")
      dataXM1 = alphaBinFile.Get("data_XM1")
      outFile.cd()
      Hist.Write(hname)
      dataXM.Write()
      dataXM1.Write()
    else:
      outFile = ROOT.TFile("{}/{}.root".format(outDir,fname), "recreate")
      outFile.cd()
      Hist.Write(hname)

    outFile.Close()

    return

def GetEfficiency(sig, alphaBin):
  eFile = "{}/{}/{}/{}.txt".format(GEN_SHAPE_DIR, alphaBin, sig, sig)
  if(not checkFile(eFile)): return 0
  eF = open(eFile,"r").readlines()
  return float(eF[0])

def WriteEff(sig, eff):
   global outDir

   effFile= open("{}/{}.txt".format(outDir,sig),"w")
   effFile.write(str(eff))
   effFile.close()
   return

def InterpolateHists(inputSignal, alphaBin, fname):

  in_x = int(inputSignal[1 : inputSignal.find("A")])
  in_phi = float(inputSignal[inputSignal.find("A")+1 :].replace("p","."))
  in_alpha = in_phi / in_x

  noShift = False

  if(in_alpha < min(GEN_ALPHAS) or in_alpha > max(GEN_ALPHAS)):
    print("Requested alpha outside of range. Cannot interpolate")
    return False

  elif(in_x < min(GEN_X) or in_x > max(GEN_X)):
    print("Requested X Mass outside of range. Cannot interpolate")
    return False

  elif(in_x in GEN_X and in_alpha in GEN_ALPHAS):
    print("Known Signal. Doing nothing")
    return False


  elif(in_alpha not in GEN_ALPHAS and in_x in GEN_X):
    print("Known X Mass, unknown alphas. Copying low alpha X mass shape")
    noShift = True
    low_ga, hi_ga = GetClosestAlpha(in_x, in_alpha)
    lowsig=GetSignalString(in_x, low_ga)
    hisig=GetSignalString(in_x, hi_ga)
    
    print("Interpolating between {} and {} signals".format(lowsig, hisig))
    wpoint = 0.0
    print("Mixing Term: {}".format(wpoint))
    
    if(fname=="nom"):
      leff,heff = GetEfficiency(lowsig,alphaBin),GetEfficiency(hisig,alphaBin)
      neweff = linearInterpolate(in_alpha, low_ga, leff, hi_ga, heff)
      WriteEff(inputSignal, neweff)
    
    low_gx, hi_gx = in_x, in_x

  #elif(in_alpha in GEN_ALPHAS and in_x not in GEN_X):
  else:
    print("Known alpha, unknown X mass. Interpolating between Two Signals")
    low_gx, hi_gx = GetClosestX(in_x, in_alpha)
    lowsig=GetSignalString(low_gx, in_alpha)
    hisig=GetSignalString(hi_gx, in_alpha)

    print("Interpolating between {} and {} signals".format(lowsig, hisig))
    wpoint = float(in_x - low_gx) / float(hi_gx - low_gx)
    print("Mixing Term: {}".format(wpoint))

    if(fname=="nom"):
      leff,heff = GetEfficiency(lowsig,alphaBin),GetEfficiency(hisig,alphaBin)
      neweff = linearInterpolate(in_x, low_gx, leff, hi_gx, heff)
      WriteEff(inputSignal, neweff)

  ####################################

  if(fname=="nom"):
    if(alphaBin=="ALL"):
      lowfile = "{}/ALL/{}/PLOTS_0.root".format(GEN_SHAPE_DIR, lowsig)
      hifile = "{}/ALL/{}/PLOTS_0.root".format(GEN_SHAPE_DIR, hisig)
    else:
      lowfile = "{}/{}/{}/PLOTS_{}.root".format(GEN_SHAPE_DIR, alphaBin, lowsig, alphaBin)
      hifile = "{}/{}/{}/PLOTS_{}.root".format(GEN_SHAPE_DIR, alphaBin, hisig, alphaBin)
  else:
    lowfile = "{}/{}/{}/{}.root".format(GEN_SHAPE_DIR, alphaBin, lowsig, fname)
    hifile = "{}/{}/{}/{}.root".format(GEN_SHAPE_DIR, alphaBin, hisig, fname)
  if(not checkFile(lowfile)): return False
  if(not checkFile(hifile)): return False

  lowR = ROOT.TFile(lowfile, "read")
  lowH = lowR.Get("h_AveDijetMass_1GeV")
  low_center = lowH.GetMean()
  low_max = lowH.GetMaximum()

  hiR = ROOT.TFile(hifile, "read")
  hiH = hiR.Get("h_AveDijetMass_1GeV")
  hi_center = hiH.GetMean()
  hi_max = hiH.GetMaximum()

  if(noShift == True):
    new_center = abs(low_center + hi_center) / 2
    new_max = abs(low_max + hi_max) / 2
  else:
    new_center = linearInterpolate(in_x, low_gx, low_center, hi_gx, hi_center)
    new_max = linearInterpolate(in_x, low_gx, low_max, hi_gx, hi_max)

  cdif = new_center - low_center
  newHist = lowH.Clone(inputSignal)
  newHist.Reset()

  cbin = lowH.FindBin(low_center)
  ncbin = lowH.FindBin(new_center)
  bindiff = ncbin - cbin

  for bb in range(lowH.GetNbinsX()):
    if(bb + bindiff > newHist.GetNbinsX()): continue
    newHist.SetBinContent(bb+bindiff, lowH.GetBinContent(bb)*new_max / low_max)

  #Debug help
  print("Centers: {} - {} - {}".format(low_center, new_center, hi_center))
  print("Maxes: {} - {} - {}".format(low_max, new_max, hi_max))
  print("Ints: {} - {} - {}".format(lowH.Integral(), newHist.Integral(), hiH.Integral()))

  #Check if I still need to do this
  hist_low_trim = TrimHist(lowH)
  hist_hi_trim = TrimHist(hiH)

  c1 = ROOT.TCanvas()
  c1.cd()
  FindAndSetMax(lowH, newHist)
  lowH.SetLineColor(ROOT.kBlack)
  lowH.SetFillColor(ROOT.kBlack)
  hiH.SetLineColor(ROOT.kBlack)
  hiH.SetFillColor(ROOT.kBlack)
  newHist.SetLineColor(ROOT.kRed)
  newHist.SetFillStyle(0)
  newHist.SetLineWidth(2)
  lowH.Draw("hist")
  newHist.Draw("histsame")
  hiH.Draw("histsame")
  c1.Print("tmp.png")

  SaveHists(newHist, inputSignal, alphaBin, fname)
 
  return True

inputSignal = sys.argv[1]

for alphaBin in range(0,9+1):
  if(doAll==True): 
    if(alphaBin == 0): alphaBin = "ALL"
    if(alphaBin != "ALL" and alphaBin > 0): break
  print("Starting Alpha Bin {}".format(alphaBin))
  #if(alphaBin != 5): continue

  outDir = "{}/{}/{}".format(INTERPO_SHAPE_DIR, alphaBin, inputSignal)
  MakeFolder(outDir)

  saved = InterpolateHists(inputSignal,alphaBin,"nom")
  if(not quick):
    InterpolateHists(inputSignal,alphaBin,"Sig_PU")
    InterpolateHists(inputSignal,alphaBin,"Sig_PD")
    InterpolateHists(inputSignal,alphaBin,"Sig_SU")
    InterpolateHists(inputSignal,alphaBin,"Sig_SD")
    InterpolateHists(inputSignal,alphaBin,"Sig_nominal")
  if(saved == True):
    CopyRangeData(outDir, alphaBin)
  else: 
    os.system("rm -rf {}".format(outDir))


