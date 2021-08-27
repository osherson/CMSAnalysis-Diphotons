import os

def RunFitter(o):
    for SL in [0,1,2]:
        config = " -c config/fourjet_%s_RunII_alpha%d" % (str(o.FIT), SL) + ("_no4J" if o.NOFJ else "") + ".config"
        lumi = " -l 137500"
        box = " -b PFJetHT_RunII_asl%d" % SL
        if o.FIT is not "combine": box += "_%s" % str(o.FIT)
        input = " inputs/PFJetHT_RunII_asl%d" % SL + ("_no4J" if o.NOFJ else "") + ".root"
        output = " -d output"
        
        dcstring = "python python/BinnedFit.py" + config + lumi + box + input + output + " --fit-spectrum --write-fit"
        os.system(dcstring)

if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-f", "--fit", dest="FIT", help="name of fit function", metavar="FITFUNC")
    parser.add_option("--no4J", action="store_true", dest="NOFJ", help="remove four-jet cut and advance fit start")
    (o, args) = parser.parse_args()
    RunFitter(o)