import os
import sys
import ROOT
import FTest

ROOT.gROOT.SetBatch()

sNparams = [("Three",3),("Four",4),("Five",5),("Six",6)]

BD = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/DoAlphaFits/saveOutput/"

anum=1

anums = range(0,16)
functions = ["dijet","atlas","dipho","moddijet"]
#functions=["moddijet"]

pValue = 0.05
bestFits = []

if("append" in sys.argv):
  saveFile = open("FTestResults.txt","a")
else:
  saveFile = open("FTestResults.txt","w")

for anum in anums:
  #if(anum != 2): continue
  #if(anum > 1): break
  for function in functions:
    found=False

    for ii in range(len(sNparams)-1):
      (S,NL) = sNparams[ii]
      (SP,NH) = sNparams[ii+1]

      if(function=="moddijet" and SP=="Six"): break

      folder = BD + S + "Params/combineCards/"
      for ff in os.listdir(folder):
        if (ff.endswith(".txt") and "X600" in ff and "alpha{}_".format(anum) in ff and "_{}".format(function) in ff):
          cardL = os.path.join(folder,ff)

      folderP = BD + SP + "Params/combineCards/"
      print(folderP)
      for ff in os.listdir(folderP):
        if (ff.endswith(".txt") and "X600" in ff and "alpha{}_".format(anum) in ff and "_{}".format(function) in ff):
          cardH = os.path.join(folderP,ff)

      print("Using These Two Cards: ")
      print(cardH)
      print(cardL)
      print("\n")

      #c21 = FTest.DoFTest(cardH, NH, cardL, NL, function)
      try: 
        c21 = FTest.DoFTest(cardH, NH, cardL, NL, function)
      except AttributeError:
        print("FIT FAILED, Moving on")
        if(NH==6):
          saveFile.write("{},{},999,999".format(anum,function))
        continue
      os.system("mv FTest.png FTestPlots/FTest_alpha{}_{}_{}{}.png".format(anum, function, NH, NL))

      if(c21 > pValue or NH==6):
        bestFits.append((anum, function, c21, NL))
        saveFile.write("{},{},{},{}\n".format(anum,function,c21,NL))
        Found=True
        break

print(bestFits)
saveFile.close()

