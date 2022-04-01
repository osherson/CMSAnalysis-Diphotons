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

MAX_XM = 2000
MAX_ALPHA = 0.05
nxbins = MAX_XM / 2

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
    #self._x  = ROOT.RooRealVar("x","x",0.,0.1)
    self._x.setBins(histArr[0].GetNbinsX())
    self._histInts = [h.Integral() for h in histArr]
    self._inxhists = []
    self._cutEff = []

  def morph(self, MM, var, nameM, N, scaled=False):
    #scaled=True
    self._lowI, self._hiI = computeBoundingIndices(MM, self._massArr)
    print(self._massArr[self._lowI], self._massArr[self._hiI])

    if var == "XM":
      HL = self._histArr[self._lowI].Clone(self._histArr[self._lowI].GetName() + "HL")
      HH = self._histArr[self._hiI].Clone(self._histArr[self._hiI].GetName() + "HH")

    elif var == "alpha":
      HH = self._histArr[self._lowI].Clone(self._histArr[self._lowI].GetName() + "HL")
      HL = self._histArr[self._hiI].Clone(self._histArr[self._hiI].GetName() + "HH")

    inxhists = [HL, HH]
    un = nameM

    ##
    c1 = ROOT.TCanvas()
    c1.cd()
    ll = ROOT.TLegend(0.6,0.5,0.8,0.75)
    ll.SetBorderSize(0)
    HL.SetLineColor(ROOT.kGreen)
    HL.SetTitle("HL")
    HL.Draw("hist")
    HH.SetTitle("HH")
    HH.SetLineColor(ROOT.kRed)
    HH.Draw("histsame")

    ll.AddEntry(HL, "HL")
    ll.AddEntry(HH, "HL")
    ##

    print("Bounding Masses: {} - {}".format(self._massArr[self._lowI], self._massArr[self._hiI]))

    if var == "XM": 
      alpha = (float(MM) - float(self._massArr[self._lowI]))/(float(self._massArr[self._hiI]) - float(self._massArr[self._lowI]))
      rmass = ROOT.RooRealVar("rm_{}".format(un), "rmass", alpha, 0., 1.)
    elif var == "alpha": 
      rmass = ROOT.RooRealVar("rm_{}".format(un), "rmass", 0.5, 0., 1.)

    RHL = ROOT.RooDataHist("HL_".format(un), ";DiCluster Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HL)
    RHLR = ROOT.RooHistPdf("HL_AbsReal_{}".format(un), "", ROOT.RooArgSet(self._x), RHL)
    RHH = ROOT.RooDataHist("HH_{}".format(un), ";DiCluster Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HH)
    RHHR = ROOT.RooHistPdf("HH_AbsReal_{}".format(un), "", ROOT.RooArgSet(self._x), RHH)

    RHIM = ROOT.RooIntegralMorph("Hmorph_{}".format(un), "", RHHR, RHLR, self._x, rmass)
    #self.xframe = self._x.frame(ROOT.RooFit.Title(";DiCluster Mass [GeV];Events/GeV"), ROOT.RooFit.Range(0, 10000))
    self.xframe = self._x.frame(ROOT.RooFit.Title(";DiCluster Mass [GeV];Events/GeV"), ROOT.RooFit.Range(0, 0.1))
    RHI = RHIM.createHistogram("Hinterpo_{}".format(un), self._x)
    #if scaled: RHI.Scale(integralInterpo(self._massArr, self._histInts, MM)/RHI.Integral())


    ##
    rr = RHI.Clone(un+N)
    rr.SetTitle("OUT")
    rr.SetLineColor(ROOT.kBlack)
    rr.Draw("histsame")
    ll.AddEntry(rr, "OUT")
    ll.Draw("same")
    c1.Print("tc3.png")
    ##

    return RHI.Clone(un+N), inxhists

def getAlphaHists(xtreename, xs, alpha, dists, var):
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
        cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70"
        rdf = rdf.Filter(cutString)
        hist = rdf.Histo1D( ("alpha","alpha",4000,0,4000), "alpha")
        alphastd = hist.GetStdDev()
        #rdf = rdf.Filter("alpha > {} && alpha < {}".format(alpha - alphastd*3, alpha + alphastd*3), "alpha Window")
        rdf = rdf.Filter("alpha > 0 && alpha < {}".format(MAX_ALPHA), "alpha Window")
        num = float(rdf.Count().GetValue())
        rdf = rdf.Filter("XM > {} && XM < 2000".format(float(xm)*0.85))

        #xhist = rdf.Histo1D(("xhist_{}_{}".format(xm, phim),"xmass", nxbins, 0, max(int(xm)*2, MAX_XM)), "XM")
        if(var=="XM"): max_x = max(int(xm)*2, MAX_XM)
        elif(var=="alpha"): max_x = max(int(alpha)*2, MAX_ALPHA)

        myhist = rdf.Histo1D(("{}_{}_{}".format(var, xm, dphi),var, nxbins, 0, max_x ), var)

        effs.append(num / getDenom(int(xm), float(phim)))
        denoms.append(getDenom(int(xm), float(phim)))
        histos.append(myhist.GetValue().Clone())
        del Chain, rdf

  return histos, effs, denoms

def getPhiHists(xtreename, xm, alpha, alphas, dists, var):
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
        cutString = "masym < 0.25 && clu1_dipho > 0.9 && clu2_dipho > 0.9 && clu1_iso > 0.8 && clu2_iso > 0.8 && clu1_pt > 70 && clu2_pt > 70"
        rdf = rdf.Filter(cutString)
        hist = rdf.Histo1D( ("alpha","alpha",4000,0,4000), "alpha")
        alphastd = hist.GetStdDev()
        #rdf = rdf.Filter("alpha > {} && alpha < {}".format(t_alpha - alphastd*3, t_alpha + alphastd*3), "alpha Window")
        rdf = rdf.Filter("alpha > 0 && alpha < {}".format(MAX_ALPHA), "alpha Window")
        num = float(rdf.Count().GetValue())
        rdf = rdf.Filter("XM > {} && XM < 2000".format(float(xm)*0.85))

        if(var=="XM"): max_x = max(int(xm)*2, MAX_XM)
        elif(var=="alpha"): max_x = max(int(alpha)*2, MAX_ALPHA)

        myhist = rdf.Histo1D(("{}_{}_{}".format(var, xm, dphi),var, nxbins, 0, max_x ), var)
        effs.append(num / getDenom(int(xm), float(dphi)))
        denoms.append(getDenom(int(xm), float(dphi)))
        histos.append(myhist.GetValue().Clone())
        del Chain, rdf

  return gphis, histos, effs, denoms


def InterpolateHists(input_x, input_phi, var, xtreename, masslist, lm, him, usehists, usemasses, useeffs, denoms):

      h1,h2 = usehists[0], usehists[1]
      h1.Scale(1/h1.Integral())
      h2.Scale(1/h2.Integral())
      h1.Sumw2()
      h2.Sumw2()
      scalehists=[h1, h2]

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

      E, newxhists = mp.morph(input_x, var, "{}_{}_{}_{}".format(input_x, input_phi, xtreename, var), "newhist_{}_{}_{}_{}".format(input_x, input_phi, xtreename, var), input_x)
      #E.SetName("X{}phi{}_normed".format(input_x, input_phi))
      E.SetTitle("{}, X {} #phi {} Interpolated Signal".format(var, input_x, input_phi))
      E.Sumw2()
      ##
      #E.Scale(neweff * LUMI[year] * XS)
      E.Scale(neweff * newNevt)
      E.SetName("X{}phi{}_{}".format(input_x, input_phi, var))
      ##
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
  

  ### PICOTREE DIRECTORIES ###
  pico_dir = "/cms/xaastorage-2/DiPhotonsTrees/"
  dists = {}
  xmasses = []
  phimasses = []
  alphas = []
  ##


  nud = xtreename[xtreename.find("_")+1 :]
  outFileName = "../inputs/Interpolations/{}/X{}phi{}_{}.root".format(year,in_x,in_phi,nud)

  ###

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

  xphipairs = [] 
  for (xx,pp) in zip(xmasses,phimasses):
    if (pp.is_integer()): pp = str(int(pp))
    else: pp = str(pp).replace(".","p")
    xphipairs.append("X{}A{}".format(xx,pp))

  if(in_x in xmasses): have_x = True
  if(in_phi in phimasses): have_phi=True
  if(o.mass in xphipairs): interpoBool=False
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

    #ivars = ["XM"]
    #ivars = ["alpha"]
    ivars = ["XM", "alpha"]

    ##
    myout = ROOT.TFile(outFileName, "RECREATE")
    myout.cd()
    ##

    for ivar in ivars:

      print("\nGetting {} Shape for X {} Phi {} Signal".format(ivar, in_x, in_phi))

      if(have_alpha == True and not o.force): 
        print("Interpolating from known alpha signals")
        lowx, hix = computeBoundingIndices(in_x, xmasses)
        print(lowx, hix)

        INPUTM = [xmasses[lowx], xmasses[hix]]
        print(INPUTM)
        myhists, myeffs, mydenoms = getAlphaHists(xtreename, INPUTM, in_alpha, dists, ivar)
        use_masses = {}
        use_masses["X"] = xmasses
        finalshape, feff, fevt = InterpolateHists(in_x, in_phi, ivar, xtreename, use_masses, lowx, hix, myhists, INPUTM, myeffs, mydenoms)

      elif( (have_x and not have_alpha) or o.force ):
        if( o.force ): print("Forcing Interpolation for known signal")
        else: print("Known X, Unknown alpha. Interpolating from same X mass, nearest phi mass signals")

        lowa, hia = computeBoundingIndices(in_alpha, alphas)

        INPUTM = [alphas[lowa], alphas[hia]]
        myphis, myhists, myeffs, mydenoms = getPhiHists(xtreename, in_x, in_alpha, INPUTM, dists, ivar)
        use_masses = {}
        use_masses["phi"] = myphis
        finalshape, feff, fevt = InterpolateHists(in_x, in_phi, ivar, xtreename, use_masses, 0, 1, myhists, myphis, myeffs, mydenoms)

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
          myphis, myhists, myeffs, mydenoms = getPhiHists(xtreename, dox, in_alpha, INPUTM, dists, ivar)
          print(myphis)
          use_masses = {}
          use_masses["phi"] = myphis
          newhist, neweff, newdenom = InterpolateHists(dox, in_phi, ivar, xtreename, use_masses, 0, 1, myhists, myphis, myeffs, mydenoms)
          inx_alphahists.append(newhist)
          myeffs.append(neweff)
          mydenoms.append(newdenom)
        #myhists, myeffs, mydenoms = getAlphaHists(INPUTM, in_alpha, dists)

        use_masses = {}
        use_masses["X"] = xmasses
        finalshape, feff, fevt = InterpolateHists(in_x, in_phi, ivar, xtreename, use_masses, lowx, hix, inx_alphahists, bxs, myeffs, mydenoms)

      finalshape.Write()
    myout.Close()

  else: 
    print("Known Signal. Doing Nothing")
    return

  print("Saving file: {}".format(outFileName))

if __name__ == "__main__":
  from argparse import ArgumentParser
  parser = ArgumentParser()
  
  parser.add_argument("--year", required=True, default=2018, help='Run II Year' )
  parser.add_argument("--mass", required=True, default = "X623A17", help='X, Phi mass entered as X123A123' )
  parser.add_argument("--forceinterpo", action="store_true", dest="force", help="Force interpolation of intermediate mass points which are given.")

  args = parser.parse_args()

  interpoSignalMaker(args, "pico_nom")
  #interpoSignalMaker(args, "pico_scale_up")
  #interpoSignalMaker(args, "pico_scale_down")
