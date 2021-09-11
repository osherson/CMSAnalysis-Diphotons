import ROOT
import numpy
import os
import math
import sys
sys.path.append('/users/h2/th544/CMSSW_11_0_0_pre2/src/PairedPairs2D/data_analysis/')
import PlottingPayload as PL

### PICOTREE DIRECTORIES ###

dists = {}
dists["QCD_2016"] = "/cms/xaastorage-2/PicoTrees/4JETS/2016/v6_v0/QCD_HT_all_2016.root"
dists["QCD_2017"] = "/cms/xaastorage-2/PicoTrees/4JETS/2017/v6/QCD_HT_all_2017.root"
dists["QCD_2018"] = "/cms/xaastorage-2/PicoTrees/4JETS/2018/v6/QCD_HT_all_2018.root"
dists["data_2016"] = "/cms/xaastorage-2/PicoTrees/4JETS/2016/v6/Athens/data_JetHT_Run2016_all_2016.root"
dists["data_2017"] = "/cms/xaastorage-2/PicoTrees/4JETS/2017/v6/Athens/data_JetHT_Run2017_all_2017.root"
dists["data_2018"] = "/cms/xaastorage-2/PicoTrees/4JETS/2018/v6/Athens/data_JetHT_Run2018_all_2018.root"
dists["data_II"] = "/cms/xaastorage-2/PicoTrees/4JETS/AllYears/v6/Athens/data_JetHT_Run2_all.root"

bins = [1., 3., 6., 10., 16., 23., 31., 40., 50., 61., 74., 88., 103., 119., 137., 156., 176., 197., 220., 244., 270., 296., 325., 354., 386., 419., 453., 489., 526., 565., 606., 649., 693., 740., 788., 838., 890., 944., 1000., 1058., 1118., 1181., 1246., 1313., 1383., 1455., 1530., 1607., 1687., 1770., 1856., 1945., 2037., 2132., 2231., 2332., 2438., 2546., 2659., 2775., 2895., 3019., 3147., 3279., 3416., 3558., 3704., 3854., 4010., 4171., 4337., 4509., 4686., 4869., 5058., 5253., 5455., 5663., 5877., 6099., 6328., 6564., 6808., 7060., 7320., 7589., 7866., 8152., 8447., 8752., 9067., 9391., 9726., 10072., 10430., 10798., 11179., 11571., 11977., 12395., 12827., 13272., 13732., 14000.]

ALPHA = [["Slice 1", 0.15, 0.25], ["Slice 2", 0.25,  0.35], ["Slice 3", 0.35, 0.5]]

def bkgmaker(o):
    unibins = {}
    if o.NOFJ: 
        unibins[0] = PL.MakeNBinsFromMinToMax(3656, 354., 4010.)
        unibins[1] = PL.MakeNBinsFromMinToMax(3484, 526., 4010.)
        unibins[2] = PL.MakeNBinsFromMinToMax(3404, 606., 4010.)
    else:
        unibins[0] = PL.MakeNBinsFromMinToMax(3591, 419., 4010.)
        unibins[1] = PL.MakeNBinsFromMinToMax(3445, 565., 4010.)
        unibins[2] = PL.MakeNBinsFromMinToMax(3404, 606., 4010.)

    ALPHS = ALPHA if o.ALPH is None else [ALPHA[int(o.ALPH)]]
    for sl in range(len(ALPHS)):
        year = str(o.YEAR)
        print("|===> Working on year %s, slice %d" % (year, (sl if o.ALPH is None else o.ALPH)+1))
        cuts = "evt_Masym < 0.1 && evt_Deta < 1.1 && dj1_dR < 2.0 && dj2_dR < 2.0 " + ("" if o.NOFJ else "&& evt_4JetM > 1607. ") + "&& evt_alpha >= " + str(ALPHA[sl if o.ALPH is None else o.ALPH][1]) + "&& evt_alpha < " + str(ALPHA[sl if o.ALPH is None else o.ALPH][2])
        D = PL.GetM2jA(dists["data_%s" % year], "tree_nominal", "h_AveDijetMass_1GeV", "1", cuts, BIN=bins if o.varbins else unibins[sl], divbin=False)
        F = ROOT.TFile("inputs/PFJetHT_Run%s_asl%d" % (year, sl if o.ALPH is None else o.ALPH) + ("_no4J" if o.NOFJ else "") + ".root", "recreate")
        F.cd()
        D.Write()
        F.Close()
        
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-y", dest="YEAR", help="Dataset to run on. Acceptable arguments are '2016', '2017', '2018', and 'II' for full Run II.")
    parser.add_option("-a", type=int, dest="ALPH", default=None, help="Index of alpha slice. By default runs all alpha slices.")
    #parser.add_option("-t", type=str, dest="TREE", default=None, help="tree_nominal, JES, or JER subtrees")
    parser.add_option("--varbins", action="store_true", dest="varbins", help="Binning in variable bins?")
    parser.add_option("--no4J", action="store_true", dest="NOFJ", help="Remove four-jet cut and advance fit start")
    (o, args) = parser.parse_args()
    bkgmaker(o)
