import os
import sys
import ROOT
import FTest

ROOT.gROOT.SetBatch()

sNparams = [("Three",3),("Four",4),("Five",5),("Six",6)]
#sNparams = [("Three",3),("Four",4)]

BD = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/DoEnvelopeFits/saveOutput/Unblind/FTest/"

anum=1

anums = range(0,9)
#anums=[3]
functions = ["dijet","atlas","dipho","moddijet"]
#functions=["dijet","atlas"]

pValue = 0.05

if("append" in sys.argv):
  saveFile = open("FTestResults.txt","a")
else:
  saveFile = open("FTestResults.txt","w")

for function in functions:
  for anum in anums:
    #if(anum != 0): continue
    c21=0

    for ii in range(len(sNparams)-1):
      (S,NL) = sNparams[ii]
      (SP,NH) = sNparams[ii+1]

      if(function=="moddijet" and SP=="Six"): break

      folder = BD + function + "/" + S + "Params/combineCards/"
      for cc in os.listdir(folder):
        if(cc.endswith("alphabin{}.txt".format(anum))):
          cardL = os.path.join(folder,cc)
          break

      folder = BD + function + "/" + SP + "Params/combineCards/"
      for cc in os.listdir(folder):
        if(cc.endswith("alphabin{}.txt".format(anum))):
          cardH = os.path.join(folder,cc)
          break

      print("Using These Two Cards: ")
      print(cardL)
      print(cardH)
      print("\n")

      #c21 = FTest.DoFTest(cardH, NH, cardL, NL, function)
      c21_prev = c21
      try: 
        c21 = FTest.DoFTest(cardH, NH, cardL, NL, function)
      except AttributeError:
        print("FIT FAILED, Moving on")
        if(NH==6):
          saveFile.write("{},{},999,999,0\n".format(anum,function))
        continue
      os.system("mv FTest.png FTestPlots/FTest_alpha{}_{}_{}{}.png".format(anum, function, NH, NL))

      if(c21 > pValue or NH==6):
        saveFile.write("{},{},{},{},{}\n".format(anum,function,c21,NL,c21_prev))
        Found=True
        break

saveFile.close()

