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

#for dir_base in [interp_dir, gen_dir]:
#for dir_base in [gen_dir]:
for dir_base in [interp_dir]:
  for alphaBin in os.listdir(dir_base):
    for xx in os.listdir(os.path.join(dir_base,alphaBin)):
      #if(ct > 1000): break #For testing
      mydir = "{}/{}/{}".format(gen_dir, alphaBin, xx)
  
      rt_file = open("Call_template.sh","r")
      #r_file = open("CallFiles/Call_alpha{}_{}.sh".format(alphaBin,xx),"w")
      r_file = open("CallFiles/Call_{}.sh".format(ct),"w")
      for line in rt_file.readlines():
        line = line.replace("ALPHA", "{}".format(alphaBin))
        line = line.replace("SIGNAL", "{}".format(xx))
        if(dir_base == interp_dir):
          line = line.replace("USEINTERP","Interpo")
        else:
          line = line.replace("USEINTERP","")
        r_file.write(line)

      ct += 1

os.system("chmod +x CallFiles/*.sh")

DIR = "CallFiles"
ncalls = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
print("Number files: {}".format(ncalls))
os.system("sed -i \"s/ Queue.*/ Queue {}/g\" runCondor.jdl".format(ncalls))




