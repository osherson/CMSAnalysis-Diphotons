import ROOT
import numpy
import os
import math
import sys
import pandas 
sys.path.append("../.")
#import PlottingPayload as PL

#ROOT.gROOT.SetBatch()


year = sys.argv[1]
in_xphi = sys.argv[2]

in_x = float(in_xphi[1 : in_xphi.find("A")])
in_phi = float(in_xphi[in_xphi.find("A")+1 :].replace("p","."))
if(in_x.is_integer()): in_x = int(in_x)
if(in_phi.is_integer()): in_phi = int(in_phi)

print("\n Getting Expected Efficiency for X {} Phi {} Signal".format(in_x, in_phi))

### Efficiency Files ###
infoFile = "CutInfoFiles/cutInfo_{}cutInfo.csv".format(year)
dists = {}
xmasses = []
phimasses = []

df = pandas.read_csv(infoFile,index_col=0)
print(df.head())

exit()

outFileName = "OutFiles/{}/X{}phi{}.root".format(year,in_x,in_phi)

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
    self._histArr = histArr
    self._x  = ROOT.RooRealVar("x","x",histArr[0].GetXaxis().GetXmin(),histArr[0].GetXaxis().GetXmax())
    self._x.setBins(histArr[0].GetNbinsX())
    self._histInts = [h.Integral() for h in histArr]
    self._inxhists = []

  def morph(self, MM, N, scaled=False):
    self._lowI, self._hiI = computeBoundingIndices(MM, self._massArr)
    HL = self._histArr[self._lowI].Clone()
    HH = self._histArr[self._hiI].Clone()

    inxhists = [HL, HH]

    print(self._massArr[self._lowI], self._massArr[self._hiI])

    alpha = (float(MM) - float(self._massArr[self._lowI]))/(float(self._massArr[self._hiI]) - float(self._massArr[self._lowI]))
    rmass = ROOT.RooRealVar("rm_%d" % MM, "rmass", alpha, 0., 1.)

    RHL = ROOT.RooDataHist("HL_%d" % MM, ";DiCluster Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HL)
    RHLR = ROOT.RooHistPdf("HL_AbsReal_%d" % MM, "", ROOT.RooArgSet(self._x), RHL)
    RHH = ROOT.RooDataHist("HH_%d" % MM, ";DiCluster Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HH)
    RHHR = ROOT.RooHistPdf("HH_AbsReal_%d" % MM, "", ROOT.RooArgSet(self._x), RHH)

    RHIM = ROOT.RooIntegralMorph("Hmorph_%d" % MM, "", RHHR, RHLR, self._x, rmass)
    self.xframe = self._x.frame(ROOT.RooFit.Title(";DiCluster Mass [GeV];Events/GeV"), ROOT.RooFit.Range(MM, 10000))
    RHI = RHIM.createHistogram("Hinterpo_%d" % MM, self._x)
    #if scaled: RHI.Scale(integralInterpo(self._massArr, self._histInts, MM)/RHI.Integral())
    return RHI.Clone(N), inxhists


#Determine if we already have xmass or phi mass
interpoBool = True
have_x = False
have_phi = False

if(in_x in xmasses): have_x = True
if(in_phi in phimasses): have_phi=True
if(have_x and have_phi): interpoBool=False

savehists = []
nxbins = 700

def CallInterpOnPhi(my_x):
    global dists, nxbins

    INPUTH = []
    INPUTM = []

    for xphi,F in dists.items():
      this_xm = xphi[1:xphi.find("A")]
      if(str(my_x)==this_xm):   #Doing 1D for now, only get matching x mass
        this_phim = float(xphi[xphi.find("A")+1 :].replace("p","."))
        Chain=ROOT.TChain("pico_nom")
        Chain.Add(F)
        rdf = ROOT.RDataFrame.RDataFrame(Chain)
        cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70"
        rdf = rdf.Filter(cutString)
        rdf = rdf.Filter("XM > {}".format(float(this_xm)*0.85))
        xhist = rdf.Histo1D(("xhist_{}_{}".format(this_xm, this_phim),"xmass", nxbins, 0, int(this_xm)*2), "XM")

        INPUTH.append(xhist.GetValue().Clone())
        INPUTM.append(this_phim)

    print(INPUTM)
    mp = HC(INPUTH, INPUTM)
    E, xhists = mp.morph(in_phi, "newhist")
    return E, xhists


if interpoBool: 
  savehists = []

  print("Unknown X and phi mass. interpolating twice")
  lowx, hix = computeBoundingIndices(in_x, xmasses)

  t_Es = []
  INPUTM = []
  
  for DOX in [xmasses[lowx], xmasses[hix]]:
    t_Es.append(CallInterpOnPhi(DOX)[0])
    INPUTM.append(DOX)

  for (hh,mm) in zip(t_Es, INPUTM):
    hh.SetName("{}".format(mm))
    savehists.append(hh)

  print(INPUTM)
  mp = HC(t_Es, INPUTM)
  E, newxhists = mp.morph(in_x, "newhist")

  myout = ROOT.TFile(outFileName, "RECREATE")
  myout.cd()
  E.SetName("X{}phi{}".format(in_x, in_phi))
  E.SetTitle("X {} #phi {} Interpolated Signal".format(in_x, in_phi))
  E.Write()

else: 
  print("Known Signal. Getting X Mass")
  for xphi,F in dists.items():
    this_xm = xphi[1 : xphi.find("A")]
    this_phim = xphi[xphi.find("A")+1 :].replace("p",".")
    if(str(in_x) == this_xm and str(in_phi)==this_phim):   #Doing 1D for now, only get matching x mass
      Chain=ROOT.TChain("pico_nom")
      Chain.Add(F)
      rdf = ROOT.RDataFrame.RDataFrame(Chain)
      cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70"
      rdf = rdf.Filter(cutString)
      rdf = rdf.Filter("XM > {}".format(in_x*0.85))
      #xhist = rdf.Histo1D(("xhist","xmass", nxbins, 0, in_x*2), "XM")
      xhist = rdf.Histo1D(("xhist","xmass", nxbins, 0, 1400), "XM")

  myout = ROOT.TFile(outFileName, "RECREATE")
  myout.cd()
  xhist.SetName("X{}phi{}".format(in_x, in_phi))
  xhist.SetTitle("X {} #phi {} Known Signal".format(in_x, in_phi))
  xhist.Write()

print("Saving file: {}".format(outFileName))

for hh in savehists:
  hh.Write()
myout.Write()
myout.Save()
myout.Close()
