import ROOT
import numpy
import os
import math
import sys
import pandas
sys.path.append("../.")

LUMI = {}
LUMI["2016"] = 36.050
LUMI["2017"] = 39.670
LUMI["2018"] = 59.320

XS = 100 #fb^-1

maxvv = 2000
nxbins = maxvv

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

def getDenom(my_x, my_phi):
  """
  Get N Events Generated for a known signal
  """
  ### N Events File ###
  infoFile = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/Diphoton-Treemaker/HelperFiles/Signal_NEvents_{}.csv".format(year)
  xm, phim, nevt = numpy.loadtxt(infoFile, delimiter=',', skiprows=1, unpack=True)
  for (x,p,n) in zip(xm, phim, nevt):
    if (x == my_x and p == my_phi):
      return n

class HC:
  def __init__(self, histArr, massArr):
    self._massArr = massArr
    self._histArr = histArr
    self._x  = ROOT.RooRealVar("x","x",histArr[0].GetXaxis().GetXmin(),histArr[0].GetXaxis().GetXmax())
    #self._x  = ROOT.RooRealVar("x","x",800,1000)
    self._x.setBins(histArr[0].GetNbinsX())
    self._histInts = [h.Integral() for h in histArr]
    self._inxhists = []
    self._cutEff = []

  def morph(self, MM, nameM, N, scaled=False):
    #scaled=True
    self._lowI, self._hiI = computeBoundingIndices(MM, self._massArr)
    HL = self._histArr[self._lowI].Clone(self._histArr[self._lowI].GetName() + "HL")
    HH = self._histArr[self._hiI].Clone(self._histArr[self._hiI].GetName() + "HH")
    print(HL.GetXaxis().GetXmin(),HL.GetXaxis().GetXmax())

    inxhists = [HL, HH]
    un = nameM

    print("Bounding Masses: {} - {}".format(self._massArr[self._lowI], self._massArr[self._hiI]))

    alpha = (float(MM) - float(self._massArr[self._lowI]))/(float(self._massArr[self._hiI]) - float(self._massArr[self._lowI]))
    rmass = ROOT.RooRealVar("rm_{}".format(un), "rmass", alpha, 0., 1.)

    RHL = ROOT.RooDataHist("HL_".format(un), ";DiCluster Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HL)
    RHLR = ROOT.RooHistPdf("HL_AbsReal_{}".format(un), "", ROOT.RooArgSet(self._x), RHL)
    RHH = ROOT.RooDataHist("HH_{}".format(un), ";DiCluster Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HH)
    RHHR = ROOT.RooHistPdf("HH_AbsReal_{}".format(un), "", ROOT.RooArgSet(self._x), RHH)

    RHIM = ROOT.RooIntegralMorph("Hmorph_{}".format(un), "", RHHR, RHLR, self._x, rmass)
    #self.xframe = self._x.frame(ROOT.RooFit.Title(";DiCluster Mass [GeV];Events/GeV"), ROOT.RooFit.Range(MM, 10000))
    self.xframe = self._x.frame(ROOT.RooFit.Title(";DiCluster Mass [GeV];Events/GeV"), ROOT.RooFit.Range(0, 10000))
    RHI = RHIM.createHistogram("Hinterpo_{}".format(un), self._x)
    if scaled: RHI.Scale(integralInterpo(self._massArr, self._histInts, MM)/RHI.Integral())
    return RHI.Clone(un+N), inxhists

def getAlphaHists(xtreename, xs, alpha, dists):
  histos = []
  effs = []
  denoms = []

  for xm in xs:
    phim = xm*alpha
    for xphi,F in dists.items():
      dx = int(xphi[1:xphi.find("A")])
      dphi = float(xphi[xphi.find("A")+1 :].replace("p","."))
      if(dphi/dx == alpha and dx == xm):
        Chain=ROOT.TChain(xtreename)
        Chain.Add(F)
        rdf = ROOT.RDataFrame.RDataFrame(Chain)
        xhist_nocut = rdf.Histo1D(("xhist_{}_{}".format(xm, phim),"xmass", nxbins, 0, max(int(xm)*2, maxvv)), "XM")
        cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70"
        rdf = rdf.Filter(cutString)
        hist = rdf.Histo1D( ("alpha","alpha",4000,0,4000), "alpha")
        alphastd = hist.GetStdDev()
        rdf = rdf.Filter("alpha > {} && alpha < {}".format(alpha - alphastd*3, alpha + alphastd*3), "alpha Window")
        num = float(rdf.Count().GetValue())
        rdf = rdf.Filter("XM > {} && XM < 2000".format(float(xm)*0.85))
        xhist = rdf.Histo1D(("xhist_{}_{}".format(xm, phim),"xmass", nxbins, 0, max(int(xm)*2, maxvv)), "XM")
        effs.append(num / getDenom(int(xm), float(phim)))
        denoms.append(getDenom(int(xm), float(phim)))
        histos.append(xhist.GetValue().Clone())
        del Chain, rdf

  return histos, effs, denoms

def getPhiHists(xtreename, xm, alpha, alphas, dists):
  gphis = []
  histos = []
  effs = []
  denoms = []

  for t_alpha in alphas:
    for xphi,F in dists.items():
      dx = int(xphi[1:xphi.find("A")])
      if(dx != xm): continue
      dphi = float(xphi[xphi.find("A")+1 :].replace("p","."))
      dalpha = dphi / dx
      if(dalpha == t_alpha):
        print(xphi)
        gphis.append(dphi)
        Chain=ROOT.TChain(xtreename)
        Chain.Add(F)
        rdf = ROOT.RDataFrame.RDataFrame(Chain)
        xhist_nocut = rdf.Histo1D(("xhist_{}_{}".format(xm, dphi),"xmass", nxbins, 0, max(int(xm)*2, maxvv)), "XM")
        cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70"
        rdf = rdf.Filter(cutString)
        hist = rdf.Histo1D( ("alpha","alpha",4000,0,4000), "alpha")
        alphastd = hist.GetStdDev()
        rdf = rdf.Filter("alpha > {} && alpha < {}".format(t_alpha - alphastd*3, t_alpha + alphastd*3), "alpha Window")
        num = float(rdf.Count().GetValue())
        rdf = rdf.Filter("XM > {} && XM < 2000".format(float(xm)*0.85))
        xhist = rdf.Histo1D(("xhist_{}_{}".format(xm, dphi),"xmass", nxbins, 0, max(int(xm)*2, maxvv)), "XM")
        effs.append(num / getDenom(int(xm), float(dphi)))
        denoms.append(getDenom(int(xm), float(dphi)))
        histos.append(xhist.GetValue().Clone())
        del Chain, rdf

  return gphis, histos, effs, denoms


def InterpolateHists(input_x, input_phi, xtreename, masslist, lm, him, usehists, usemasses, useeffs, denoms, outFName):
      myout = ROOT.TFile(outFName, "UPDATE")
      myout.cd()
      for h in usehists:
        a = h.Clone(h.GetName()+"_original")
        a.Write()

      h1,h2 = usehists[0], usehists[1]
      h1.Scale(1/h1.Integral())
      h2.Scale(1/h2.Integral())
      h1.Sumw2()
      h2.Sumw2()
      scalehists=[h1, h2]
      for sh in scalehists:
        b = sh.Clone(sh.GetName()+"_scaledOne")
        b.Write()
      myout.Write()
      myout.Close()

      mp = HC(scalehists, usemasses)

      if(masslist.keys()[0]=='X'):
        x1,phi1,eff1,d1 = masslist['X'][lm], input_phi, useeffs[0], denoms[0]
        x2,phi2,eff2,d2 = masslist['X'][him], input_phi, useeffs[1], denoms[1]
        neweff = linearInterpolate(input_x, x1, eff1, x2, eff2) #This is the final efficiency for new signal
        newNevt = linearInterpolate(input_x, x1, d1, x2, d2) #This is the expected n events for new signal

      elif(masslist.keys()[0]=='phi'):
        x1,phi1,eff1,d1 = input_x, masslist['phi'][lm], useeffs[0], denoms[0]
        x2,phi2,eff2,d2 = input_x, masslist['phi'][him], useeffs[1], denoms[1]
        neweff = linearInterpolate(input_phi, phi1, eff1, phi2, eff2) #This is the final efficiency for new signal
        newNevt = linearInterpolate(input_phi, phi1, d1, phi2, d2) #This is the expected n events for new signal

      print("Final Efficiency: ")
      print("X {}, phi {} : {:.4f}".format(input_x, input_phi, neweff))

      E, newxhists = mp.morph(input_x, "{}_{}_{}".format(input_x, input_phi, xtreename), "newhist_{}_{}_{}".format(input_x, input_phi, xtreename), input_x)

      myout = ROOT.TFile(outFName, "UPDATE")
      myout.cd()
      E.SetName("X{}phi{}_normed".format(input_x, input_phi))
      E.SetTitle("X {} #phi {} Interpolated Signal".format(input_x, input_phi))
      E.Sumw2()
      E.Write()
      ##
      #E.Scale(neweff * LUMI[year] * XS)
      E.Scale(neweff * newNevt)
      E.SetName("X{}phi{}".format(input_x, input_phi))
      ##
      E.Write()
      myout.Write()
      myout.Close()
      return E, neweff, newNevt

def interpoSignalMaker(o, xtreename):

  global year
  year = o.year
  in_xphi = o.mass
  in_x = float(in_xphi[1 : in_xphi.find("A")])
  in_phi = float(in_xphi[in_xphi.find("A")+1 :].replace("p","."))
  in_alpha = in_phi / in_x
  if(in_x.is_integer()): in_x = int(in_x)
  if(in_phi.is_integer()): in_phi = int(in_phi)

  nom_updown = xtreename[xtreename.find("_")+1 :]
  
  print("\nGetting Dicluster Mass Shape for X {} Phi {} Signal".format(in_x, in_phi))

  ### PICOTREE DIRECTORIES ###
  pico_dir = "/cms/xaastorage-2/DiPhotonsTrees/"
  dists = {}
  xmasses = []
  phimasses = []
  alphas = []
  ##

  outFileName = "../inputs/Interpolations/{}/X{}phi{}_{}.root".format(year,in_x,in_phi,nom_updown)

  for path, subdirs, files in os.walk(pico_dir):
    for name in files:
      File = os.path.join(path, name)
      if name[0]=="X" and year in name:
        xamass = name[:name.find("_")]
        xmass = int(xamass[1 : xamass.find("A")])
        phimass = float(xamass[xamass.find("A")+1 :].replace("p",".") )
  
        if (File.endswith(".root") and year in name and "v_" not in File):
          if(os.path.getsize(File) > 100):
              dists[xamass]=File
              xmasses.append(xmass)
              phimasses.append(phimass)
              alphas.append(phimass / xmass)

  #Determine if we already have xmass or phi mass
  interpoBool = True
  have_x = False
  have_phi = False
  have_alpha = False

  if(in_x in xmasses): have_x = True
  if(in_phi in phimasses): have_phi=True
  if(have_x and have_phi): interpoBool=False
  if(in_alpha in alphas): have_alpha = True
  if o.force : interpoBool=True

  ###
  if(in_x < min(xmasses) or in_x > max(xmasses)): 
    print("Input X = {} GeV out of X mass range. Doing nothing".format(in_x))
    return
  elif(in_alpha < min(alphas) or in_alpha > max(alphas)): 
    print("Input alpha={} out of alpha mass range. Doing nothing".format(in_alpha))
    return
  ###

  if interpoBool: 
    myout = ROOT.TFile(outFileName, "RECREATE")
    myout.Close()

    if(have_alpha == True and not o.force): 
      print("Interpolating from known alpha signals")
      lowx, hix = computeBoundingIndices(in_x, xmasses)

      INPUTM = [xmasses[lowx], xmasses[hix]]
      myhists, myeffs, mydenoms = getAlphaHists(xtreename, INPUTM, in_alpha, dists)
      use_masses = {}
      use_masses["X"] = xmasses
      InterpolateHists(in_x, in_phi, xtreename, use_masses, lowx, hix, myhists, INPUTM, myeffs, mydenoms, outFileName)

    elif( (have_x and not have_alpha) or o.force ):
      if( o.force ): print("Forcing Interpolation for known signal")
      else: print("Known X, Unknown alpha. Interpolating from same X mass, nearest phi mass signals")

      lowa, hia = computeBoundingIndices(in_alpha, alphas)

      INPUTM = [alphas[lowa], alphas[hia]]
      myphis, myhists, myeffs, mydenoms = getPhiHists(xtreename, in_x, in_alpha, INPUTM, dists)
      use_masses = {}
      use_masses["phi"] = myphis
      InterpolateHists(in_x, in_phi, xtreename, use_masses, 0, 1, myhists, myphis, myeffs, mydenoms, outFileName)

    else:
      print("Unknown X and phi mass. Interpolating twice")
      lowx, hix = computeBoundingIndices(in_x, xmasses) 
      bxs = [xmasses[lowx], xmasses[hix]]
      
      inx_alphahists = []
      myeffs = []
      mydenoms = []
      for dox in bxs:
        lowa, hia = computeBoundingIndices(in_alpha, alphas)

        INPUTM = [alphas[lowa], alphas[hia]]
        myphis, myhists, myeffs, mydenoms = getPhiHists(xtreename, dox, in_alpha, INPUTM, dists)
        print(myphis)
        use_masses = {}
        use_masses["phi"] = myphis
        newhist, neweff, newdenom = InterpolateHists(dox, in_phi, xtreename, use_masses, 0, 1, myhists, myphis, myeffs, mydenoms, outFileName)
        inx_alphahists.append(newhist)
        myeffs.append(neweff)
        mydenoms.append(newdenom)
      #myhists, myeffs, mydenoms = getAlphaHists(INPUTM, in_alpha, dists)

      use_masses = {}
      use_masses["X"] = xmasses
      InterpolateHists(in_x, in_phi, xtreename, use_masses, lowx, hix, inx_alphahists, bxs, myeffs, mydenoms, outFileName)


  else: 
    print("Known Signal. Getting X Mass")
    outFileName = outFileName.replace(".root","_known.root")
    for xphi,F in dists.items():
      this_xm = xphi[1 : xphi.find("A")]
      this_phim = xphi[xphi.find("A")+1 :].replace("p",".")
      alpha = float(this_phim) / float(this_xm)
      if(str(in_x) == this_xm and str(in_phi)==this_phim):   #Doing 1D for now, only get matching x mass
        Chain=ROOT.TChain(xtreename)
        Chain.Add(F)
        rdf = ROOT.RDataFrame.RDataFrame(Chain)
        cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70"
        rdf = rdf.Filter(cutString, "Analysis Cuts")
        hist = rdf.Histo1D( ("alpha","alpha",4000,0,4000), "alpha")
        alphastd = hist.GetStdDev()
        rdf = rdf.Filter("alpha > {} && alpha < {}".format(alpha - alphastd*3, alpha + alphastd*3), "alpha Window")
        num = float(rdf.Count().GetValue())
        rdf = rdf.Filter("XM > {} && XM < 2000".format(float(this_xm)*0.85), "xmass cut")
        xhist = rdf.Histo1D(("xhist_{}_{}".format(this_xm, this_phim),"xmass", nxbins, 0, max(int(this_xm)*2, maxvv)), "XM")
        rep=rdf.Report()
        rep.Print()
        del Chain, rdf

    myout = ROOT.TFile(outFileName, "RECREATE")
    myout.cd()
    xhist.SetName("X{}phi{}".format(in_x, in_phi))
    xhist.SetTitle("X {} #phi {} Known Signal".format(in_x, in_phi))
    #xhist.Scale(1/xhist.Integral())
    xhist.Sumw2()
    eff = num / getDenom(int(this_xm), float(this_phim))
    xhist.Write()

  print("Saving file: {}".format(outFileName))

if __name__ == "__main__":
  from argparse import ArgumentParser
  parser = ArgumentParser()
  
  parser.add_argument("--year", required=True, default=2018, help='Run II Year' )
  parser.add_argument("--mass", required=True, default = "X623A17", help='X, Phi mass entered as X123A123' )
  parser.add_argument("--forceinterpo", action="store_true", dest="force", help="Force interpolation of intermediate mass points which are given.")

  args = parser.parse_args()

  interpoSignalMaker(args, "pico_nom")
  interpoSignalMaker(args, "pico_scale_up")
  interpoSignalMaker(args, "pico_scale_down")
