import os
import sys
import PlotDataSigTogether as PT

goLim = False
fast=False
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
if ('Interpo' in sys.argv): doInterpo = True

def pdiff(n1,n2):
  #return abs(n1-n2)/n1
  return (n2-n1)/n1

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

year = 2018
LUMI = 137 * 1000 
XS = 0.001
#XS = 0.01
#XS = 0.1
#XS = 0.00015
#XS = 0.0001
#XS = 0.00001

def getEff(s, d):
  effFile = "{}/{}.txt".format(d,s)
  with open(effFile) as f:
    eff = float(f.readline().rstrip())
  return eff

#GEN_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/"
#INT_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning/"

INT_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/"
#INT_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning_allBins/"
GEN_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning/"
def makeThisLimit(signal, alphaBin):
  global year, LUMI
  FRAC_THRESH=5./100. #5%
  FRAC_THRESH=0./100. #5%

  if(doInterpo):
    data_dir = INT_dir
    GorI = "int"
  else:
    data_dir = GEN_dir
    GorI = "gen"
  dirs = []

  mydir = data_dir + alphaBin + "/" + signal
  print(mydir)
  print(doInterpo)
  if(os.path.exists("{}/PLOTS_{}.root".format(mydir,alphaBin))):
        fracName="{}/alphaFraction_alpha{}_{}_su.txt".format(mydir,alphaBin,signal)
        if(os.path.exists(fracName)):
          fracFile = open(fracName, "r")
          frac = float(fracFile.readline())
        elif(os.path.exists(fracName.replace("_su",""))):
          fracName = fracName.replace("_su","")
          fracFile = open(fracName, "r")
          frac = float(fracFile.readline())
        else:
          print("No Frac File. Quitting")
          exit()
        #if(frac < FRAC_THRESH or frac > 0.1) : 
        #if(frac < FRAC_THRESH) : 
        #  fracFile.close()
        #  print("Not enough signal in this bin. Moving on")
        #  return
        fracFile.close()
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
  #PT.PlotTogether(signal, abin_num, "output/alpha_{}/{}".format(alphaBin,signal))
  os.system("cp {}/{}/{}/arange.txt output/alpha_{}/{}/.".format(data_dir,abin_num,signal,abin_num,signal))
  
  """
  if(goLim==True and os.path.exists("combineOutput/alpha{}/higgsCombine_envelope_alpha{}_{}.root".format(alphaBin, alphaBin, signal))):
    print(abin_num, signal)
    print("Limit already done, moving on. ")
    return

  elif(goLim==False and os.path.exists("output/combineCards/CARD_multi_{}_alpha{}.txt".format(signal,abin_num))):
    print(abin_num, signal)
    print("Card already done, moving on. ")
    return
  """

  #GetSignal and efficiency
  print("{}/{}.txt".format(mydir,signal))
  with open("{}/{}.txt".format(mydir,signal)) as f:
    eff = float(f.readline().rstrip())
    print(eff)
  #eff = 1.

  #FIX THIS YOU GOTTA PUT THIS BACK IN
  eff_su = 1
  with open("{}/{}_su.txt".format(mydir,signal)) as f:
    eff_su = float(f.readline().rstrip())
  eff_sd = 1
  with open("{}/{}_sd.txt".format(mydir,signal)) as f:
    eff_sd = float(f.readline().rstrip())
  #eff = eff_su
  print(eff, eff_sd, eff_su)
  print(XS*eff, XS*eff_sd, XS*eff_su)
  pdiff_up = pdiff(XS*eff, XS*eff_su)
  pdiff_down = pdiff(XS*eff, XS*eff_sd)
  print(pdiff_down, pdiff_up)
  print(1+pdiff_down, 1+pdiff_up)

  #func = "dijet"
  mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/envelope2/diphoton_multi_alpha{}.config -y {} -l {} -b DIPHOM_alpha{} {}/PLOTS_{}.root -d output --fit-spectrum --write-fit --words test --sig {} --abin {} --lowA {} --hiA {}".format(abin_num,year,LUMI,abin_num,mydir,abin_num,signal,abin_num,la,ha)
  #mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/ThreeParams/diphoton_{}.config -y {} -l {} -b diphoton_{} {}/PLOTS_{}.root -d output --fit-spectrum --write-fit True --words test --abin {} --lowA {} --hiA {} --sig {}".format(func,year,LUMI,func,mydir,abin_num,abin_num,la,ha, signal)

  print(mycommand)

  os.system(mycommand)

  os.system("mv output/fit_mjj_Full_diphoton_dipho_2018_{}_alpha{}.png output/alpha_{}/{}/fit_mjj_Full_diphoton_dipho_{}_{}.png ".format(signal,abin_num,abin_num,signal,signal,abin_num))
  os.system("rm crudeFitPlot_DIPHOM_alpha{}_{}_alpha{}.png".format(abin_num,signal,abin_num))
  os.system("rm output/Plots_DIPHOM_alpha{}_{}_alpha{}.root".format(abin_num,signal,abin_num))
  os.system("rm output/fit_mjj_Full_DIPHOM_alpha{}_2018_{}_alpha{}.C ".format(abin_num,signal,abin_num))
  os.system("mv output/DijetFitResults_DIPHOM_alpha{}_2018_{}_alpha{}.root output/alpha_{}/{}/DijetFitResults_DIPHOM_2018_{}_alpha{}.root ".format(abin_num,signal,abin_num,abin_num,signal,signal,abin_num))

  #os.system("mv output/fit_mjj_Full_diphoton_{}_2018_{}_alpha{}.png output/alpha_{}/{}/fit_mjj_Full_diphoton_{}_{}_{}.png ".format(func,signal,abin_num,abin_num,signal,func,signal,abin_num))
  #os.system("rm output/fit_mjj_Full_diphoton_{}_2018_{}_alpha{}.C ".format(func,signal,abin_num))
  #os.system("rm crudeFitPlot_diphoton_dijet_{}_alpha{}.png".format(signal,abin_num))
  #print("mv output/DijetFitResults_diphoton_{}_2018_{}_alpha{}.root output/alpha_{}/{}/DijetFitResults_DIPHOM_2018_{}_alpha{}.root ".format(func,signal, abin_num, abin_num,signal,signal,abin_num))
  #os.system("mv output/DijetFitResults_diphoton_{}_2018_{}_alpha{}.root output/alpha_{}/{}/DijetFitResults_DIPHOM_2018_{}_alpha{}.root ".format(func,signal, abin_num, abin_num,signal,signal,abin_num))
  #os.system("mv output/Plots_diphoton_{}_{}_alpha{}.root output/alpha_{}/{}/Plots_DIPHOM_alpha{}_{}.root ".format(func,signal,abin_num,abin_num,signal,abin_num,signal))

  print("EFF: {}".format(eff))
  lcommand = "python ../python/DiphotonCardMakerAlphaBinSingle_envelope.py -f DIPHOM_alpha{} -l {} -y {} -a {} -s {} -x {} --xsecsu {} --xsecsd {} -g {}".format(abin_num, LUMI, year, abin_num, signal, XS*eff, XS*eff_su, XS*eff_sd, GorI)
  print(lcommand)
  MakeFolder("output/combineCards")
  os.system(lcommand)

  #cname = "output/dijet_combine_gg_{}_alpha{}_lumi-13.700_2018_DIPHOM_alpha{}".format(signal,abin_num,abin_num)
  cname = "output/dijet_combine_gg_{}_alpha{}_lumi-137.000_2018_DIPHOM_alpha{}".format(signal,abin_num,abin_num)
  #ocname = "output/combineCards/CARD_multi_{}_alpha{}".format(signal,abin_num)
  #fpname = "{}/output/combineCards/CARD_multi_{}_alpha{}".format(os.getcwd(),signal,abin_num)
  ocname = "output/combineCards/dipho_combine_multipdf_lumi-137.00_RunII_{}_alphabin{}".format(signal,abin_num)
  fpname = "{}/output/combineCards/dipho_combine_multipdf_lumi-137.00_RunII_{}_alphabin{}".format(os.getcwd(),signal,abin_num)

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
