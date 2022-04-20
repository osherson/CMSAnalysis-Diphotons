import os

def RunFitter(o):
    config = " -c config/diphoton_%s" % (str(o.FIT))+".config"
    lumi = " -l " + str(int(float(o.LUM)*1000.))
    box = " -b diphoton"#_" + str(o.SIG)
    words = " --words " + o.WORDS
    if o.FIT != "combine": box += "_%s" % str(o.FIT)
    input = " inputs/" + str(o.SIG) + "/PLOTS_" + str(o.SIG) + ".root"
    print(input)
    if(os.path.exists(input)):
      print("Getting Generated Shape for {}".format(o.SIG))
    else:
      print("Getting Interpolated Shape for {}".format(o.SIG))
      input = " inputs/Shapes_fromInterpo/" + str(o.SIG) + "/PLOTS_" + str(o.SIG) + ".root"
    output = " -d output"
    
    dcstring = "python python/BinnedDiphotonFit.py" + config + lumi + box + input + output + " --fit-spectrum --write-fit" + words
    os.system(dcstring)

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--fit", dest="FIT", type=str, help="name of fit function", metavar="FITFUNC")
    parser.add_option("-l", "--lumi", dest="LUM", type=str, help="lumi in this sample (in fb-1)", metavar="THELUMI")
    parser.add_option("-s", "--sig", dest="SIG", type=str, help="signal samples", metavar="THESIGNAL")
    parser.add_option("-w", "--words", dest="WORDS", type=str, help="cut string", metavar="WORDS")
    (o, args) = parser.parse_args()
    RunFitter(o)
