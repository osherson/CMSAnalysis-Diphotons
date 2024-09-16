import ROOT
import numpy
import os
import math
import sys
import pandas
import time
import gc

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

GEN_SHAPE_DIR = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/unBinned"
INTERPO_SHAPE_DIR = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/unBinned"

#######################################

def Make1BinsFromMinToMax(Min,Max):
  BINS = []
  for i in range(int(Max-Min)+1):
    BINS.append(Min+i)
  return numpy.array(BINS)

def Make0p1BinsFromMinToMax(Min,Max):
  BINS = []
  for i in range(int(Max-Min)+1):
    BINS.append(float(Min+i) / float(Max-Min))
  return numpy.array(BINS)

def LookupAndWriteEff(sig,ix, ia, outDir):
  
  refFile = open("/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/EfficiencyInterpolator/EfficiencyFiles/FULL.csv","r")

  ia = round(ia, 3)

  for ll in refFile.readlines():
    ll = ll.rstrip()
    ls = ll.split(",")
    xm = int(ls[0])
    aa = float(ls[1])
    if(xm == ix and aa==ia):
      eff = float(ls[2])
      break

  effFile= open("{}/{}.txt".format(outDir,sig),"w")
  effFile.write(str(eff))
  effFile.close()
  return

#XB = [297.0, 303.0, 310.0, 317.0, 324.0, 331.0, 338.0, 345.0, 352.0, 360.0, 368.0, 376.0, 384.0, 392.0, 400.0, 409.0, 418.0, 427.0, 436.0, 445.0, 454.0, 464.0, 474.0, 484.0, 494.0, 504.0, 515.0, 526.0, 537.0, 548.0, 560.0, 572.0, 584.0, 596.0, 609.0, 622.0, 635.0, 648.0, 662.0, 676.0, 690.0, 704.0, 719.0, 734.0, 749.0, 765.0, 781.0, 797.0, 814.0, 831.0, 848.0, 866.0, 884.0, 902.0, 921.0, 940.0, 959.0, 979.0, 999.0, 1020.0, 1041.0, 1063.0, 1085.0, 1107.0, 1130.0, 1153.0, 1177.0, 1201.0, 1226.0, 1251.0, 1277.0, 1303.0, 1330.0, 1357.0, 1385.0, 1413.0, 1442.0, 1472.0, 1502.0, 1533.0, 1564.0, 1596.0, 1629.0, 1662.0, 1696.0]
X1B = Make1BinsFromMinToMax(297., 3110.) #Steven for making signals over 2000, this becomes a problem. I think you can just change 3110 to something much bigger. Verify this works

#Read AfineB from file
#fineFile = open("/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/ConstructAlphaBins/FineBinEdges.txt","r")
#AfineB = []
#for line in fineFile.readlines():
#  val = float(line)
#  AfineB.append(val)
#fineFile.close()
AfineB = list(numpy.linspace(0.0,0.03, 10000))
AlphaBins = [ 0.003, 0.00347, 0.00395, 0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.00872, 0.0093, 0.01049, 0.01505, 0.03] 

for aa in AlphaBins:
  if(aa not in AfineB): AfineB.append(aa)
AfineB = sorted(AfineB)

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
    print("Xmin, xmax: ", histArr[0].GetXaxis().GetXmin(),histArr[0].GetXaxis().GetXmax())
    print("Hist n bins ", histArr[0].GetNbinsX())
    self._x.setBins(histArr[0].GetNbinsX())
    self._histInts = [h.Integral() for h in histArr]
    self._inxhists = []
    self._cutEff = []

  def morph(self, MM, wpoint, signame, shape):
    #scaled=True
    #self._lowI, self._hiI = computeBoundingIndices(MM, self._massArr)
    self._lowI, self._hiI = 0,1
    print(self._massArr[self._lowI], self._massArr[self._hiI])

    HL = self._histArr[self._lowI].Clone(self._histArr[self._lowI].GetName() + "HL")
    HH = self._histArr[self._hiI].Clone(self._histArr[self._hiI].GetName() + "HH")

    inxhists = [HL, HH]

    print("Bounding Masses: {} - {}".format(self._massArr[self._lowI], self._massArr[self._hiI]))

    rmass = ROOT.RooRealVar("rm_{}".format(signame), "rmass", wpoint, 0., 1.)

    if(shape == "X"):
      RHL = ROOT.RooDataHist("HL_".format(signame), ";DiCluster Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HL)
      RHLR = ROOT.RooHistPdf("HL_AbsReal_{}".format(signame), "", ROOT.RooArgSet(self._x), RHL)
      RHH = ROOT.RooDataHist("HH_{}".format(signame), ";DiCluster Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HH)
      RHHR = ROOT.RooHistPdf("HH_AbsReal_{}".format(signame), "", ROOT.RooArgSet(self._x), RHH)

      RHIM = ROOT.RooIntegralMorph("Hmorph_{}".format(signame), "", RHHR, RHLR, self._x, rmass)
      self.xframe = self._x.frame(ROOT.RooFit.Title(";DiCluster Mass [GeV];Events/GeV"), ROOT.RooFit.Range(0, 10000))
      RHI = RHIM.createHistogram("Hinterpo_{}".format(signame), self._x)

    elif(shape == "alpha"):
      RHL = ROOT.RooDataHist("HL_".format(signame), ";#alpha;Events/GeV", ROOT.RooArgList(self._x), HL)
      RHLR = ROOT.RooHistPdf("HL_AbsReal_{}".format(signame), "", ROOT.RooArgSet(self._x), RHL)
      RHH = ROOT.RooDataHist("HH_{}".format(signame), ";#alpha;Events/GeV", ROOT.RooArgList(self._x), HH)
      RHHR = ROOT.RooHistPdf("HH_AbsReal_{}".format(signame), "", ROOT.RooArgSet(self._x), RHH)

      RHIM = ROOT.RooIntegralMorph("Hmorph_{}".format(signame), "", RHHR, RHLR, self._x, rmass)
      self.xframe = self._x.frame(ROOT.RooFit.Title(";#alpha;Events/GeV"), ROOT.RooFit.Range(0, 1.))
      RHI = RHIM.createHistogram("Hinterpo_{}".format(signame), self._x)

    ##
    ##
    c1 = ROOT.TCanvas()
    c1.cd()
    ll = ROOT.TLegend(0.6,0.7,0.8,0.95)
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
    rm = rr.GetMean()
    rr.SetTitle("OUT")
    rr.SetLineColor(ROOT.kBlack)
    ll.AddEntry(rr, "OUT")
    FindAndSetMax([HH, HL, rr])
    rr.GetXaxis().SetRangeUser(0.2*rm, 1.8*rm)
    HL.GetXaxis().SetRangeUser(0.2*rm, 1.8*rm)
    HH.GetXaxis().SetRangeUser(0.2*rm, 1.8*rm)
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


def getXBinIndex(num):
  for ii in range(0,len(X1B)):
    if num < X1B[ii]:
      return ii
def getABinIndex(num):
  for ii in range(0,len(AfineB)):
    if num < AfineB[ii]:
      return ii


def TrimWideHist(lowhist, hihist, shape):
  global AfineB
  lowmean,lowrms = lowhist.GetMean(), lowhist.GetRMS()
  himean,hirms = hihist.GetMean(), hihist.GetRMS()
  WW = 2

  if(shape=="X"):
    botidx = getXBinIndex(lowmean - WW*lowrms)
    topidx = getXBinIndex(himean + WW*hirms)
    newBins = Make1BinsFromMinToMax(0., 10000.)
    bval = X1B[botidx]
    tval = X1B[topidx]
  elif(shape=="alpha"):
    botidx = getABinIndex(lowmean - (WW+1)*lowrms)
    topidx = getABinIndex(himean + (WW+1)*hirms)
    newBins = AfineB
    #AfineB = numpy.linspace(-0.03,0.03, 1201)

    #Read AfineB from file
    #fineFile = open("/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/ConstructAlphaBins/FineBinEdges.txt","r")
    #newBins = []
    #for (ii,line) in enumerate(fineFile.readlines()):
    #  if(ii %2 == 1): continue
    #  val = float(line)
    #  newBins.append(val)
    #fineFile.close()

    bval = AfineB[botidx]
    tval = AfineB[topidx]

    print(bval, tval)

  tl_Hist = ROOT.TH1D("{}_t".format(lowhist.GetName),"",len(newBins)-1, numpy.array(newBins))
  th_Hist = ROOT.TH1D("{}_t".format(hihist.GetName),"",len(newBins)-1, numpy.array(newBins))

  for bb in range(tl_Hist.GetNbinsX()):
    if( tl_Hist.GetBinLowEdge(bb) < bval or tl_Hist.GetBinLowEdge(bb) > tval):
      continue
      tl_Hist.SetBinContent(bb,0)
      th_Hist.SetBinContent(bb,0)
    else:
      tl_Hist.SetBinContent(bb, lowhist.GetBinContent(lowhist.FindBin(tl_Hist.GetBinLowEdge(bb))))
      th_Hist.SetBinContent(bb, hihist.GetBinContent(hihist.FindBin(tl_Hist.GetBinLowEdge(bb))))

  if(shape=="alpha"):
   #Maybe
    tl_Hist.Smooth()
    th_Hist.Smooth()

  return tl_Hist.Clone(), th_Hist.Clone()

def SaveHists(Hist, inputSignal, hname, fname, outDir):

    outFname="{}/{}.root".format(outDir,fname)
    if(hname=="h_AveDijetMass_1GeV"):
      outFile = ROOT.TFile(outFname, "recreate")
    else:
      outFile = ROOT.TFile(outFname, "update")
    outFile.cd()
    Hist.Write(hname)

    outFile.Close()

    return

def InterpolateHists(inputSignal, shape, fname, outDir, force=False):

  in_x = int(inputSignal[1 : inputSignal.find("A")])
  in_phi = float(inputSignal[inputSignal.find("A")+1 :].replace("p","."))
  in_alpha = in_phi / in_x

  if(shape=="X"): hname = "h_AveDijetMass_1GeV"
  elif(shape=="alpha"): hname = "h_alpha_fine"

  if(in_alpha < min(GEN_ALPHAS) or in_alpha > max(GEN_ALPHAS)):
    print("Requested alpha outside of range. Cannot interpolate")
    return False

  elif(in_x < min(GEN_X) or in_x > max(GEN_X)):
    print("Requested X Mass outside of range. Cannot interpolate")
    return False

  elif(in_x in GEN_X and in_alpha in GEN_ALPHAS and force==False):
    print("Known Signal. Doing nothing")
    return False

  elif(in_x in GEN_X and in_alpha in GEN_ALPHAS and force==True):
    print("Forcing Interpolation of Known Signal")
#    idx_ina = [a for a in range(len(GEN_ALPHAS)) if GEN_ALPHAS[a] == in_alpha][0]
#    if(idx_ina == 0 or idx_ina == len(GEN_ALPHAS)-1): 
#      print("Can't do that!")
#      return False
#    low_ga, hi_ga = GEN_ALPHAS[idx_ina - 1], GEN_ALPHAS[idx_ina + 1]
#    lowsig=GetSignalString(in_x, low_ga)
#    hisig=GetSignalString(in_x, hi_ga)
#
#    print("Interpolating between {} and {} signals".format(lowsig, hisig))
#    wpoint = float(in_alpha - low_ga) / float(hi_ga - low_ga)
#    print("Mixing Term: {}".format(wpoint))
#
#    if(fname=="Sig_nominal" and shape=="X"): #Just so I only do this once
#      LookupAndWriteEff(inputSignal, in_x,in_alpha, outDir)
#
#    low_gx, hi_gx = in_x, in_x
    print("Known alpha, unknown X mass. Interpolating between Two Signals")
    idx_ina = [a for a in range(len(GEN_X)) if GEN_X[a] == in_x][0]
    if(idx_ina == 0 or idx_ina == len(GEN_X)-1): 
      print("Can't do that!")
      return False
    low_gx, hi_gx = GEN_X[idx_ina - 1], GEN_X[idx_ina + 1]
#    low_gx, hi_gx = GetClosestX(in_x, in_alpha)
    lowsig=GetSignalString(low_gx, in_alpha)
    hisig=GetSignalString(hi_gx, in_alpha)

    print("Interpolating between {} and {} signals".format(lowsig, hisig))
    wpoint = float(in_x - low_gx) / float(hi_gx - low_gx)
    print("Mixing Term: {}".format(wpoint))

    if(fname=="Sig_nominal" and shape=="X"): #Just so I only do this once
      LookupAndWriteEff(inputSignal, in_x,in_alpha, outDir)

    low_ga, hi_ga = in_alpha, in_alpha

  elif(in_alpha in GEN_ALPHAS and in_x not in GEN_X):
    print("Known alpha, unknown X mass. Interpolating between Two Signals")
    low_gx, hi_gx = GetClosestX(in_x, in_alpha)
    lowsig=GetSignalString(low_gx, in_alpha)
    hisig=GetSignalString(hi_gx, in_alpha)

    print("Interpolating between {} and {} signals".format(lowsig, hisig))
    wpoint = float(in_x - low_gx) / float(hi_gx - low_gx)
    print("Mixing Term: {}".format(wpoint))

    if(fname=="Sig_nominal" and shape=="X"): #Just so I only do this once
      LookupAndWriteEff(inputSignal, in_x,in_alpha, outDir)

    low_ga, hi_ga = in_alpha, in_alpha
  elif(in_alpha not in GEN_ALPHAS and in_x in GEN_X):
    print("Known X Mass, unknown alphas. Interpolating between two signals")
    low_ga, hi_ga = GetClosestAlpha(in_x, in_alpha)
    lowsig=GetSignalString(in_x, low_ga)
    hisig=GetSignalString(in_x, hi_ga)

    print("Interpolating between {} and {} signals".format(lowsig, hisig))
    wpoint = float(in_alpha - low_ga) / float(hi_ga - low_ga)
    print("Mixing Term: {}".format(wpoint))

    if(fname=="Sig_nominal" and shape=="X"): #Just so I only do this once
      LookupAndWriteEff(inputSignal, in_x,in_alpha, outDir)

    low_gx, hi_gx = in_x, in_x
####################################
#The hard case
  elif(in_alpha not in GEN_ALPHAS and in_x not in GEN_X): 
    print("Interpolated signal does not match generated alpha. Interpolating Twice")
    low_gx, hi_gx = GetClosestX(in_x, in_alpha)
    print(low_gx, hi_gx)

    faux_sig_low = GetSignalString(low_gx, in_alpha)
    faux_sig_hi = GetSignalString(hi_gx, in_alpha)
    #Now we have a 'known' X, unknown phi, follow that workflow

    midhists = []

    #################################################################################
    #Tried to do this in a loop but had some weird problem that wouldn't let me save both histograms
    f1_in_x = int(faux_sig_low[1 : faux_sig_low.find("A")])
    f1_in_phi = float(faux_sig_low[faux_sig_low.find("A")+1 :].replace("p","."))
    f1_in_alpha = f1_in_phi / f1_in_x
    f1_low_ga, f1_hi_ga = GetClosestAlpha(f1_in_x, f1_in_alpha)
    f1_lowsig=GetSignalString(f1_in_x, f1_low_ga)
    f1_hisig=GetSignalString(f1_in_x, f1_hi_ga)

    print("Interpolating between {} and {} signals".format(f1_lowsig, f1_hisig))
    wpoint = float(f1_in_alpha - f1_low_ga) / float(f1_hi_ga - f1_low_ga)
    print("Mixing Term: {}".format(wpoint))

    f1_lowfile = "{}/{}/{}.root".format(GEN_SHAPE_DIR, f1_lowsig, fname)
    f1_hifile = "{}/{}/{}.root".format(GEN_SHAPE_DIR, f1_hisig, fname)
    if(not checkFile(f1_lowfile)): return False
    if(not checkFile(f1_hifile)): return False

    f1_lowR, f1_hiR = ROOT.TFile(f1_lowfile, "read"), ROOT.TFile(f1_hifile, "read")
    f1_lowH, f1_hiH = f1_lowR.Get(hname), f1_hiR.Get(hname)
    f1_hist_low_trim, f1_hist_hi_trim= TrimWideHist(f1_lowH, f1_hiH, shape)
    masslist = [f1_in_x, f1_in_x]
    histlist = [f1_hist_low_trim, f1_hist_hi_trim]
    MP = HC(histlist, masslist)
    newHist, _ = MP.morph(f1_in_x, wpoint, faux_sig_low, shape)
    midhists.append([faux_sig_low, newHist])

    #######
    print(faux_sig_hi)
    f2_in_x = int(faux_sig_hi[1 : faux_sig_hi.find("A")])
    f2_in_phi = float(faux_sig_hi[faux_sig_hi.find("A")+1 :].replace("p","."))
    f2_in_alpha = f2_in_phi / f2_in_x
    f2_low_ga, f2_hi_ga = GetClosestAlpha(f2_in_x, f2_in_alpha)
    f2_lowsig=GetSignalString(f2_in_x, f2_low_ga)
    f2_hisig=GetSignalString(f2_in_x, f2_hi_ga)

    print("Interpolating between {} and {} signals".format(f2_lowsig, f2_hisig))
    wpoint = float(f2_in_alpha - f2_low_ga) / float(f2_hi_ga - f2_low_ga)
    print("Mixing Term: {}".format(wpoint))


    f2_lowfile = "{}/{}/{}.root".format(GEN_SHAPE_DIR, f2_lowsig, fname)
    f2_hifile = "{}/{}/{}.root".format(GEN_SHAPE_DIR, f2_hisig, fname)
    if(not checkFile(f2_lowfile)): return False
    if(not checkFile(f2_hifile)): return False

    f2_lowR, f2_hiR = ROOT.TFile(f2_lowfile, "read"), ROOT.TFile(f2_hifile, "read")
    f2_lowH, f2_hiH = f2_lowR.Get(hname), f2_hiR.Get(hname)
    #f2_hist_low_trim, f2_hist_hi_trim= TrimHist(f2_lowH), TrimHist(f2_hiH)
    f2_hist_low_trim, f2_hist_hi_trim= TrimWideHist(f2_lowH, f2_hiH, shape)
    masslist = [f2_in_x, f2_in_x]
    histlist = [f2_hist_low_trim, f2_hist_hi_trim]
    MP = HC(histlist, masslist)
    newHist, _ = MP.morph(f2_in_x, wpoint, faux_sig_hi, shape)
    midhists.append([faux_sig_hi, newHist])
    #######

    ##Now midhists contains intermediate signals
    c_sig_low, c_sig_hi = midhists[0][0], midhists[1][0]
    c_x_low = int(c_sig_low[1:c_sig_low.find("A")])
    c_x_hi = int(c_sig_hi[1:c_sig_hi.find("A")])
    c_phi_low = float(c_sig_low[c_sig_low.find("A")+1 :].replace("p","."))
    c_phi_hi = float(c_sig_hi[c_sig_hi.find("A")+1 :].replace("p","."))
    c_a_low, c_a_hi = c_phi_low/c_x_low, c_phi_hi/c_x_hi
    print("Interpolating between {} and {} signals".format(c_sig_low, c_sig_hi))

    c_wpoint = float(in_x - c_x_low) / float(c_x_hi - c_x_low)
    print("Mixing Term: {}".format(wpoint))

    if(fname=="Sig_nominal" and shape=="X"): #Just so I only do this once
      LookupAndWriteEff(inputSignal, in_x,in_alpha, outDir)

    masslist = [c_x_low, c_x_hi]
    histlist = [midhists[0][1], midhists[1][1]]

    MP = HC(histlist, masslist)
    newHist, _ = MP.morph(in_x, wpoint, inputSignal, shape)

    SaveHists(newHist, inputSignal, hname, fname, outDir)

    return True

####################################
  lowfile = "{}/{}/{}.root".format(GEN_SHAPE_DIR, lowsig, fname)
  hifile = "{}/{}/{}.root".format(GEN_SHAPE_DIR, hisig, fname)
  print("Getting file: ", lowfile)
  if(not checkFile(lowfile)): return False
  if(not checkFile(hifile)): return False

  lowR = ROOT.TFile(lowfile, "read")
  lowH = lowR.Get(hname)

  hiR = ROOT.TFile(hifile, "read")
  hiH = hiR.Get(hname)

  hist_low_trim, hist_hi_trim = TrimWideHist(lowH, hiH, shape)

  if(shape=="X"):
    masslist = [low_gx, hi_gx]
  elif(shape=="alpha"):
    masslist = [low_ga, hi_ga]
  histlist = [hist_low_trim, hist_hi_trim]

  MP = HC(histlist, masslist)
  newHist, _ = MP.morph(in_x, wpoint, inputSignal, shape)

  SaveHists(newHist, inputSignal, hname, fname, outDir)

  return True

inputSignal = sys.argv[1]
shape = sys.argv[2]
treeName = sys.argv[3]

print(inputSignal)
print(shape)
print(treeName)

forceInt = True
if(forceInt):
  INTERPO_SHAPE_DIR += "_Known"

outDir = "{}/{}".format(INTERPO_SHAPE_DIR, inputSignal)
MakeFolder(outDir)

InterpolateHists(inputSignal,shape,treeName,outDir,force=forceInt)

#This doesn't work, must call as command line arg
#InterpolateHists(inputSignal,"Sig_PU",outDir)
#InterpolateHists(inputSignal,"Sig_PD",outDir)
#InterpolateHists(inputSignal,"Sig_SU",outDir)
#InterpolateHists(inputSignal,"Sig_SD",outDir)
#InterpolateHists(inputSignal,"Sig_nominal",outDir)

