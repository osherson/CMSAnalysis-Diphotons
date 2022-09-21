import os
import sys

goLim = False
fast=False
doAll = False
doInterpo = False
fnum=999

SIGNAL = sys.argv[1]
ALPHA_BIN = sys.argv[2]

#To run test on one alpha bin, add fast# to command line arg
for arg in sys.argv:
  if 'fast' in arg:
    fnum = int(arg[4:])
    fast=True
    print("Only doing alpha bin {}".format(fnum))

if ('limit' in sys.argv): goLim = True
if ('ALL' in sys.argv): doAll = True
if ('Interpo' in sys.argv): doInterpo = True

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

year = 2018
lumi = 13.7

def getEff(s, d):
  effFile = "{}/{}.txt".format(d,s)
  with open(effFile) as f:
    eff = float(f.readline().rstrip())
  return eff

def makeThisLimit(signal, alphaBin):
  global year, lumi

  if(doInterpo):
    data_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/"
  else:
    data_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning/"
  dirs = []

  if(doAll == True):
      mydir = data_dir + "ALL/" + signal
      if(os.path.exists("{}/PLOTS_0.root".format(mydir))):
            rangeFile = open("{}/arange.txt".format(mydir),"r")
            rr = rangeFile.readline().rstrip()
            la = float(rr.split(",")[0])
            ha = float(rr.split(",")[-1])
            rangeFile.close()
      else: 
        print("Signal Shape does not exist in this alpha bin")
        print("Directory is empty: {}".format(mydir))
        return
  else:
      mydir = data_dir + alphaBin + "/" + signal
      if(os.path.exists("{}/PLOTS_{}.root".format(mydir,alphaBin))):
            rangeFile = open("{}/arange.txt".format(mydir),"r")
            rr = rangeFile.readline().rstrip()
            la = float(rr.split(",")[0])
            ha = float(rr.split(",")[-1])
            rangeFile.close()
      else: 
        print("Signal Shape does not exist in this alpha bin")
        print("Directory is empty: {}".format(mydir))
        return

  if(goLim): MakeFolder("combineOutput/alpha{}".format(alphaBin))

  sigX = float(signal[1 : signal.find("A")])
  sigPhi = float(signal[signal.find("A")+1:].replace("p","."))
  sigAlpha = sigPhi / sigX
  abin_num = alphaBin

  print("Starting {} Signal, alpha bin {}" .format(signal, abin_num))
  MakeFolder("output/alpha_{}/{}".format(abin_num,signal))
  os.system("cp {}/{}/{}/arange.txt output/alpha_{}/{}/.".format(data_dir,abin_num,signal,abin_num,signal))
  
  if(goLim==True and os.path.exists("combineOutput/alpha{}/higgsCombine_envelope_alpha{}_{}.root".format(alphaBin, alphaBin, signal))):
    print(abin_num, signal)
    print("Limit already done, moving on. ")
    return

  elif(goLim==False and os.path.exists("output/combineCards/CARD_multi_{}_alpha{}.txt".format(signal,abin_num))):
    print(abin_num, signal)
    print("Card already done, moving on. ")
    return

  #GetSignal and efficiency
  with open("{}/{}.txt".format(mydir,signal)) as f:
    eff = float(f.readline().rstrip())
    print(eff)

  if(doAll):
    mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/envelope2/diphoton_multi.config -y {} -l {} -b DIPHOM {}/PLOTS_0.root -d output --fit-spectrum --write-fit --words test --lowA {} --hiA {}".format(year,lumi,mydir, la, ha)
  else:
    mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/envelope2/diphoton_multi.config -y {} -l {} -b DIPHOM {}/PLOTS_{}.root -d output --fit-spectrum --write-fit --words test --lowA {} --hiA {}".format(year,lumi,mydir,abin_num, la, ha)
  print(mycommand)

  os.system(mycommand)
  os.system("mv output/fit_mjj_Full_DIPHOM_2018.png output/alpha_{}/{}/fit_mjj_Full_diphoton_{}_{}.png ".format(abin_num,signal,signal,abin_num))
  os.system("mv output/fit_mjj_Full_DIPHOM_2018.C output/alpha_{}/{}/fit_mjj_Full_diphoton_{}_{}.C ".format(abin_num,signal,signal,abin_num))
  os.system("mv output/DijetFitResults_*2018.root output/alpha_{}/{}/DijetFitResults_diphoton_{}_DIPHOM.root ".format(abin_num,signal,signal))

  lcommand = "python ../python/DiphotonCardMakerAlphaBinSingle_envelope.py -f DIPHOM -l {} -y {} -a {} -s {} -x {}".format(lumi/10, year, abin_num, signal, eff)
  print(lcommand)
  MakeFolder("output/combineCards")
  os.system(lcommand)

  cname = "output/dijet_combine_gg_{}_lumi-1.370_2018_DIPHOM".format(signal)
  ocname = "output/combineCards/CARD_multi_{}_alpha{}".format(signal,abin_num)
  fpname = "{}/output/combineCards/CARD_multi_{}_alpha{}".format(os.getcwd(),signal,abin_num)

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
    return

  
  os.system("rm crude*")
  os.system("rm stuff*")
  os.system("rm output/corr*")

  print(goLim)
  if goLim:
    for of in os.listdir("output/combineCards"):
      if( os.path.join("output/combineCards",of)=="{}.txt".format(ocname)):
        comb_command = "combine {} -M AsymptoticLimits -n _alpha{}_{}".format(os.path.join("output/combineCards",of), abin_num, signal)
        print(comb_command)
        os.system(comb_command)
        os.system("mv higgsCombine_alpha{}_{}.AsymptoticLimits.mH120.root combineOutput/alpha{}/higgsCombine_envelope_alpha{}_{}.root".format(abin_num,signal,abin_num,abin_num,signal))

###################

makeThisLimit(SIGNAL, ALPHA_BIN)
