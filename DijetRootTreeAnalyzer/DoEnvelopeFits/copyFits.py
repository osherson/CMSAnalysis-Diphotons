import os
import sys

#print("Removing previous plots")
#os.system("rm fitPlots/*")

#outdir = "output"
outdir = "saveOutput/Unblind/full_ndof_dijet/"

for abin in os.listdir(outdir):
  if(abin.startswith("alpha")):
    adir = os.path.join(outdir,abin)
    anum = abin[len("alpha")+1 : ]
    for xa in os.listdir(adir):
      fitplot = "{}/{}/fit_mjj_Full_diphoton_dijet_{}_{}.png".format(adir, xa, xa, anum)
      #print(fitplot)
      if(os.path.exists(fitplot)):
        if(int(anum) < 25):
          letter = chr(ord('`')+int(anum)+1)
        else:
          letter = chr(ord('`')+int(anum)-25+1)
        #print("Copying {} to fitPlots/fit_{}_{}.png".format(fitplot,letter,anum))
        #os.system("cp {} fitPlots/fit_{}_{}.png".format(fitplot,letter,anum))
        print("Copying {} to fitPlots/fullAnalysisCuts/fit_{}_{}.png".format(fitplot,letter,anum))
        os.system("cp {} fitPlots/fullAnalysisCuts/fit_{}_{}.png".format(fitplot,letter,anum))
        break
