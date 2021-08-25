import ROOT
import numpy
import os
import math
import sys
sys.path.append('/users/h2/th544/CMSSW_11_0_0_pre2/src/PairedPairs2D/data_analysis/')
import PlottingPayload as PL

ROOT.gROOT.SetBatch()

### script to make 1 GeV binned signal for the DijetRootTreeAnalyzer code by Dimitris and Ilias ###

dists = {}
dists["Diquark_chi500suu2000"] = "/cms/xaastorage-2/PicoTrees/4JETS/2016/v6/Diquark_S2000_chi500_2016.root"
dists["Diquark_chi500suu3000"] = "/cms/xaastorage-2/PicoTrees/4JETS/2016/v6/Diquark_S3000_chi500_2016.root"
dists["Diquark_chi1000suu4000"] = "/cms/xaastorage-2/PicoTrees/4JETS/2016/v6/Diquark_S4000_chi1000_2016.root"
dists["Diquark_chi1000suu5000"] = "/cms/xaastorage-2/PicoTrees/4JETS/2016/v6/Diquark_S5000_chi1000_2016.root"
dists["Diquark_chi1800suu8000"] = "/cms/evah/workspace/CMSSW_10_2_2/src/nanoTREE/trees/2017/Diquark_chi1800suu8000/tree_Diquark_chi1800suu8000.root"
dists["Diquark_chi2000suu8400"] = "/cms/xaastorage-2/PicoTrees/4JETS/2016/v6/Diquark_S8400_chi2000_2016.root"
dists["Diquark_chi2100suu9000"] = "/cms/xaastorage-2/PicoTrees/4JETS/2016/v6/Diquark_S9000_chi2100_2016.root"
dists["Diquark_chi3000suu8000"] = "/cms/xaastorage-2/PicoTrees/4JETS/2016/v6/Diquark_S8000_chi3000_2016.root"
dists["Xaa_X2000a500"] = "/home/th544/CMSSW_10_2_2/src/picotreeMaker/trees/2016/Xaa_x2000a500/Xaa_x2000a500_2016_DR.root"

dists["rpv_M500"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M500_all.root"
dists["rpv_M600"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M600_all.root"
dists["rpv_M700"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M700_all.root"
dists["rpv_M800"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M800_all.root"
dists["rpv_M900"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M900_all.root"
dists["rpv_M1000"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M1000_all.root"
dists["rpv_M1250"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M1250_all.root"
dists["rpv_M1500"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M1500_all.root"
dists["rpv_M1750"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M1750_all.root"
dists["rpv_M2000"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M2000_all.root"
dists["rpv_M2500"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M2500_all.root"
dists["rpv_M3000"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v7/Athens/RPV_M3000_all.root"

bins = [1., 3., 6., 10., 16., 23., 31., 40., 50., 61., 74., 88., 103., 119., 137., 156., 176., 197., 220., 244., 270., 296., 325., 354., 386., 419., 453., 489., 526., 565., 606., 649., 693., 740., 788., 838., 890., 944., 1000., 1058., 1118., 1181., 1246., 1313., 1383., 1455., 1530., 1607., 1687., 1770., 1856., 1945., 2037., 2132., 2231., 2332., 2438., 2546., 2659., 2775., 2895., 3019., 3147., 3279., 3416., 3558., 3704., 3854., 4010., 4171., 4337., 4509., 4686., 4869., 5058., 5253., 5455., 5663., 5877., 6099., 6328., 6564., 6808., 7060., 7320., 7589., 7866., 8152., 8447., 8752., 9067., 9391., 9726., 10072., 10430., 10798., 11179., 11571., 11977., 12395., 12827., 13272., 13732., 14000.]
unibins = {}
unibins[0] = PL.MakeNBinsFromMinToMax(1812, 419., 2231.)
unibins[1] = PL.MakeNBinsFromMinToMax(1666, 565., 2231.)
unibins[2] = PL.MakeNBinsFromMinToMax(1625, 606., 2231.)
unibins[3] = PL.MakeNBinsFromMinToMax(1625, 606., 2231.)
unibins["full"] = PL.MakeNBinsFromMinToMax(13999, 1., 14000.)

LUMI = {}
LUMI["2016"] = [35900, 1.05]
LUMI["2017"] = [41500, 1.025]
LUMI["2018"] = [59700, 1.025]
LUMI["II"] = [137500, 1.]
ALPHA = [["Slice 1", 0.15, 0.25], ["Slice 2", 0.25, 0.35], ["Slice 3", 0.35, 0.5]]

def computeBoundingIndices(M, anchors):
    lowI, hiI = 0, 0
    if M in anchors:
        for n in range(len(anchors)-2):
            if anchors[n] < M and anchors[n+2] > M: lowI, hiI = n, n+2
    else:
        for n in range(len(anchors)-1):
            if anchors[n] < M and anchors[n+1] > M: lowI, hiI = n, n+1
    return lowI, hiI

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
    def __init__(self, histArr, massArr, alph):
        self._massArr  = massArr
        self._histArr = histArr
        self._x  = ROOT.RooRealVar("x","x",histArr[0].GetXaxis().GetXmin(),histArr[0].GetXaxis().GetXmax())
        self._x.setBins(histArr[0].GetNbinsX())
        self._histInts = [h.Integral() for h in histArr]

    def morph(self, M, sl, normalize=True):
        self._lowI, self._hiI = computeBoundingIndices(M, self._massArr)

        HL = self._histArr[self._lowI].Clone("tempL_%d_%d" % (M, sl))
        HH = self._histArr[self._hiI].Clone("tempH_%d_%d" % (M, sl))
        
        alpha = (M - self._massArr[self._lowI])/(self._massArr[self._hiI] - self._massArr[self._lowI])
        rmass = ROOT.RooRealVar("rm_%d" % sl, "rmass", alpha, 0., 1.)

        RHL = ROOT.RooDataHist("HL_%d" % sl, ";Average Dijet Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HL)
        RHLR = ROOT.RooHistPdf("HL_AbsReal_%d" % sl, "", ROOT.RooArgSet(self._x), RHL)
        RHH = ROOT.RooDataHist("HH_%d" % sl, ";Average Dijet Mass [GeV];Events/GeV", ROOT.RooArgList(self._x), HH)
        RHHR = ROOT.RooHistPdf("HH_AbsReal_%d" % sl, "", ROOT.RooArgSet(self._x), RHH)
        
        RHIM = ROOT.RooIntegralMorph("Hmorph_%d" % sl, "", RHHR, RHLR, self._x, rmass)
        self.xframe = self._x.frame(ROOT.RooFit.Title(";Average Dijet Mass [GeV];Events/GeV"), ROOT.RooFit.Range(400, 2000))
        RHI = RHIM.createHistogram("Hinterpo_%d" % sl, self._x)
        if normalize: RHI.Scale(integralInterpo(self._massArr, self._histInts, M)/RHI.Integral())
        return RHI

def signalmaker(o):
    INPUTM = [500,600,700,800,900,1000,1250,1500,1750,2000,2500,3000]
    STEPARR = []
    if o.massrange != None:
        MIN, MAX, STEP = o.massrange
        STEPARR = range(MIN, MAX + STEP, STEP) 
    else: STEPARR = o.mass
    
    for m in STEPARR:
        sw_nom = "1."
        TREES = ["nominal", "jer_up", "jer_down", "jesCorr_up", "jesCorr_down"] if o.TREE is None else [str(o.TREE)]
        ALPHS = ALPHA if o.ALPH is None else [ALPHA[int(o.ALPH)]]
        print("\n#=======================#")
        print("||      RPV M%d      ||" % int(m))
        print("#=======================#\n")
        
        if m in INPUTM:
            for sl in range(len(ALPHS)):
                cuts = "evt_Masym < 0.1 && evt_Deta < 1.1 && dj1_dR < 2.0 && dj2_dR < 2.0 " + ("" if o.NOFJ else "&& evt_4JetM > 1607. ") + " && evt_alpha >= " + str(ALPHA[sl][1]) + "&& evt_alpha < " + str(ALPHA[sl][2])
                print("|===> Working on: slice %d for rpv_M%d" % (sl+1, int(m)))
                for tree in TREES:
                    print("|===> tree_%s" % tree)
                    D = PL.GetM2jA(dists["rpv_M%d" % int(m)], "tree_" + tree, "h_AveDijetMass_1GeV", sw_nom, cuts, BIN=bins if o.varbins else unibins["full"], divbin=False)
                    F = ROOT.TFile("/users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M%d_%s_asl%d" % (int(m), tree, sl) + ("_no4J" if o.NOFJ else "") + ".root", "recreate")
                    if o.norm: D.Scale(1./D.Integral())
                    F.cd()
                    D.Write()
                    F.Close()
        else:
            for sl in range(len(ALPHS)):
                cuts = "evt_Masym < 0.1 && evt_Deta < 1.1 && dj1_dR < 2.0 && dj2_dR < 2.0 " + ("" if o.NOFJ else "&& evt_4JetM > 1607. ") + " && evt_alpha >= " + str(ALPHA[sl][1]) + "&& evt_alpha < " + str(ALPHA[sl][2])
                print("|===> Working on: slice %d for rpv_M%d" % (sl+1, int(m)))
                print("|===> Interpolating...")
                for tree in TREES:
                    print("|===> tree_%s" % tree)
                    F = ROOT.TFile("/users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M%d_%s_asl%d" % (int(m), tree, sl) + ("_no4J" if o.NOFJ else "") + ".root", "recreate")
                    INPUTH = [PL.GetM2jA(dists["rpv_M%d" % INPUTM[j]], "tree_" + tree, "RPVH_%d_%d" % (INPUTM[j], sl), sw_nom, cuts, BIN=unibins["full"]) for j in range(len(INPUTM))]
                    mp = HC(INPUTH, INPUTM, ALPHA)
                    D = mp.morph(m, sl)
                    D.SetName("h_AveDijetMass_1GeV")
                    D.SetStats(0)
                    if o.norm: D.Scale(1./D.Integral())
                    F.cd()
                    D.Write()
                    F.Close()

if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()
    
    mass_parse = parser.add_mutually_exclusive_group(required=True)
    mass_parse.add_argument("--mass", type=int, nargs = '*', default = 1000, help="Mass can be specified as a single value or a whitespace separated list (default: %(default)s)" )
    mass_parse.add_argument("--massrange", type=int, nargs = 3, help="Define a range of masses to be produced. Format: min max step", metavar = ('MIN', 'MAX', 'STEP') )
    
    parser.add_argument("-a", type=int, dest="ALPH", default=None, help="alpha slice")
    parser.add_argument("-t", type=str, dest="TREE", default=None, help="tree_nominal, JES, or JER subtrees")
    parser.add_argument("--varbins", action="store_true", dest="varbins", help="binning in variable bins?")
    parser.add_argument("--normalize", action="store_true", dest="norm", help="normalized to unity?")
    parser.add_argument("--no4J", action="store_true", dest="NOFJ", help="remove four-jet mass cut and advance fit start")
    args = parser.parse_args()
    
    signalmaker(args)