import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))

def RunDataCardMaker(o):
    env=False
    if("envelope" in o.FIT):
      env=True

    if(env):
      config = " -c {}/../config/envelope/{}".format(dir_path,str(o.FIT)) + ".config"
      box=" -b "
    else:
      config = " -c {}/../config/diphoton_{}".format(dir_path,str(o.FIT)) + ".config"
      box = " -b diphoton_"

    lumi = " --lumi " + str(int(float(o.LUM)*1000.))
    if o.FIT != "combine": box += "%s" % str(o.FIT)
    mass = " --mass " + str(o.SIG).split("X")[1].split("A")[0]
    savemass = " --savemass " + str(o.SIG)
    output = " -d output"
    xs = " --xsec " + o.XS

    yr = str(o.YEAR)
    year = " --year " + yr

    abin = str(o.ABIN)
    sig = str(o.SIG)

    if(os.path.exists(dir_path + "/../inputs/Shapes_fromGen/alphaBinning/" + abin + "/" + str(o.SIG) + "/DATA.root")):
      if(env):
        inputs = " -i output/alpha_{}/{}/DijetFitResults_diphoton_{}_{}.root".format(abin,sig,sig,str(o.FIT))
      else:
        inputs = " -i output/alpha_{}/{}/DijetFitResults_diphoton_{}_{}_alpha{}.root".format(abin,sig,sig,str(o.FIT),abin)
      inputs += " {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path)  + abin+"/"+sig+ "/DATA.root"
      inputs += " {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_nominal.root"
      jesup = " --jesUp {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_SU.root"
      jesdown = " --jesDown {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_SD.root"
      jerup = " --jerUp {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_PU.root"
      jerdown = " --jerDown {}/../inputs/Shapes_fromGen/alphaBinning/".format(dir_path) + abin +"/"+sig+"/Sig_PD.root"

    else:
      print("IN ELSE LOOP")
      exit()
      inputs = " -i output/DijetFitResults_diphoton_{}_{}.root".format(str(o.FIT),yr)
      inputs += " inputs/Shapes_fromInterpo/" + yr + "/" + str(o.SIG) + "/DATA.root"
      inputs += " inputs/Shapes_fromInterpo/"+ yr + "/" + str(o.SIG)+"/Sig_nominal.root"
      jesup = " --jesUp inputs/Shapes_fromInterpo/"+ yr + "/" + str(o.SIG)+"/Sig_SU.root"
      jesdown = " --jesDown inputs/Shapes_fromInterpo/"+ yr + "/" + str(o.SIG)+"/Sig_SD.root"
      jerup = " --jerUp inputs/Shapes_fromInterpo/"+ yr + "/" + str(o.SIG)+"/Sig_PU.root"
      jerdown = " --jerDown inputs/Shapes_fromInterpo/"+ yr + "/" + str(o.SIG)+"/Sig_PD.root"

    dcstring = "python {}/../python/WriteDataCard_photons.py".format(dir_path) + config + mass + savemass + year + box + output + inputs + jesup + jesdown + jerup + jerdown + xs + lumi
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
    (o, args) = parser.parse_args()
    RunDataCardMaker(o)
