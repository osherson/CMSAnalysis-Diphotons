import os
import ROOT
import numpy

def computeBoundingIndices(M, anchors):
    lowI, hiI = 0, 0
    if M in anchors:
        for n in range(len(anchors)-2):
            if anchors[n] < M and anchors[n+2] > M: lowI, hiI = n, n+2
    else:
        for n in range(len(anchors)-1):
            if anchors[n] < M and anchors[n+1] > M: lowI, hiI = n, n+1
    return lowI, hiI

def simpleInterpo(XIN, YIN, M, log=False):
    MSS = [float(k) for k in XIN]
    INTS = [float(k) for k in YIN]
    PRED = 0
    if log:
        IL, IH = computeBoundingIndices(M, MSS)
        TF = ROOT.TF1("tempF", "[1]*TMath::Exp((x-[0])*TMath::Log([3]/[1])/([2]-[0]))", M-50, M+50)
        TF.SetParameter(0, MSS[IL])
        TF.SetParameter(1, INTS[IL])
        TF.SetParameter(2, MSS[IH])
        TF.SetParameter(3, INTS[IH])
        PRED = TF.Eval(M)
    else:
        TG = ROOT.TGraph(len(MSS), numpy.array(MSS), numpy.array(INTS))
        PRED = TG.Eval(M)
    return PRED

def RunDataCardMaker(o):
    XS = {}
    if o.NOFJ:
        XS[500] = [0.002376997004, 0.006172311027, 0.0009517303482]
        XS[600] = [0.002420969938, 0.006428743091, 0.0009903145698]
        XS[700] = [0.002413272121, 0.006576443854, 0.001006216604]
        XS[800] = [0.002349632868, 0.006563502717, 0.001028801696]
        XS[900] = [0.002339659773, 0.006605327472, 0.001039477414]
        XS[1000] = [0.002308644127, 0.006595855909, 0.001054596688]
        XS[1250] = [0.002355066722, 0.006444151058, 0.001074243378]
        XS[1500] = [0.002445121562, 0.006360010333, 0.001083958525]
        XS[1750] = [0.002478593083, 0.006583680193, 0.001063766086]
        XS[2000] = [0.002413609294, 0.006782656863, 0.001088086579]
        XS[2500] = [0.00205748369, 0.006519488412, 0.001235270073]
        XS[3000] = [0.002061827332, 0.005142698642, 0.001160230797]
    else:
        XS[500] = [0.0009702134203, 0.001395471943, 0.00002373226457]
        XS[600] = [0.0009878596181, 0.002959444199, 0.0002339956534]
        XS[700] = [0.001099890562, 0.003933398075, 0.0005715798139]
        XS[800] = [0.001543895495, 0.005010895834, 0.0007989398505]
        XS[900] = [0.001974672849, 0.005929700577, 0.0009490996989]
        XS[1000] = [0.002157485718, 0.006309343859, 0.001017651358]
        XS[1250] = [0.002333361355, 0.006406735141, 0.001067697316]
        XS[1500] = [0.002439566361, 0.006352649692, 0.001082986365]
        XS[1750] = [0.002477479046, 0.006582566156, 0.001063487576]
        XS[2000] = [0.002413609294, 0.006782378509, 0.001088086579]
        XS[2500] = [0.00205748369, 0.006519353954, 0.001235270073]
        XS[3000] = [0.002061827332, 0.005142698642, 0.001160230797]
    
    INPUTM = [500,600,700,800,900,1000,1250,1500,1750,2000,2500,3000]
    STEPARR = []
    if o.massrange != None:
        MIN, MAX, STEP = o.massrange
        STEPARR = range(MIN, MAX + STEP, STEP)
    elif o.massvarbins:
        BinEdges = [526., 565., 606., 649., 693., 740., 788., 838., 890., 944., 1000., 1058., 1118., 1181., 1246., 1313., 1383., 1455., 1530., 1607., 1687., 1770., 1856., 1945., 2037., 2132., 2231., 2332., 2438., 2546., 2659., 2775., 2895.]
        TempH = ROOT.TH1F("binedge_temp_H", ";Average Dijet Mass [GeV];Events", len(BinEdges)-1, numpy.array(BinEdges))
        STEPARR = [TempH.GetBinCenter(n) for n in range(1, TempH.GetNbinsX()+1)]
        STEPARR.extend(INPUTM)
        STEPARR = sorted(STEPARR)
    else: STEPARR = o.mass

    print(STEPARR)

    for m in STEPARR:
        if type(m)==float and m.is_integer(): m = int(m)
        print("|===> M" + str(m))
        for SL in [0, 1, 2]:
            config = " -c /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/config/fourjet_envelope_RunII_alpha%d" % SL + ("_no4J" if o.NOFJ else "") + ".config"
            mass = " --mass " + str(m)
            box = " -b PFJetHT_RunII_asl%d" % SL
            output = " -d /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/output"
            inputs = " -i /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/output/DijetFitResults_PFJetHT_RunII_asl%d.root" % SL
            inputs += " /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/PFJetHT_RunII_asl%d" % SL + ("_no4J" if o.NOFJ else "") + ".root"
            inputs += " /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M" + str(m).replace(".", "_") + "_nominal_asl%d" % SL + ("_no4J" if o.NOFJ else "") + ".root"
            
            jesup = " --jesUp /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M" + str(m).replace(".", "_") + "_jesCorr_up_asl%d" % SL + ("_no4J" if o.NOFJ else "") + ".root"
            jesdown = " --jesDown /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M" + str(m).replace(".", "_") + "_jesCorr_down_asl%d" % SL + ("_no4J" if o.NOFJ else "") + ".root"
            jerup = " --jerUp /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M" + str(m).replace(".", "_") + "_jer_up_asl%d" % SL + ("_no4J" if o.NOFJ else "") + ".root"
            jerdown = " --jerDown /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M" + str(m).replace(".", "_") + "_jer_down_asl%d" % SL + ("_no4J" if o.NOFJ else "") + ".root"
            xs = ""
            if m in INPUTM:
                xs += " --xsec %f" % XS[m][SL]
            else: 
                xsinput = [XS[j][SL] for j in INPUTM]
                xs += " --xsec %f" % simpleInterpo(INPUTM, xsinput, m)
            lumi = " --lumi 137500"
            
            dcstring = "python python/WriteDataCard_4J_envelope_Jim.py" + config + mass + box + output + inputs + jesup + jesdown + jerup + jerdown + xs + lumi + " --multi"
            print(dcstring)
            os.system(dcstring)
            
        os.chdir("/users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/output")
        os.system("combineCards.py dijet_combine_gg_gg_%s_750_lumi-137.500_PFJetHT_RunII_asl0.txt dijet_combine_gg_gg_%s_750_lumi-137.500_PFJetHT_RunII_asl1.txt dijet_combine_gg_gg_%s_750_lumi-137.500_PFJetHT_RunII_asl2.txt > Full_envelope_M%s.txt" % (str(m).replace(".", "_"), str(m).replace(".", "_"), str(m).replace(".", "_"), str(m).replace(".", "_")))
        os.chdir("..")
if __name__ == "__main__":
    from argparse import ArgumentParser
    parser = ArgumentParser()

    mass_parse = parser.add_mutually_exclusive_group(required=True)
    mass_parse.add_argument("--mass", type=int, nargs = '*', default = 1000, help="Mass can be specified as a single value or a whitespace separated list (default: %(default)s)" )
    mass_parse.add_argument("--massrange", type=int, nargs = 3, help="Define a range of masses to be produced. Format: min max step", metavar = ('MIN', 'MAX', 'STEP') )
    mass_parse.add_argument("--massvarbins", action="store_true", help="Compute limits for` RPV signals with masses equal to the bin centers of the dijet binning.")

    parser.add_argument("--no4J", action="store_true", dest="NOFJ", help="Remove four-jet mass cut and advance fit start")
    o = parser.parse_args()
    RunDataCardMaker(o)