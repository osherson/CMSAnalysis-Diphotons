import os
import sys
import ROOT
import FTest

ROOT.gROOT.SetBatch()

sNparams = [("Three",3),("Four",4),("Five",5),("Six",6)]

BD = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/DoAlphaFits/saveOutput/"

anum=1
function="dijet"

pValue = 0.05
bestFits = []

for ii in range(len(sNparams)-1):
  (S,NL) = sNparams[ii]
  (SP,NH) = sNparams[ii+1]

  folder = BD + S + "Params/combineCards/"
  for ff in os.listdir(folder):
    if (ff.endswith(".txt") and "X600" in ff and "alpha{}_".format(anum) in ff and "_{}".format(function) in ff):
      cardL = os.path.join(folder,ff)

  folderP = BD + SP + "Params/combineCards/"
  for ff in os.listdir(folderP):
    if (ff.endswith(".txt") and "X600" in ff and "alpha{}_".format(anum) in ff and "_{}".format(function) in ff):
      cardH = os.path.join(folderP,ff)

  c21 = FTest.DoFTest(cardH, NH, cardL, NL)
  os.system("mv FTest.png FTestPlots/FTest_alpha{}_{}_{}{}.png".format(anum, function, NH, NL))

  if(c21 > pValue):
    bestFits.append((anum, function, NL))
    break

print(bestFits)

#CH = "SixParams/combineCards/CARD_alpha1_X600A3_dijet.txt"
#nH=6
#CL = "/cms/sclark/DiphotonAnalysis/CMSSW_11_1_0_pre7/src/CMSAnalysis-Diphotons/DijetRootTreeAnalyzer/DoAlphaFits/saveOutput/FiveParams/combineCards/CARD_alpha1_X600A3_dijet.txt"
#nL = 5

#FTest.DoFTest(CH,nH,CL,nL)
