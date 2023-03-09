import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))

def RunDataCardMaker(o):
    env=False
    if("envelope" in o.FIT or "multi" in o.FIT or "DIPHOM" in o.FIT):
      env=True

    abin = str(o.ABIN)
    sig = str(o.SIG)
    gi = o.GI
    print("GEN OR INT",gi)

    if(env):
      if(abin=="ALL"):
        config = " -c {}/../config/envelope2/diphoton_multi_alpha0.config".format(dir_path,abin)
      else:
        config = " -c {}/../config/envelope2/diphoton_multi_alpha{}.config".format(dir_path,abin)
      box=" -b "
    else:
      config = " -c {}/../config/diphoton_{}".format(dir_path,str(o.FIT)) + ".config"
      box = " -b diphoton_"

    lumi = " --lumi " + str(int(float(o.LUM)))
    if o.FIT != "combine": box += "%s" % str(o.FIT)
    mass = " --mass " + str(o.SIG).split("X")[1].split("A")[0]
    savemass = " --savemass " + str(o.SIG)
    output = " -d output"
    xs = " --xsec " + o.XS
    xssu = " --xsecsu " + o.XSsu

    yr = str(o.YEAR)
    year = " --year " + yr
    multi = " --multi {}".format(env)
    alphabin = " --abin {}".format(abin)

    if(abin=="ALL"):
      if(not os.path.exists(dir_path + "/../inputs/Shapes_fromGen/OneBigBin/"  + str(o.SIG) + "/DATA.root")):
        print("No data, in all loop")
        print("Check sig {}".format(o.SIG))
        exit()
      if(env):
        inputs = " -i output/alpha_0/{}/DijetFitResults_DIPHOM_2018_{}_alpha0.root".format(sig,sig)
      else:
        inputs = " -i output/alpha_0/{}/DijetFitResults_diphoton_{}_{}_alpha0.root".format(sig,sig,str(o.FIT))
      inputs += " {}/../inputs/Shapes_fromGen/OneBigBin/".format(dir_path)  + sig+ "/DATA.root"
      inputs += " {}/../inputs/Shapes_fromGen/OneBigBin/".format(dir_path) + sig+"/Sig_nominal.root"
      jesup = " --jesUp {}/../inputs/Shapes_fromGen/OneBigBin/".format(dir_path) + sig+"/Sig_SU.root"
      jesdown = " --jesDown {}/../inputs/Shapes_fromGen/OneBigBin/".format(dir_path) +sig+"/Sig_SD.root"
      jerup = " --jerUp {}/../inputs/Shapes_fromGen/OneBigBin/".format(dir_path) + sig+"/Sig_PU.root"
      jerdown = " --jerDown {}/../inputs/Shapes_fromGen/OneBigBin/".format(dir_path) +sig+"/Sig_PD.root"

    if(abin !="ALL"):
      #if(os.path.exists(dir_path + "/../inputs/Shapes_fromGen/alphaBinning/" + abin + "/" + str(o.SIG) + "/DATA.root")):
      if(gi=="gen"):
        if(env):
          inputs = " -i output/alpha_{}/{}/DijetFitResults_DIPHOM_2018_{}_alpha{}.root".format(abin,sig,sig,abin)
        else:
          inputs = " -i output/alpha_{}/{}/DijetFitResults_diphoton_{}_{}_alpha{}.root".format(abin,sig,sig,str(o.FIT),abin)
        inputs += " {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path)  + abin+"/"+sig+ "/DATA.root"
        inputs += " {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_nominal.root"
        jesup = " --jesUp {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_SU.root"
        jesdown = " --jesDown {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_SD.root"
        jerup = " --jerUp {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_PU.root"
        jerdown = " --jerDown {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_PD.root"

      #elif(os.path.exists(dir_path + "/../inputs/Shapes_fromInterpo/alphaBinning/" + abin + "/" + str(o.SIG) + "/DATA.root")):
      elif(gi=="int"):
        if(env):
          inputs = " -i output/alpha_{}/{}/DijetFitResults_DIPHOM_2018_{}_alpha{}.root".format(abin,sig,sig,abin)
        else:
          inputs = " -i output/alpha_{}/{}/DijetFitResults_diphoton_{}_{}_alpha{}.root".format(abin,sig,sig,str(o.FIT),abin)
        inputs += " {}/../inputs/Shapes_fromInterpo/alphaBinning/".format(dir_path)  + abin+"/"+sig+ "/DATA.root"
        inputs += " {}/../inputs/Shapes_fromInterpo/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_nominal.root"
        jesup = " --jesUp {}/../inputs/Shapes_fromInterpo/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_SU.root"
        jesdown = " --jesDown {}/../inputs/Shapes_fromInterpo/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_SD.root"
        jerup = " --jerUp {}/../inputs/Shapes_fromInterpo/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_PU.root"
        jerdown = " --jerDown {}/../inputs/Shapes_fromInterpo/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_PD.root"

      else:
        print("IN ELSE LOOP")
        print(abin)
        print(os.path.exists(dir_path + "/../inputs/Shapes_fromGen/alphaBinning/" + abin + "/" + str(o.SIG) + "/DATA.root"))
        exit()

    dcstring = "python {}/../python/WriteDataCard_photons_envelope.py".format(dir_path) + config + mass + savemass + year + box + output + inputs + jesup + jesdown + jerup + jerdown + xs + xssu + lumi + multi + alphabin
    print(dcstring)
    os.system(dcstring)

if __name__ == "__main__":
    from optparse import OptionParser
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--fit", dest="FIT", type=str, help="name of fit function", metavar="FITFUNC")
    parser.add_option("-l", "--lumi", dest="LUM", type=str, help="lumi in this sample (in fb-1)", metavar="THELUMI")
    parser.add_option("-y", "--year", dest="YEAR", type=str, help="Run II Year", metavar="THEYEAR")
    parser.add_option("-a", "--alphabin", dest="ABIN", type=str, help="AlphaBin Number", metavar="THEALPHA")
    parser.add_option("-s", "--sig", dest="SIG", type=str, help="signal samples", metavar="THESIGNAL")
    parser.add_option("-x", "--xsec", dest="XS", type=str, help="signal xs", metavar="THESIGNALxs")
    parser.add_option("-q", "--xsecsu", dest="XSsu", type=str, help="signal xs, scale up", metavar="THESIGNALxssu")
    parser.add_option("-g", "--GenOrInt", dest="GI", type=str, help="Generated or Interpolated", metavar="GENORINT")
    (o, args) = parser.parse_args()
    RunDataCardMaker(o)
