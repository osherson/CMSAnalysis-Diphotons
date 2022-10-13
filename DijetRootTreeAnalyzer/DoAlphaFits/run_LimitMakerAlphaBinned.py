import os
import sys

clean=False
goLim = False
DoInterpo = False

xmasslist = ['400','600','1000','300','500','750','1500','2000','3000']
xmasslist = ['600']

if ("Interpo" in sys.argv):
  DoInterpo = True

if ('clean' in sys.argv):
  clean=True

if ('limit' in sys.argv):
  goLim = True

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

year = 2018
LUMI = 13.7 * 1000
XS = 0.001 #pb

def getEff(s, d):
  effFile = "{}/{}.txt".format(d,s)
  with open(effFile) as f:
    eff = float(f.readline().rstrip())
  return eff


def makeThisLimit(xmass):
  global year, LUMI

  print("\n")
  print("_______________________________________________")
  print("STARTING X MASS {}".format(xmass))

  if(DoInterpo):
    data_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/"
  else:
    data_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromGen/alphaBinning/"
  dirs = []

  for dd in os.listdir(data_dir):
    if(dd=="ALL"): continue
    anum = int(dd)
    #if(anum == 0): continue
    for xx in os.listdir(os.path.join(data_dir,dd)):
      if("X{}A".format(xmass) in xx and os.path.exists("{}{}/{}/PLOTS_{}.root".format(data_dir,dd,xx,anum))):
        sig=xx
        rangeFile = open("{}{}/{}/arange.txt".format(data_dir,dd,sig),"r")
        rr = rangeFile.readline().rstrip()
        la = float(rr.split(",")[0])
        ha = float(rr.split(",")[-1])
        dirs.append(("{}{}/{}".format(data_dir,dd,sig), anum,la,ha))

    MakeFolder("output/alpha_{}/{}".format(anum,sig))
    if(goLim): MakeFolder("combineOutput/alpha_{}/{}/".format(anum,sig))
    #os.system("cp {}{}/{}/arange.txt output/alpha_{}/{}/.".format(data_dir,dd,sig,anum,sig))

  fitfuncs = ["dijet","moddijet","atlas","dipho","myexp"] #FourParams
  #fitfuncs = ["dijet","moddijet","atlas","dipho"] #Five and Three
  #fitfuncs = ["dijet","atlas","dipho"] #Six

  for (dd,anum,la,ha) in dirs:
    sig = dd.split("/")[-1]
    #if(sig != "X400A2"):continue
    #abin_num = int(dd.split("/")[-2])
    abin_num = anum
    MakeFolder("output/alpha_{}/{}".format(anum,sig))
    print("Starting {} Signal, alpha bin {}" .format(sig, abin_num))

    #GetSignal and efficiency
    for fil in os.listdir(dd):
      if(fil.startswith("X") and fil.endswith(".txt")):
        with open(os.path.join(dd,fil)) as f:
          eff = float(f.readline().rstrip())
          print(eff)

    for ff in fitfuncs:
      if(os.path.exists("output/combineCards/CARD_alpha{}_{}_{}.txt".format(abin_num,sig,ff))):
        print(abin_num, sig, ff)
        print("Already done, moving on. ")
        continue

      mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/diphoton_{}.config -y {} -l {} -b diphoton_{} {}/PLOTS_{}.root -d output --fit-spectrum --write-fit --words test --sig {} --abin {} --lowA {} --hiA {}".format(ff,year,LUMI,ff,dd,abin_num,sig,abin_num,la,ha)
      print(mycommand)
      os.system(mycommand)
      os.system("mv output/fit_mjj_Full_diphoton_{}_2018_{}_alpha{}.png output/alpha_{}/{}/fit_mjj_Full_diphoton_{}_{}_{}.png ".format(ff,sig,abin_num,abin_num,sig,sig,ff,abin_num))
      os.system("rm output/fit_mjj_Full_diphoton_{}_2018_{}_alpha{}.C".format(ff,sig,abin_num))
      os.system("rm crudeFitPlot_diphoton_{}_{}_alpha{}.png".format(ff,sig,abin_num))
      os.system("mv output/DijetFitResults_diphoton_{}_2018_{}_alpha{}.root output/alpha_{}/{}/DijetFitResults_diphoton_{}_{}_alpha{}.root ".format(ff,sig,abin_num,abin_num,sig,sig,ff,abin_num))
      if clean:
        os.system("mv output/*.* output/alpha_{}/{}/.".format(abin_num,sig))

      lcommand = "python ../python/DiphotonCardMakerAlphaBinSingle_envelope.py -f {} -l {} -y {} -a {} -s {} -x {}".format(ff,LUMI, year, abin_num, sig, XS*eff)
      print(lcommand)
      MakeFolder("output/combineCards")
      os.system(lcommand)
      cname = "output/dijet_combine_gg_{}_alpha{}_lumi-13.700_2018_diphoton_{}".format(sig,abin_num,ff)
      ocname = "output/combineCards/CARD_alpha{}_{}_{}".format(abin_num,sig,ff)
      fpname = "{}/output/combineCards/CARD_alpha{}_{}_{}".format(os.getcwd(),abin_num,sig,ff)

      try:
        with open('{}.txt'.format(cname), 'r') as input_file, open('{}.txt'.format(ocname), 'w') as output_file:
          print("File successfully opened")
          for line in input_file:
            if line.startswith('shapes') and cname in line:
              output_file.write(line.replace(cname,fpname))
            else:
              output_file.write(line)

        os.system("mv {}.root {}.root".format(cname, ocname))
        os.system("rm {}.txt ".format(cname))

      except IOError:
        print("Something broke, moving on")
    
      #os.system("rm crude*")
      #os.system("rm stuff*")
      #os.system("rm output/corr*")

      if goLim:
        for of in os.listdir("output/alpha_{}".format(abin_num)):
          if( of.endswith(".root") and "dijet_combine" in of and ff in of):
            comb_command = "combine output/alpha_{}/{} -M AsymptoticLimits -n _{}_{}".format(abin_num, of, year,sig)
            print(comb_command)
            os.system(comb_command)
            os.system("mv higgsCombine_{}_{}.AsymptoticLimits.mH120.root combineOutput/alpha_{}/higgsCombine_{}_{}.root".format(year,sig,abin_num,ff,sig))


if(DoInterpo):
  print("Using interpolated shapes")
  #i_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/"
  i_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/unBinned/"
  xmlist = []
  for xa in os.listdir(i_dir):
    xm = int(xa[1 : xa.find("A")])
    if(xm != 600): continue
    xmlist.append(xm)

  for xm in xmlist:
    makeThisLimit(xm)

else:
  for xm in xmasslist:
    makeThisLimit(xm)
