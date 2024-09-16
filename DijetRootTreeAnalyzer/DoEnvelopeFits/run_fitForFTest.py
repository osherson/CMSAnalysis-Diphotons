import os
import sys

clean=False
goLim = False
fast=False
doInterpo = False
fnum=999

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

#xmasslist = ['600','400','500','300','750','1000','1500','2000']
#xmasslist = ['600','400','500','200','300','750','1000','1500','2000','3000']
xmasslist = ['600']

year = 2018
#LUMI = 137   #provide lumi in fb
LUMI = 137 * 1000    #provide lumi in fb
XS = 0.001

dataDir = "../inputs/Shapes_DATA/Unblinding/full_tight_ndofBins/"


alist = []
for anum in os.listdir(dataDir):
  if(not anum.isdigit()): continue
  alist.append(int(anum))

adlist = [os.path.join(dataDir,str(aa)) for aa in sorted(alist)]

#To run test on one alpha bin, add fast# to command line arg
for arg in sys.argv:
  if 'fast' in arg:
    fnum = int(arg[4:])
    fast=True
    print("Only doing alpha bin {}".format(fnum))


def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

funcmap = {
  0:"dijet",
  1:"dijet",
  2:"dijet",
  3:"moddijet",
  4:"dijet",
  5:"dijet",
  6:"dipho",
  7:"moddijet",
  8:"dijet",
  }

sigmap = {
  0:"X1000A5",
  1:"X1000A5",
  2:"X1000A5",
  3:"X1000A5",
  4:"X1000A6",
  5:"X1000A6",
  6:"X1000A6",
  7:"X1000A6",
  8:"X1000A8",
  }

func = sys.argv[1]
#func = funcmap[anum]
#useNpar = "Three"
useNpar = sys.argv[2]
#useNpar = "Five"
useabin = int(sys.argv[3])

for npars in ["ThreeParams","FourParams","FiveParams","SixParams"]:
  if(npars!="{}Params".format(useNpar)): continue
  #if(npars!="ThreeParams"): continue
  #if(npars!="FourParams"): continue
  #if(npars!="FiveParams"): continue
  #if(npars!="SixParams"): continue

  if(func=="moddijet" and npars=="SixParams"):continue

  for adir in adlist:
    anum = int(adir[adir.rfind("/")+1:])
    if(anum != useabin ):continue
    #if(anum != 6 ):continue
    os.system("cp ../config/{}/diphoton_{}_alpha{}.config ../config/diphoton_{}.config".format(npars,func,anum,func))
    print("cp ../config/{}/diphoton_{}_alpha{}.config ../config/diphoton_{}.config".format(npars,func,anum,func))

    signal = sigmap[anum]
    MakeFolder("output/alpha_{}".format(anum))
    MakeFolder("output/alpha_{}/{}".format(anum,signal))
    eff = 1
    eff_su = 1
    GorI="int"

    rfile = open("{}/arange.txt".format(adir),"r")
    rr = rfile.readline().split(",")
    la,ha = rr[0],rr[1]
    rfile.close()
    
    print("Alpha Bin {}".format(anum))
    print("{} - {}".format(la,ha))
    
    dfname = "{}/DATA.root".format(adir)

    #mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/envelope2/diphoton_multi_alpha{}.config -y {} -l {} -b DIPHOM_alpha{} {} -d output --fit-spectrum --write-fit --words test  --abin {} --lowA {} --hiA {}".format(anum,year,LUMI,anum,dfname,anum,la,ha)
    #mycommand = "python ../python/BinnedDiphotonFitPretty.py -c ../config/envelope2/diphoton_multi_alpha{}.config -y {} -l {} -b DIPHOM_alpha{} {} -d output --fit-spectrum --write-fit True --words test  --abin {} --lowA {} --hiA {}".format(anum,year,LUMI,anum,dfname,anum,la,ha)

    mycommand = "python ../python/BinnedDiphotonFitPretty.py -c ../config/diphoton_{}.config -y {} -l {} -b diphoton_{} {} -d output -s {} --fit-spectrum --write-fit True --words test --abin {} --lowA {} --hiA {}".format(func,year,LUMI,func,dfname,signal,anum,la,ha)
    print(mycommand)
    os.system(mycommand)
    os.system("rm crudeFitPlot_diphoton_{}_X100A10_alpha{}.png".format(func,anum,signal))
    #continue

    #Now Make Cards

    os.system("mv output/fit_mjj_Full_diphoton_{}_2018_X100A10_alpha{}.png output/alpha_{}/{}/fit_mjj_Full_diphoton_{}_{}_{}.png ".format(func,anum,anum,signal,func,signal,anum))
    os.system("rm output/fit_mjj_Full_diphoton_{}_2018_X100A10_alpha{}.C ".format(func,anum))
    os.system("mv output/DijetFitResults_diphoton_{}_2018_X100A10_alpha{}.root output/alpha_{}/{}/DijetFitResults_diphoton_{}_diphoton_{}_alpha{}.root ".format(func,anum, anum,signal,signal,func,anum))
    os.system("mv output/Plots_diphoton_{}_X100A10_alpha{}.root output/alpha_{}/{}/Plots_DIPHOM_alpha{}_{}.root ".format(func,anum,anum,signal,anum,signal))

    lcommand = "python ../python/DiphotonCardMakerAlphaBinSingle_envelope.py -f diphoton_{} -l {} -y {} -a {} -s {} -x {} --xsecsu {} -g {}".format(func, LUMI, year, anum, signal, XS*eff, XS*eff_su, GorI)
    print(lcommand)
    MakeFolder("output/combineCards")
    os.system(lcommand)

    cname = "output/dijet_combine_gg_{}_alpha{}_lumi-137.000_2018_diphoton_{}".format(signal,anum,func)
    ocname = "output/combineCards/dipho_combine_{}_lumi-137.00_RunII_{}_alphabin{}".format(func,signal,anum)
    fpname = "{}/output/combineCards/dipho_combine_{}_lumi-137.00_RunII_{}_alphabin{}".format(os.getcwd(),func,signal,anum)

    try:
      with open('{}.txt'.format(cname), 'r') as input_file, open('{}.txt'.format(ocname), 'w') as output_file:
        print("File successfully opened: {}.txt".format(cname))
        for line in input_file:
          if line.startswith('shapes') and cname in line:
            output_file.write(line.replace(cname,fpname))
          else:
            output_file.write(line)
        print("Saving card as: {}.txt".format(ocname))
      os.system("mv {}.root {}.root".format(cname, ocname))
      os.system("rm {}.txt ".format(cname))
   
    except IOError:
      print("Something went wrong")


  if("save" in sys.argv):
    MakeFolder("saveOutput/Unblind/FTest/{}".format(func))
    MakeFolder("saveOutput/Unblind/FTest/{}/{}".format(func, npars))
    os.system("rm saveOutput/Unblind/FTest/{}/{}/*".format(func, npars))
    os.system("mv output/* saveOutput/Unblind/FTest/{}/{}/.".format(func, npars))

