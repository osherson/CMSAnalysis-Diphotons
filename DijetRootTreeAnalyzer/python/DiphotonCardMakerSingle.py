import os
import sys

def RunDataCardMaker(o):
    config = " -c config/diphoton_%s" % (str(o.FIT))+".config"
    lumi = " --lumi " + str(int(float(o.LUM)*1000.))
    box = " -b diphoton"#_" + str(o.SIG)
    if o.FIT != "combine": box += "_%s" % str(o.FIT)
    mass = " --mass " + str(o.SIG).split("X")[1].split("A")[0]
    savemass = " --savemass " + str(o.SIG)
    output = " -d output"
    xs = " --xsec " + o.XS

    yr = str(o.YEAR)
    year = " --year " + yr

    if(os.path.exists("inputs/Shapes_fromGen/" + yr + "/" + str(o.SIG) + "/DATA.root")):
      inputs = " -i output/DijetFitResults_diphoton_{}_{}.root".format(str(o.FIT),yr)
      inputs += " inputs/Shapes_fromGen/" + yr + "/" + str(o.SIG) + "/DATA.root"
      inputs += " inputs/Shapes_fromGen/"+ yr + "/" + str(o.SIG)+"/Sig_nominal.root"
      jesup = " --jesUp inputs/Shapes_fromGen/"+ yr + "/" + str(o.SIG)+"/Sig_SU.root"
      jesdown = " --jesDown inputs/Shapes_fromGen/"+ yr + "/" + str(o.SIG)+"/Sig_SD.root"
      jerup = " --jerUp inputs/Shapes_fromGen/"+ yr + "/" + str(o.SIG)+"/Sig_PU.root"
      jerdown = " --jerDown inputs/Shapes_fromGen/"+ yr + "/" + str(o.SIG)+"/Sig_PD.root"

    else:
      inputs = " -i output/DijetFitResults_diphoton_{}_{}.root".format(str(o.FIT),yr)
      inputs += " inputs/Shapes_fromInterpo/" + yr + "/" + str(o.SIG) + "/DATA.root"
      inputs += " inputs/Shapes_fromInterpo/"+ yr + "/" + str(o.SIG)+"/Sig_nominal.root"
      jesup = " --jesUp inputs/Shapes_fromInterpo/"+ yr + "/" + str(o.SIG)+"/Sig_SU.root"
      jesdown = " --jesDown inputs/Shapes_fromInterpo/"+ yr + "/" + str(o.SIG)+"/Sig_SD.root"
      jerup = " --jerUp inputs/Shapes_fromInterpo/"+ yr + "/" + str(o.SIG)+"/Sig_PU.root"
      jerdown = " --jerDown inputs/Shapes_fromInterpo/"+ yr + "/" + str(o.SIG)+"/Sig_PD.root"

    dcstring = "python python/WriteDataCard_photons.py" + config + mass + savemass + year + box + output + inputs + jesup + jesdown + jerup + jerdown + xs + lumi
    print(dcstring)
    os.system(dcstring)

if __name__ == "__main__":
    from optparse import OptionParser
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--fit", dest="FIT", type=str, help="name of fit function", metavar="FITFUNC")
    parser.add_option("-l", "--lumi", dest="LUM", type=str, help="lumi in this sample (in fb-1)", metavar="THELUMI")
    parser.add_option("-y", "--year", dest="YEAR", type=str, help="Run II Year", metavar="THELUMI")
    parser.add_option("-s", "--sig", dest="SIG", type=str, help="signal samples", metavar="THESIGNAL")
    parser.add_option("-x", "--xsec", dest="XS", type=str, help="signal xs", metavar="THESIGNALxs")
    (o, args) = parser.parse_args()
    RunDataCardMaker(o)
