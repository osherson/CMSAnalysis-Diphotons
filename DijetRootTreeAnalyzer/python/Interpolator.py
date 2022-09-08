import ROOT
import numpy
import os
import math
import sys
import pandas

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../../.")
import PlottingPayload as PL

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

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

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

def computeBoundingIndices(M, anchors):
  lowI, highI = 0,0

  minlDiff=9999
  minhDiff=9999
  for ind, N in enumerate(anchors):
    if(N < M):
      if (M - N < minlDiff): 
        minlDiff = M - N
        lowI = ind

    elif(N > M):
      if (N - M < minhDiff): 
        minhDiff = N - M
        highI = ind

  return lowI, highI

def integralInterpo(Min, INTS, M, log=True):
  MSS = [float(k) for k in Min]

  SPLINE = 0
  if log:
    IL, IH = computeBoundingIndices(M, MSS)
    TF = ROOT.TF1("tempF", "[1]*TMath::Exp((x-[0])*TMath::Log([3]/[1])/([2]-[0]))", M-50, M+50)
    TF.SetParameter(0, MSS[IL])
    TF.SetParameter(1, INTS[IL])
    TF.SetParameter(2, MSS[IH])
    TF.SetParameter(3, INTS[IH])
    SPLINE = TF.Eval(M)

  else:
    LINTS = [numpy.log(INTS) for sl in range(len(INTS.keys()))]
    TG = ROOT.TGraph(len(MSS), numpy.array(MSS), numpy.array(LINTS[sl]))
    TG.SetBit(ROOT.TGraph.kIsSortedX)
    SPLINE = TG.Eval(M)

  return SPLINE

class HC:

  def __init__(self, histArr, massArr):
    self._massArr = massArr
    print("MASSARR: {}".format(massArr))
    self._histArr = histArr
    self._x  = ROOT.RooRealVar("x","x",histArr[0].GetXaxis().GetXmin(),histArr[0].GetXaxis().GetXmax())
    #self._x  = ROOT.RooRealVar("x","x",histArr[0].GetXaxis().GetXmin(),2100.)
    self._x.setBins(histArr[0].GetNbinsX())
    self._histInts = [h.Integral() for h in histArr]
    self._inxhists = []
    self._cutEff = []

  def morph(self, MM, wpoint, signame):
    #scaled=True
    #self._lowI, self._hiI = computeBoundingIndices(MM, self._massArr)
    self._lowI, self._hiI = 0,1
    print(self._massArr[self._lowI], self._massArr[self._hiI])

    HL = self._histArr[self._lowI].Clone(self._histArr[self._lowI].GetName() + "HL")
    HH = self._histArr[self._hiI].Clone(self._histArr[self._hiI].GetName() + "HH")

    inxhists = [HL, HH]

    print("Bounding Masses: {} - {}".format(self._massArr[self._lowI], self._massArr[self._hiI]))

    rmass = ROOT.RooRealVar("rm_{}".format(signame), "rmass", wpoint, 0., 1.)

    RHL = ROOT.RooDataHist("HL_".format(signame), ";DiCluster Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HL)
    RHLR = ROOT.RooHistPdf("HL_AbsReal_{}".format(signame), "", ROOT.RooArgSet(self._x), RHL)
    RHH = ROOT.RooDataHist("HH_{}".format(signame), ";DiCluster Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HH)
    RHHR = ROOT.RooHistPdf("HH_AbsReal_{}".format(signame), "", ROOT.RooArgSet(self._x), RHH)

    RHIM = ROOT.RooIntegralMorph("Hmorph_{}".format(signame), "", RHHR, RHLR, self._x, rmass)
    self.xframe = self._x.frame(ROOT.RooFit.Title(";DiCluster Mass [GeV];Events/GeV"), ROOT.RooFit.Range(0, 10000))
    RHI = RHIM.createHistogram("Hinterpo_{}".format(signame), self._x)

    ##
    ##
    c1 = ROOT.TCanvas()
    c1.cd()
    ll = ROOT.TLegend(0.6,0.5,0.8,0.75)
    ll.SetBorderSize(0)
    HH.SetTitle("HH")
    HH.SetLineColor(ROOT.kRed)
    HL.SetLineColor(ROOT.kGreen)
    HL.SetLineWidth(2)
    HL.SetTitle("HL")

    ll.AddEntry(HL, "In_Low")
    ll.AddEntry(HH, "In_High")
    ##
    rr = RHI.Clone(signame+"new")
    rr.SetTitle("OUT")
    rr.SetLineColor(ROOT.kBlack)
    ll.AddEntry(rr, "OUT")
    FindAndSetMax([HH, HL, rr])
    HH.Draw("hist")
    HL.Draw("histsame")
    rr.Draw("histsame")
    ll.Draw("same")
    c1.Print("tc3.png")
    ##

    return RHI.Clone(signame+"new"), inxhists

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
  phi = xx*alph
  sphi = str(phi).replace(".0","")
  sphi = sphi.replace(".","p")
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

  if(in_alpha < min(GEN_ALPHAS) or in_alpha > max(GEN_ALPHAS)):
    print("Requested alpha outside of range. Cannot interpolate")

  if(in_x < min(GEN_X) or in_x > max(GEN_X)):
    print("Requested X Mass outside of range. Cannot interpolate")

  if(in_alpha in GEN_ALPHAS and in_x not in GEN_X):
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

  elif(in_alpha not in GEN_ALPHAS and in_x in GEN_X):
    print("Known X Mass, unknown alphas. Interpolating between two signals")
    low_ga, hi_ga = GetClosestAlpha(in_x, in_alpha)
    lowsig=GetSignalString(in_x, low_ga)
    hisig=GetSignalString(in_x, hi_ga)

    print("Interpolating between {} and {} signals".format(lowsig, hisig))
    wpoint = float(in_alpha - low_ga) / float(hi_ga - low_ga)
    print("Mixing Term: {}".format(wpoint))

    if(fname=="nom"):
      leff,heff = GetEfficiency(lowsig,alphaBin),GetEfficiency(hisig,alphaBin)
      neweff = linearInterpolate(in_alpha, low_ga, leff, hi_ga, heff)
      WriteEff(inputSignal, neweff)

    low_gx, hi_gx = in_x, in_x

  elif(in_alpha not in GEN_ALPHAS and in_x not in GEN_X): 
    print("Interpolated signal does not match generated alpha. Interpolating Twice")

  if(fname=="nom"):
    lowfile = "{}/{}/{}/PLOTS_{}.root".format(GEN_SHAPE_DIR, alphaBin, lowsig, alphaBin)
    hifile = "{}/{}/{}/PLOTS_{}.root".format(GEN_SHAPE_DIR, alphaBin, hisig, alphaBin)
  else:
    lowfile = "{}/{}/{}/{}.root".format(GEN_SHAPE_DIR, alphaBin, lowsig, fname)
    hifile = "{}/{}/{}/{}.root".format(GEN_SHAPE_DIR, alphaBin, hisig, fname)
  if(not checkFile(lowfile)): return
  if(not checkFile(hifile)): return

  lowR = ROOT.TFile(lowfile, "read")
  lowH = lowR.Get("h_AveDijetMass_1GeV")

  hiR = ROOT.TFile(hifile, "read")
  hiH = hiR.Get("h_AveDijetMass_1GeV")

  hist_low_trim = TrimHist(lowH)
  hist_hi_trim = TrimHist(hiH)

  masslist = [low_gx, hi_gx]
  #histlist = [lowH, hiH]
  histlist = [hist_low_trim, hist_hi_trim]

  MP = HC(histlist, masslist)
  newHist, _ = MP.morph(in_x, wpoint, inputSignal)

  SaveHists(newHist, inputSignal, alphaBin, fname)

 
  return

inputSignal = sys.argv[1]
alphaBin = 9 #ToDo do this in all alpha bins

outDir = "{}/{}/{}".format(INTERPO_SHAPE_DIR, alphaBin, inputSignal)
MakeFolder(outDir)

#CopyRangeData(outDir, alphaBin)
InterpolateHists(inputSignal,alphaBin,"nom")
#InterpolateHists(inputSignal,alphaBin,"Sig_PU")
#InterpolateHists(inputSignal,alphaBin,"Sig_PD")
#InterpolateHists(inputSignal,alphaBin,"Sig_SU")
#InterpolateHists(inputSignal,alphaBin,"Sig_SD")
#InterpolateHists(inputSignal,alphaBin,"Sig_nominal")


