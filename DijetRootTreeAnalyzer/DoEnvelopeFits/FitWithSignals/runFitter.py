import os
import sys
import ROOT

def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

year = 2018
LUMI = 137 * 1000 

useAbin = False
myAbin=-999
if("abin" in sys.argv):
  useAbin=True
  myAbin = sys.argv[sys.argv.index("abin") + 1]

print(useAbin)
print(myAbin)

doFit=False
if("fit" in sys.argv or "Fit" in sys.argv):
  doFit=True

#XS = 0.001
XS = 0.00007

def getEff(s, d):
  effFile = "{}/{}.txt".format(d,s)
  with open(effFile) as f:
    eff = float(f.readline().rstrip())
  return eff

INT_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_fromInterpo/alphaBinning/"
DATA_dir = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/inputs/Shapes_DATA/alphaBinning/"

abins = range(0,9)
signalDict = {
  0:"X400A2",
  1:"X400A2",
  2:"X400A2",
  3:"X400A2",
  4:"X400A2",
  5:"X400A2",
  6:"X400A3p2",
  7:"X400A4",
  8:"X400A10",
}

abins = range(0,9)
signalDict = {
  0:["X400A2",  "X1200A6"],
  1:["X400A2",  "X1200A6"],
  2:["X400A2",  "X1200A6"],
  3:["X400A2",  "X1200A6"],
  4:["X400A2",  "X1200A6"],
  5:["X400A2",  "X1200A6"],
  6:["X400A3p2", "X1200A9p6"],
  7:["X400A4",  "X1200A9p6"],
  8:["X400A10", "X1200A30"],
}


def makeThisLimit(signalList, alphaBin):
  global year, LUMI
  signal = signalList[0]
  moresignals = ""
  for sig in signalList[1:]:
    moresignals += sig 
    moresignals += ","
  moresignals = moresignals[:-1]

  mydir = INT_dir + alphaBin + "/" + signal
  print("Reading from: ")
  print(mydir)
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

  sigX = float(signal[1 : signal.find("A")])
  sigPhi = float(signal[signal.find("A")+1:].replace("p","."))
  sigAlpha = sigPhi / sigX
  abin_num = alphaBin

  MakeFolder("output/")
  
  #GetSignal and efficiency
  #print("{}/{}.txt".format(mydir,signal))
  with open("{}/{}.txt".format(mydir,signal)) as f:
    eff = float(f.readline().rstrip())
    print("Signal Efficiency: {}".format(eff))


  print("\nFitter command: ")
  #mycommand = "python ../../python/BinnedDiphotonFit_withSignals.py -c ../../config/envelope2/diphoton_multi_alpha{}.config -y {} -l {} -b DIPHOM_alpha{} {}/PLOTS_{}.root -d output --fit-spectrum --write-fit --words test --sig {} --abin {} --lowA {} --hiA {} --extraSigs {}".format(abin_num,year,LUMI,abin_num,mydir,abin_num,signal,abin_num,la,ha,moresignals)
  #func='atlas'
  for func in ['dijet','atlas','moddijet','dipho','myexp']:
  #for func in ['dipho']:
    mycommand = "python ../../python/BinnedDiphotonFit_withSignals.py -c ../../config/ThreeParams/diphoton_{}.config -y {} -l {} -b diphoton_{} {}/PLOTS_{}.root -d output --fit-spectrum --write-fit True --words test --abin {} --lowA {} --hiA {} --sig {} --extraSigs {}".format(func,year,LUMI,func,mydir,abin_num,abin_num,la,ha, signal, moresignals)

    print(mycommand)
  
    os.system(mycommand)
  #os.system("rm output/*.root")
  os.system("rm output/*.C")
  #os.system("rm output/*.pdf")

  return

def DrawFromFit(abin, flist):
  print("Draw time")

  lstyles={
    "dijet":1,
    "atlas":2,
    "moddijet":7,
    "dipho":9,
    "myexp":10}
  lcolors={
    "dijet":2,
    "atlas":4,
    "moddijet":6,
    "dipho":8,
    "myexp":7}

  getFirstCanv=False

  aflist = {}
  for ff in flist:
    fname="output/alpha{}/Plots_diphoton_{}_X400A2_alpha{}.root".format(abin, ff, abin)
    print(fname)
    F = ROOT.TFile(fname,"r")
    canv = F.Get("output/c")
    if(getFirstCanv==False):
      fullcanv = canv.Clone()
      getFirstCanv=True
      continue
    else:
      canv1 = canv.GetPrimitive("c_1")
      for cc in canv1.GetListOfPrimitives():
        print("Name: ", cc.GetName())
        if(cc.GetName()=="h_th1x__th1x_mjj"):
          aflist[ff] = cc.Clone("h_th1_{}".format(ff))
          break

  print("List: ")
  print(aflist)
  print("\n")
  fullcanv.Draw()
  fullcanv.cd()
  for (fc, gr) in aflist.items():
    gr.SetLineStyle(lstyles[fc])
    #gr.SetLineColor(lcolors[fc])
    gr.SetLineColor(ROOT.kBlue)
    gr.SetLineWidth(2)
    gr.SetStats(0)
    
    gr.Draw("same")

  fullcanv.Print("tmp.png")
  return

for (abin, slist) in signalDict.items():
  if(useAbin==True and abin != int(myAbin)): 
    continue
  print("Do Alpha Bin {}".format(abin))
  if(doFit):
    print("Starting Fitter")
    makeThisLimit(slist, str(abin))
    MakeFolder("output/alpha{}".format(abin))
    print("Moving output to output/alpha{}".format(abin))
    os.system("mv output/*alpha{}* output/alpha{}/.".format(abin,abin))
    os.system("rm output/*")

  #drawFuncList = ["dijet","atlas","moddijet","dipho","myexp"]
  #drawFuncList = ["dijet"]
  #drawFuncList = ["dijet","atlas"]
  #DrawFromFit(abin, drawFuncList)


