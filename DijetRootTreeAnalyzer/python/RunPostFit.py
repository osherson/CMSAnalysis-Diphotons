import os

# os.chdir("/users/h2/th544/CMSSW_10_2_13/src/CMSDIJET/DijetRootTreeAnalyzer")
outdir = "output/PostFit"

for m in [500,600,700,800,900,1000,1250,1500,1750,2000,2500,3000]:
    dcstring = "python python/PlotPostFit.py fitDiagnostics_envelope_M%d.root %s" % (m, outdir)
    os.system(dcstring)