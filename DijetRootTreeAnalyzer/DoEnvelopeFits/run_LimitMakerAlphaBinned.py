import os
import sys

clean=False
goLim = False
fast=False
doInterpo = False
fnum=999

#xmasslist = ['600','400','500','300','750','1000','1500','2000']
#xmasslist = ['600','400','500','200','300','750','1000','1500','2000','3000']
xmasslist = ['600']

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
    data_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/"
    GorI="int"
  else:
    data_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning/"
    GorI="gen"
  dirs = []

  for dd in os.listdir(data_dir):
    if(dd=="ALL"): continue
    if(dd.startswith("cuts")): continue
    try:
      anum = int(dd)
    except ValueError:
      continue
    if(fast and anum!=fnum): continue
    for xx in os.listdir(os.path.join(data_dir,dd)):
      if("X{}A".format(xmass) in xx):
        if(os.path.exists("{}{}/{}/PLOTS_{}.root".format(data_dir,dd,xx,anum))):
          fracFile = open("{}/{}/{}/alphaFraction_alpha{}_{}.txt".format(data_dir, anum,xx,anum,xx), "r")
          frac = float(fracFile.readline())
          #if(frac < 0.1) : continue
          fracFile.close()
          sig=xx
          rangeFile = open("{}{}/{}/arange.txt".format(data_dir,dd,sig),"r")
          rr = rangeFile.readline().rstrip()
          la = float(rr.split(",")[0])
          ha = float(rr.split(",")[-1])
          dirs.append(("{}{}/{}".format(data_dir,dd,sig), anum,la,ha))

  if(goLim): MakeFolder("combineOutput")

  for (dd,anum,la,ha) in dirs:
    sig = dd.split("/")[-1]
    sigX = float(sig[1 : sig.find("A")])
    sigPhi = float(sig[sig.find("A")+1:].replace("p","."))
    sigAlpha = sigPhi / sigX
    abin_num = dd.split("/")[-2]

    #if(sig != "X600A18"): continue
    if(sig != "X600A3"): continue
    #if(sigAlpha != 0.005): continue
    if(anum != 4): continue

    print("Starting {} Signal, alpha bin {}" .format(sig, abin_num))
    MakeFolder("output/alpha_{}/{}".format(abin_num,sig))
    os.system("cp {}/{}/{}/arange.txt output/alpha_{}/{}/.".format(data_dir,abin_num,sig,abin_num,sig))
    
    #if(os.path.exists("output/combineCards/CARD_multi_{}_alpha{}.txt".format(sig,abin_num))):
    #  print(abin_num, sig)
    #  print("Already done, moving on. ")
    #  continue


    #GetSignal and efficiency
    for fil in os.listdir(dd):
      if(fil.startswith("X") and fil.endswith(".txt")):
        with open(os.path.join(dd,fil)) as f:
          eff = float(f.readline().rstrip())
          print(eff)

    mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/envelope2/diphoton_multi_alpha{}.config -y {} -l {} -b DIPHOM_alpha{} {}/PLOTS_{}.root -d output --fit-spectrum --write-fit --words test --sig {} --abin {} --lowA {} --hiA {}".format(abin_num,year,LUMI,abin_num,dd,abin_num,sig,abin_num,la,ha)
    print(mycommand)
    #continue

    os.system(mycommand)
    os.system("mv output/fit_mjj_Full_DIPHOM_alpha{}_2018_{}_alpha{}.png output/alpha_{}/{}/fit_mjj_Full_diphoton_{}_{}.png ".format(abin_num,sig,abin_num,abin_num,sig,sig,abin_num))
    os.system("rm output/fit_mjj_Full_DIPHOM_alpha{}_2018_{}_alpha{}.C ".format(abin_num,sig,abin_num))
    os.system("rm crudeFitPlot_DIPHOM_alpha{}_{}_alpha{}.png".format(abin_num,sig,abin_num))
    os.system("mv output/DijetFitResults_DIPHOM_alpha{}_2018_{}_alpha{}.root output/alpha_{}/{}/DijetFitResults_DIPHOM_2018_{}_alpha{}.root ".format(abin_num,sig,abin_num,abin_num,sig,sig,abin_num))
    os.system("mv output/Plots_DIPHOM_alpha{}_{}_alpha{}.root output/alpha_{}/{}/Plots_DIPHOM_alpha{}_{}.root ".format(abin_num,sig,abin_num,abin_num,sig,abin_num,sig))
    if clean:
      os.system("mv output/*.* output/alpha_{}/{}/.".format(abin_num,sig))

    lcommand = "python ../python/DiphotonCardMakerAlphaBinSingle_envelope.py -f DIPHOM_alpha{} -l {} -y {} -a {} -s {} -x {} -g {}".format(abin_num, LUMI, year, abin_num, sig, XS*eff, GorI)
    print(lcommand)
    MakeFolder("output/combineCards")
    os.system(lcommand)

    cname = "output/dijet_combine_gg_{}_alpha{}_lumi-13.700_2018_DIPHOM_alpha{}".format(sig,abin_num,abin_num)
    #ocname = "output/combineCards/CARD_multi_{}_alpha{}".format(sig,abin_num)
    #fpname = "{}/output/combineCards/CARD_multi_{}_alpha{}".format(os.getcwd(),sig,abin_num)
    ocname = "output/combineCards/dipho_combine_multipdf_lumi-13.700_RunII_{}_alphabin{}".format(sig,abin_num)
    fpname = "{}/output/combineCards/dipho_combine_multipdf_lumi-13.700_RunII_{}_alphabin{}".format(os.getcwd(),sig,abin_num)

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

    print(goLim)
    if goLim:
      for of in os.listdir("output/combineCards"):
        if( os.path.join("output/combineCards",of)=="{}.txt".format(ocname)):
          comb_command = "combine {} -M AsymptoticLimits -n _alpha{}_{}".format(os.path.join("output/combineCards",of), abin_num, sig)
          print(comb_command)
          os.system(comb_command)
          os.system("mv higgsCombine_alpha{}_{}.AsymptoticLimits.mH120.root combineOutput/higgsCombine_envelope_alpha{}_{}.root".format(abin_num,sig,abin_num,sig))

#if(doInterpo):
#  print("Using interpolated shapes")
#  i_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning"
#  xmlist = []
#  for xa in os.listdir(i_dir):
#    print(xa)
#    xm = int(xa[1 : xa.find("A")])
#    xmlist.append(xm)
#  
#  for xm in xmlist:
#    makeThisLimit(xm)
#
#else:
#  #xmasslist=[xmasslist[0]]
#  #xmasslist=["400"]
#  for xm in xmasslist:
#    print("\nStarting X Mass {}\n".format(xm))
#    makeThisLimit(xm)

for xm in xmasslist:
  print("\nStarting X Mass {}\n".format(xm))
  makeThisLimit(xm)
