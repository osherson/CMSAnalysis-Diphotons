import sys
import os

if("clean" in sys.argv):
  print("Deleting Call Files and condor_submit Files")
  os.system("rm CallFiles/*")
  os.system("rm condor_submitFiles/*")
  print("Done deleting")

dir_path = os.path.dirname(os.path.realpath(__file__))

interp_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/"
gen_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning/"

ct = 0

for dir_base in [interp_dir, gen_dir]:
  for alphaBin in os.listdir(dir_base):
    for xx in os.listdir(os.path.join(dir_base,alphaBin)):
      #if(ct > 10): break #For testing
      mydir = "{}/{}/{}".format(gen_dir, alphaBin, xx)
  
      rt_file = open("Call_template.sh","r")
      r_file = open("CallFiles/Call_alpha{}_{}.sh".format(alphaBin,xx),"w")
      for line in rt_file.readlines():
        line = line.replace("ALPHA", "{}".format(alphaBin))
        line = line.replace("SIGNAL", "{}".format(xx))
        if(dir_base == interp_dir):
          line = line.replace("USEINTERP","Interpo")
        else:
          line = line.replace("USEINTERP","")
        r_file.write(line)

      rct_file = open("runCondor_template.jdl","r")
      rc_file = open("condor_submitFiles/runCondor_alpha{}_{}.jdl".format(alphaBin, xx),"w")
      for line in rct_file.readlines():
        line = line.replace("FILENAME", "Call_alpha{}_{}.sh".format(alphaBin,xx))
        rc_file.write(line)
      ct += 1

os.system("chmod +x CallFiles/*.sh")



