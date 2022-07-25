import os
import sys

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

dir_path = os.path.dirname(os.path.realpath(__file__))

year = 2018
lumi = 13.7

#xasig = "X600A3"
xasig = "X1000A10"
data_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alpha1/{}_2Sigma_pt90".format(xasig)

dirs = []

for dd in os.listdir(data_dir):
  anum = int(dd[0:dd.find("X")])
  rangeFile = open("{}/{}/range.txt".format(data_dir,dd),"r")
  rr = rangeFile.readline().rstrip()
  la = float(rr.split(",")[0])
  ha = float(rr.split(",")[-1])
  dirs.append(("{}/{}".format(data_dir,dd), anum,la,ha))

  MakeFolder("output/{}/alpha_{}".format(xasig,anum))
  os.system("cp {}/{}/range.txt output/{}/alpha_{}/.".format(data_dir,dd,xasig,anum))

#dirs = [dirs[0]]

fitfuncs = ["dijet","moddijet","atlas","dipho","csch","myexp"]
#fitfuncs=[fitfuncs[0]]
#fitfuncs=["myexp"]

for (dd,anum,la,ha) in dirs:
  for ff in fitfuncs:
    mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/diphoton_{}.config -y {} -l {} -b diphoton_{} {}/PLOTS_{}.root -d output --fit-spectrum --write-fit --words test".format(ff,year,lumi,ff,dd,xasig)
    print(mycommand)
    os.system(mycommand)
    os.system("mv output/fit_mjj_Full_diphoton_{}_2018.png output/{}/alpha_{}/fit_mjj_Full_diphoton_{}_2018.png ".format(ff,xasig,anum,ff))
    os.system("mv output/fit_mjj_Full_diphoton_{}_2018.C output/{}/alpha_{}/fit_mjj_Full_diphoton_{}_2018.C ".format(ff,xasig,anum,ff))
    os.system("mv output/DijetFitResults_diphoton_{}_2018.root output/{}/alpha_{}/DijetFitResults_diphoton_{}_2018.root ".format(ff,xasig,anum,ff))

os.system("rm crude*")
os.system("rm stuff*")
os.system("rm output/corr*")

