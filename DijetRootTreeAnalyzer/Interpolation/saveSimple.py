import ROOT
import numpy
import os
import math
import sys
sys.path.append("../.")
#import PlottingPayload as PL

ROOT.gROOT.SetBatch()

#year = '2018'
#in_xphi = "X600A5"

year = sys.argv[1]
in_xphi = sys.argv[2]

in_x = float(in_xphi[1 : in_xphi.find("A")])
in_phi = float(in_xphi[in_xphi.find("A")+1 :])
if(in_x.is_integer()): in_x = int(in_x)
if(in_phi.is_integer()): in_phi = int(in_phi)


### PICOTREE DIRECTORIES ###
pico_dir = "/cms/xaastorage-2/DiPhotonsTrees/"
dists = {}
xmasses = []
phimasses = []

for path, subdirs, files in os.walk(pico_dir):
  for name in files:
    File = os.path.join(path, name)
    if name[0]=="X" and year in name:
      xamass = name[:name.find("_")]
      xmass = int(xamass[1 : xamass.find("A")])
      phimass = float(xamass[xamass.find("A")+1 :].replace("p",".") )
  
      #if (xmass == 200 and File.endswith(".root") and amass/xmass < alpha_high and "v_" not in name):
      if (File.endswith(".root") and year in name and "v_" not in File):
        if(os.path.getsize(File) > 100):
            dists[xamass]=File
            xmasses.append(xmass)
            phimasses.append(phimass)

LUMI = {}
LUMI["2016"] = [35900, 1.05]
LUMI["2017"] = [41500, 1.025]
LUMI["2018"] = [59700, 1.025]
LUMI["II"] = [137500, 1.]

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

  def morph(self, MM, N, scaled=False):
    self._lowI, self._hiI = computeBoundingIndices(MM, self._massArr)
    HL = self._histArr[self._lowI].Clone("tempHL_%d" % MM)
    HH = self._histArr[self._hiI].Clone("tempHL_%d" % MM)

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
    if scaled: RHI.Scale(integralInterpo(self._massArr, self._histInts, MM)/RHI.Integral())
    return RHI.Clone(N)


#Determine if we already have xmass or phi mass
interpoBool = True
have_x = False
have_phi = False

if(in_x in xmasses): have_x = True
if(in_phi in phimasses): have_phi=True
if(have_x and have_phi): interpoBool=False

print("Have X: ", have_x)
print("Have_phi: ", have_phi)

savehists = []

def CallInterpOnPhi(my_x):
    global dists

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
        xhist = rdf.Histo1D(("xhist","xmass", 200, 0, int(this_xm)*2), "XM")

        INPUTH.append(xhist.GetValue().Clone())
        INPUTM.append(this_phim)

    print(INPUTM)
    mp = HC(INPUTH, INPUTM)
    E = mp.morph(in_phi, "newhist")
    return E

def CallInterpOnX(my_phi):
    global dists

    INPUTH = []
    INPUTM = []
    for xphi,F in dists.items():
      this_phim = xphi[xphi.find("A")+1 :]
      if(str(my_phi)==this_phim):   #Doing 1D for now, only get matching x mass
        this_xm = float(xphi[1:xphi.find("A")])
        Chain=ROOT.TChain("pico_nom")
        Chain.Add(F)
        rdf = ROOT.RDataFrame.RDataFrame(Chain)
        cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70"
        rdf = rdf.Filter(cutString)
        xhist = rdf.Histo1D(("xhist","xmass", 100, 0, in_x*2), "XM")

        INPUTH.append(xhist.GetValue().Clone())
        INPUTM.append(this_xm)

    print(INPUTM)
    mp = HC(INPUTH, INPUTM)
    E = mp.morph(in_x, "newhist")
    return E

if interpoBool: 

  if (have_x and not have_phi):
    print("Known X mass, interpolating phi mass")
    E = CallInterpOnPhi(in_x)

  elif(not have_x and have_phi): 
    print("Known phi mass, interpolating X mass")
    E = CallInterpOnX(in_phi)

  else: 
    print("Unknown X and phi mass. interpolating twice")
    lowx, hix = computeBoundingIndices(in_x, xmasses)
    
    for DOX in [xmasses[lowx], xmasses[hix]]:
      these_phis = []
      pairs = []
      print("Using M_X = {} Shapes".format(DOX))
      for xphi,F in dists.items():
        this_xm = xphi[1:xphi.find("A")]
        this_phim = xphi[xphi.find("A")+1 :]

        if(int(this_xm) == DOX):
          these_phis.append(float(this_phim.replace("p",".")))

      lowphi, hiphi = computeBoundingIndices(in_phi, these_phis)
      t_INPUTM = [these_phis[lowphi], these_phis[hiphi]]
      t_INPUTH = []
      for xphi,F in dists.items():
        this_xm = xphi[1:xphi.find("A")]
        this_phim = xphi[xphi.find("A")+1 :]
        if(int(this_xm) == DOX and float(this_phim.replace("p",".")) in t_INPUTM):
          Chain=ROOT.TChain("pico_nom")
          Chain.Add(F)
          rdf = ROOT.RDataFrame.RDataFrame(Chain)
          #cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70 "
          cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70 && XM > {}".format(float(DOX) * 0.8)
          rdf = rdf.Filter(cutString)
          xhist = rdf.Histo1D(("xhist","xmass", 100, 0, in_x*2), "XM")
          alphahist = rdf.Histo1D(("alphahist","alpha", 100, 0, in_phi / in_x * 2), "alpha")

          t_INPUTH.append(xhist.GetValue().Clone())

      print(t_INPUTM)
      t_mp = HC(t_INPUTH, t_INPUTM)
      t_E = t_mp.morph(in_phi, "newhist")
      INPUTM.append(DOX)
      INPUTH.append(t_E)

      for mm,hh in zip(t_INPUTM, t_INPUTH):
        hh.SetName("X{}_phi{}".format(DOX,mm))
        savehists.append(hh)
      t_E.SetName("X{}_{}_int".format(DOX, in_phi))
      savehists.append(t_E)

    print(INPUTM)
    mp = HC(INPUTH, INPUTM)
    E = mp.morph(in_x, "newhist")

  myout = ROOT.TFile("tempout.root", "RECREATE")
  myout.cd()
  E.Write()

else: print("We have that signal. Not doing anything")

for hh in savehists:
  hh.Write()
myout.Write()
myout.Save()
myout.Close()
