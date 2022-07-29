import os
import sys

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

dir_path = os.path.dirname(os.path.realpath(__file__))

xmass = sys.argv[1]

year = 2018
lumi = 13.7

data_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning/"

dirs = []

sig=""
for dd in os.listdir(data_dir):
  for xx in os.listdir(os.path.join(data_dir,dd)):
    anum = int(dd)
    if(xmass in xx): 
      #if(anum != 6): continue
      sig=xx
      rangeFile = open("{}{}/{}/arange.txt".format(data_dir,dd,xx),"r")
      rr = rangeFile.readline().rstrip()
      la = float(rr.split(",")[0])
      ha = float(rr.split(",")[-1])
      dirs.append(("{}{}".format(data_dir,dd), anum,sig,la,ha))

  MakeFolder("output/alpha_{}/{}/".format(anum,sig))
  os.system("cp {}{}/{}/arange.txt output/alpha_{}/{}/.".format(data_dir,dd,sig,anum,sig))


#dirs = [dirs[0]]

fitfuncs = ["dijet","moddijet","atlas","dipho","myexp"]
fitfuncs=[fitfuncs[0]]
#fitfuncs=["myexp"]

for (dd,anum,sig,la,ha) in dirs:
  abin_num = int(dd.split("/")[-1])
  for ff in fitfuncs:
    mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/diphoton_{}.config -y {} -l {} -b diphoton_{} {}/{}/PLOTS_{}.root -d output --fit-spectrum --write-fit --words test".format(ff,year,lumi,ff,dd,sig,abin_num)
    print(mycommand)
    os.system(mycommand)
    os.system("mv output/fit_mjj_Full_diphoton_{}_2018.png output/alpha_{}/{}/fit_mjj_Full_diphoton_{}_2018.png ".format(ff,abin_num,sig,ff))
    os.system("mv output/fit_mjj_Full_diphoton_{}_2018.C output/alpha_{}/{}/fit_mjj_Full_diphoton_{}_2018.C ".format(ff,abin_num,sig,ff))
    os.system("mv output/DijetFitResults_diphoton_{}_2018.root output/alpha_{}/{}/DijetFitResults_diphoton_{}_2018.root ".format(ff,abin_num,sig,ff))

os.system("rm crude*")
os.system("rm stuff*")
os.system("rm output/corr*")

