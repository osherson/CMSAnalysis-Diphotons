import ROOT
import numpy
import os
import math
import sys
import pandas
sys.path.append("../.")
#import PlottingPayload as PL

#ROOT.gROOT.SetBatch()

#year = '2018'
#in_xphi = "X600A5"

year = sys.argv[1]
in_xphi = sys.argv[2]

in_x = float(in_xphi[1 : in_xphi.find("A")])
in_phi = float(in_xphi[in_xphi.find("A")+1 :].replace("p","."))
if(in_x.is_integer()): in_x = int(in_x)
if(in_phi.is_integer()): in_phi = int(in_phi)

print("\nGetting Dicluster Mass Shape for X {} Phi {} Signal".format(in_x, in_phi))


### PICOTREE DIRECTORIES ###
pico_dir = "/cms/xaastorage-2/DiPhotonsTrees/"
dists = {}
xmasses = []
phimasses = []
##

outFileName = "OutFiles/{}/X{}phi{}.root".format(year,in_x,in_phi)

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

def linearInterpolate(x, x1, y1, x2, y2):
  return y1 + ( (x - x1) * (y2 - y1) ) / (x2 - x1)

def getCutEff(M, year, my_x, my_phis):
  
  ### Efficiency File ###
  infoFile = "SignalEffCalc/CutInfoFiles/cutInfo_{}cutInfo.csv".format(year)
  df = pandas.read_csv(infoFile,index_col=0)
  dic = df.to_dict()

  for idx, row in df.iterrows():
    if (row.xmass == my_x and row.phimass == my_phis[0]):
      x1, phi1, eff1 = row.xmass, row.phimass, row.eff
    elif (row.xmass == my_x and row.phimass == my_phis[1]):
      x2, phi2, eff2 = row.xmass, row.phimass, row.eff

  print("Initial signals Efficiencies: ")
  print("X {}, phi {} : {:.4f}".format(x1, phi1, eff1))
  print("X {}, phi {} : {:.4f}".format(x2, phi2, eff2))

  neweff = linearInterpolate(M, phi1, eff1, phi2, eff2)

  print("Intermediate Signal Efficiency: ")
  print("X {}, phi {} : {:.4f}".format(my_x, M, neweff))

  return neweff

class HC:
  def __init__(self, histArr, massArr):
    self._massArr = massArr
    self._histArr = histArr
    self._x  = ROOT.RooRealVar("x","x",histArr[0].GetXaxis().GetXmin(),histArr[0].GetXaxis().GetXmax())
    self._x.setBins(histArr[0].GetNbinsX())
    self._histInts = [h.Integral() for h in histArr]
    self._inxhists = []
    self._cutEff = []

  def morph(self, MM, N, year, scaled=False):
    #scaled=True
    self._lowI, self._hiI = computeBoundingIndices(MM, self._massArr)
    HL = self._histArr[self._lowI].Clone()
    HH = self._histArr[self._hiI].Clone()

    inxhists = [HL, HH]

    print("Bounding Masses: {} - {}".format(self._massArr[self._lowI], self._massArr[self._hiI]))
    #getCutEff(MM, year, use_x, [self._massArr[self._lowI], self._massArr[self._hiI]])

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
    global dists, nxbins, year

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

    #print(INPUTM)
    mp = HC(INPUTH, INPUTM)
    lowI, hiI = computeBoundingIndices(in_phi, INPUTM)
    new_eff = getCutEff(in_phi, year, my_x, [INPUTM[lowI], INPUTM[hiI]])
    E, xhists = mp.morph(in_phi, "newhist", year)
    print("\n")

    return E, new_eff


if interpoBool: 
  savehists = []

  print("Unknown X and phi mass. interpolating twice")
  lowx, hix = computeBoundingIndices(in_x, xmasses)

  t_Es = []
  INPUTM = []
  t_effs = []
  
  for DOX in [xmasses[lowx], xmasses[hix]]:
    t_E, t_eff = CallInterpOnPhi(DOX)
    t_Es.append(t_E)
    t_effs.append(t_eff)
    INPUTM.append(DOX)

  for (hh,mm) in zip(t_Es, INPUTM):
    hh.SetName("{}".format(mm))
    savehists.append(hh)

  #print(INPUTM)
  mp = HC(t_Es, INPUTM)
  x1,phi1,eff1 = xmasses[lowx], in_phi, t_effs[0]
  x2,phi2,eff2 = xmasses[hix], in_phi, t_effs[1]

  neweff = linearInterpolate(in_x, x1, eff1, x2, eff2) #This is the final efficiency for new signal
  x1,phi1,eff1 = xmasses[lowx], in_phi, t_effs[0]
  x2,phi2,eff2 = xmasses[hix], in_phi, t_effs[1]

  neweff = linearInterpolate(in_x, x1, eff1, x2, eff2) #This is the final efficiency for new signal
  E, newxhists = mp.morph(in_x, "newhist", year, in_x)

  print("Final Efficiency: ")
  print("X {}, phi {} : {:.4f}".format(in_x, in_phi, neweff))

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
