import os
import sys

clean=False
goLim = False
fast=False
doInterpo = False
fnum=999

#xmasslist = ['600','400','500','300','750','1000','1500','2000']
#xmasslist = ['600','400','500','200','300','750','1000','1500','2000','3000']
xmasslist = ['400']

year = 2018
LUMI = 13.7 * 1000  #provide lumi in PB
XS = 0.001

#To run test on one alpha bin, add fast# to command line arg
for arg in sys.argv:
  if 'fast' in arg:
    fnum = int(arg[4:])
    fast=True
    print("Only doing alpha bin {}".format(fnum))

if ('clean' in sys.argv): clean=True
if ('limit' in sys.argv): goLim = True
if ('Interpo' in sys.argv): doInterpo = True

if clean:
  print("Deleting ALL output files")
  os.system('rm -rf output')
  os.system("mkdir output")

if clean and goLim:
  print("Deleting all combine output")
  os.system("rm -rf combineOutput")
  os.system("mkdir combineOutput")

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)


def getEff(s, d):
  effFile = "{}/{}.txt".format(d,s)
  with open(effFile) as f:
    eff = float(f.readline().rstrip())
  return eff


def makeThisLimit(xmass):
  global year, LUMI

  if(doInterpo):
    data_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/OneBigBin"
  else:
    data_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/OneBigBin/"
  dirs = []

  for xx in os.listdir(data_dir):
    if(os.path.exists("{}{}/PLOTS_0.root".format(data_dir,xx))):
      sig=xx
      la,ha = 0.0, 0.03
      dirs.append(("{}{}".format(data_dir,sig),0,la,ha))

  if(goLim): MakeFolder("combineOutput")

  for (dd,anum,la,ha) in dirs:
    #if(anum != 3 and anum != 4): continue
    sig = dd.split("/")[-1]
    sigX = float(sig[1 : sig.find("A")])
    sigPhi = float(sig[sig.find("A")+1:].replace("p","."))
    sigAlpha = sigPhi / sigX
    abin_num = 0

    #if(sig != "X1000A10"): continue

    print("Starting {} Signal, alpha bin {}" .format(sig, abin_num))
    #MakeFolder("output/alpha_{}/{}".format(abin_num,sig))
    
    if(os.path.exists("output/combineCards/CARD_multi_{}_alpha{}.txt".format(sig,abin_num))):
      print(abin_num, sig)
      print("Already done, moving on. ")
      continue

    #GetSignal and efficiency
    for fil in os.listdir(dd):
      if(fil.startswith("X") and fil.endswith(".txt")):
        with open(os.path.join(dd,fil)) as f:
          eff = float(f.readline().rstrip())
          print(eff)

    """
    mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/envelope2/diphoton_multi_alpha0.config -y {} -l {} -b DIPHOM_alpha0 {}/PLOTS_0.root -d output --fit-spectrum --write-fit --words test --sig {} --abin 0 --lowA {} --hiA {}".format(year,LUMI,dd,sig,la,ha)
    print(mycommand)

    os.system(mycommand)
    os.system("mv output/fit_mjj_Full_DIPHOM_alpha{}_2018_{}_alpha{}.png output/alpha_{}/{}/fit_mjj_Full_diphoton_{}_{}.png ".format(abin_num,sig,abin_num,abin_num,sig,sig,abin_num))
    os.system("rm output/fit_mjj_Full_DIPHOM_alpha{}_2018_{}_alpha{}.C ".format(abin_num,sig,abin_num))
    os.system("rm crudeFitPlot_DIPHOM_alpha{}_{}_alpha{}.png".format(abin_num,sig,abin_num))
    os.system("mv output/DijetFitResults_DIPHOM_alpha{}_2018_{}_alpha{}.root output/alpha_{}/{}/DijetFitResults_DIPHOM_2018_{}_alpha{}.root ".format(abin_num,sig,abin_num,abin_num,sig,sig,abin_num))
    os.system("mv output/Plots_DIPHOM_alpha{}_{}_alpha{}.root output/alpha_{}/{}/Plots_DIPHOM_alpha{}_{}.root ".format(abin_num,sig,abin_num,abin_num,sig,abin_num,sig))
    if clean:
      os.system("mv output/*.* output/alpha_{}/{}/.".format(abin_num,sig))

    lcommand = "python ../python/DiphotonCardMakerAlphaBinSingle_envelope.py -f DIPHOM_alpha{} -l {} -y {} -a ALL -s {} -x {}".format(abin_num, LUMI, year, sig, XS*eff)
    print(lcommand)
    MakeFolder("output/combineCards")
    os.system(lcommand)

    cname = "output/dijet_combine_gg_{}_alphaALL_lumi-13.700_2018_DIPHOM_alpha0".format(sig)
    ocname = "output/combineCards/CARD_multi_{}".format(sig)
    fpname = "{}/output/combineCards/CARD_multi_{}".format(os.getcwd(),sig)

    print("Opening {}.txt".format(cname))

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
      continue

    os.system("rm stuff*")
    os.system("rm output/corr*")
    """

  print(goLim)
  if goLim:
    for of in os.listdir("saveOutput/OneBigBin/combineCards"):
      if(of.endswith(".root")): continue
      nsig = of[of.find("X") : of.find(".txt")]
      comb_command = "combine {} -M AsymptoticLimits -n _alpha{}_{}".format(os.path.join("saveOutput/OneBigBin/combineCards",of), abin_num, nsig)
      print(comb_command)
      os.system(comb_command)
      os.system("mv higgsCombine_alpha{}_{}.AsymptoticLimits.mH120.root combineOutput/higgsCombine_envelope_alpha{}_{}.root".format(abin_num,nsig,abin_num,nsig))

if(doInterpo):
  print("Using interpolated shapes")
  i_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning"
  xmlist = []
  for xa in os.listdir(i_dir):
    xm = int(xa[1 : xa.find("A")])
    xmlist.append(xm)
  
  for xm in xmlist:
    makeThisLimit(xm)

else:
  #xmasslist=[xmasslist[0]]
  #xmasslist=["400"]
  for xm in xmasslist:
    print("\nStarting X Mass {}\n".format(xm))
    makeThisLimit(xm)
