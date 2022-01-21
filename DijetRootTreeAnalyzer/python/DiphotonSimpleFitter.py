import os

def RunFitter(o):
    config = " -c config/diphoton_%s" % (str(o.FIT))+".config"
    lumi = " -l " + str(int(float(o.LUM)*1000.))
    box = " -b diphoton"#_" + str(o.SIG)
    if o.FIT != "combine": box += "_%s" % str(o.FIT)
    input = " inputs/" + str(o.SIG) + "/PLOTS_" + str(o.SIG) + ".root"
    output = " -d output"
    
    dcstring = "python python/BinnedDiphotonFit.py" + config + lumi + box + input + output + " --fit-spectrum --write-fit"
    os.system(dcstring)

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--fit", dest="FIT", type=str, help="name of fit function", metavar="FITFUNC")
    parser.add_option("-l", "--lumi", dest="LUM", type=str, help="lumi in this sample (in fb-1)", metavar="THELUMI")
    parser.add_option("-s", "--sig", dest="SIG", type=str, help="signal samples", metavar="THESIGNAL")
    (o, args) = parser.parse_args()
    RunFitter(o)