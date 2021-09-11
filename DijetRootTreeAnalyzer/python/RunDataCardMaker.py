import os
import sys

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
    
    for M in [500,600,700,800,900,1000,1250,1500,1750,2000,2500,3000]:
        for SL in [0, 1, 2]:
            config = " -c /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/config/fourjet_%s_RunII_alpha%d" % (str(o.FIT), SL) + ("_no4J" if o.NOFJ else "") + ".config"
            mass = " --mass %d" % M
            box = " -b PFJetHT_RunII_asl%d_%s" % (SL, str(o.FIT))
            output = " -d /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/output"
            inputs = " -i /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/output/DijetFitResults_PFJetHT_RunII_asl%d_%s.root" % (SL, str(o.FIT))
            inputs += " /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/PFJetHT_RunII_asl%d" % SL + ("_no4J" if o.NOFJ else "") + ".root"
            inputs += " /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M%d_nominal_asl%d" % (M, SL) + ("_no4J" if o.NOFJ else "") + ".root"
            jesup = " --jesUp /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M%d_jesCorr_up_asl%d" % (M, SL) + ("_no4J" if o.NOFJ else "") + ".root"
            jesdown = " --jesDown /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M%d_jesCorr_down_asl%d" % (M, SL) + ("_no4J" if o.NOFJ else "") + ".root"
            jerup = " --jerUp /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M%d_jer_up_asl%d" % (M, SL) + ("_no4J" if o.NOFJ else "") + ".root"
            jerdown = " --jerDown /users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer/inputs/rpv_M%d_jer_down_asl%d" % (M, SL) + ("_no4J" if o.NOFJ else "") + ".root"
            xs = " --xsec %f" % XS[M][SL]
            lumi = " --lumi 137500"
            
            dcstring = "python python/WriteDataCard_4J.py" + config + mass + box + output + inputs + jesup + jesdown + jerup + jerdown + xs + lumi
            print(dcstring)
            os.system(dcstring)
            
        os.chdir("output")
        os.system("combineCards.py dijet_combine_gg_%d_lumi-137.500_PFJetHT_RunII_asl0_%s.txt dijet_combine_gg_%d_lumi-137.500_PFJetHT_RunII_asl1_%s.txt dijet_combine_gg_%d_lumi-137.500_PFJetHT_RunII_asl2_%s.txt > Full_%s_M%d.txt" % (M, str(o.FIT), M, str(o.FIT), M, str(o.FIT), str(o.FIT), M))
        os.chdir("..")
        
if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--fit", dest="FIT", help="Name of fit function. Valid choices are 'atlas', 'dijet', and 'moddijet'.", metavar="FITFUNC")
    parser.add_option("--no4J", action="store_true", dest="NOFJ", help="remove four-jet mass cut and advance fit start")
    (o, args) = parser.parse_args()
    RunDataCardMaker(o)