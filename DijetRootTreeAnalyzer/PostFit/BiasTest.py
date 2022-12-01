import ROOT
from ROOT import *
import numpy
import math
import sys
import array
import os

gROOT.SetBatch()

def getAlphaSlices(card):
  cc = open(card, "r")
  anums = []
  for lin in cc.readlines():
    if('discrete' not in lin): continue
    ls = lin.replace("\t"," ")
    ls = ls.split(" ")
    anum = ls[0]
    anum = int(anum[anum.rfind("a")+1 : ])
    anums.append(anum)
  cc.close()
  return anums

infile = sys.argv[1]
print(infile)
cps = infile[infile.rfind("/"):]
cps = cps.split("_")
an = "alphaAll"


for c in cps:
  if(c.startswith("X")):
    mm = c
    break

if(mm.endswith(".txt")):
  mm = mm[0:mm.rfind(".")]

#mm = cps[0][1:]
print(an, mm)
anum = an

comName = "_{}_{}".format(an,mm)

#PT.PlotTogether(infile, False)

newDir = "combineOutputEnvelope/{}".format(mm)
if(not os.path.exists(newDir)):
  os.system("mkdir -p {}".format(newDir))

dfname = "{}/meaninfo_{}.csv".format(newDir,mm)
if(not os.path.exists(dfname)):
  af = open(dfname,"w")
else: af=open(dfname, "a")
#PT.PlotTogether(infile, False)

os.system("combine "+sys.argv[1]+" -M Significance --name {}".format(comName))
os.system("combine "+sys.argv[1]+" -M AsymptoticLimits --name {}".format(comName))
F = ROOT.TFile("higgsCombine{}.AsymptoticLimits.mH120.root".format(comName))
T = F.Get("limit")
T.GetEntry(2)
exp = T.limit
T.GetEntry(4)
p2 = T.limit - exp
Lc = [0., exp, exp+p2]
Ln = ["null", "exp", "sig2"]
os.system("combine "+sys.argv[1]+" -M FitDiagnostics --saveShapes --saveWithUncertainties --name {}".format(comName))

#Lc = [0.]
#Ln = ["null"]
print Lc

ntoys=500

aslices = getAlphaSlices(sys.argv[1])
print(aslices)


for i,j in zip(Lc,Ln):
  print(i,j)
  for pdfi in [0,1,2,3,4]:
  #for pdfi in [0,1]:
  #for pdfi in [2,3,4]:
    if(len(aslices)==1):
      fpstring = "--freezeParameters pdf_index_DIPHOM_alpha%i --setParameters pdf_index_DIPHOM_alpha%i=%s"%(aslices[0],aslices[0],pdfi)
    else:
      fstring = " --freezeParameters "
      setstring = " --setParameters "
      for asl in aslices:
        fstring += "pdf_index_DIPHOM_alpha%i,"%(asl)
        setstring += "pdf_index_DIPHOM_alpha%i=%s,"%(asl,pdfi)
      fstring = fstring[:-1]
      setstring = setstring[:-1]
      fpstring = fstring + setstring
    #fpstring = "--freezeParameters pdf_index_DIPHOM_alpha12,pdf_index_DIPHOM_alpha13 --setParameters pdf_index_DIPHOM_alpha12=%s,pdf_index_DIPHOM_alpha13=%s "%(pdfi,pdf    i)
    print(fpstring)
    os.system("combine "+sys.argv[1]+" -M GenerateOnly -t %i --saveToys --toysFrequentist  --expectSignal %s -n _%s%s --bypassFrequentistFit %s"% (ntoys, i, j, comName, fpstring))
    os.system("combine "+sys.argv[1]+" -M FitDiagnostics --cminDefaultMinimizerStrategy=0 --skipBOnlyFit -t %i --toysFile higgsCombine_%s%s.GenerateOnly.mH120.123456.root --rMin -10 --rMax 10 --saveWorkspace -n _%s%s --bypassFrequentistFit "%(ntoys, j,comName,j,comName))

#####

  #Works on individual card
  #os.system("combine "+sys.argv[1]+" -M GenerateOnly -t 100 --saveToys --toysFrequentist  --expectSignal "+str(i)+" -n _{}{} --bypassFrequentistFit ".format(j,comName))
  #os.system("combine "+sys.argv[1]+" -M FitDiagnostics --bypassFrequentistFit --skipBOnlyFit -t 100 --toysFile higgsCombine_{}{}.GenerateOnly.mH120.123456.root --rMin -10 --rMax 10 --saveWorkspace -n_{}{} --cminDefaultMinimizerStrategy=0 ".format(j,comName,j,comName))

####

    F = ROOT.TFile("fitDiagnostics_{}{}.root".format(j,comName))
    T = F.Get("tree_fit_sb")
    H = ROOT.TH1F("Bias Test, injected r="+j, ";(#mu_{measured} - #mu_{injected})/#sigma_{#mu};toys", 50, -5., 5.)
    #T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test, injected r=" + j)
    #T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test, injected r=" + j)
    #T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test, injected r=" + j, "fit_status>0")
    #T.Draw("(r-%f)/((rHiErr*(r-%f<0)+rLoErr*(r-%f>0)))"%(i,i,i)+">>Bias Test, injected r=" + j, "fit_status>0")
    T.Draw("(r-%f)/((rHiErr*(r-%f<0)+rLoErr*(r-%f>0)))"%(i,i,i)+">>Bias Test, injected r=" + j, "fit_status>=0")
    #T.Draw("(r)/((rHiErr*(r<0)+rLoErr*(r>0)))>>Bias Test, injected r=" + j, "fit_status>0")
    G = ROOT.TF1("f", "gaus(0)", -5.,5.)
    H.Fit(G)
    ROOT.gStyle.SetOptFit(1111)
    cbb = ROOT.TCanvas()
    cbb.cd()
    H.Draw("e0")
    sname = newDir+"/"+j+"_{}_{}_pdf{}".format(an,mm,pdfi)
    cbb.Print("{}.png".format(sname))
    cbb.Print("{}.root".format(sname))
    print("Saving as: {}".format(sname))
    os.system("rm higgsCombine*{}*.root".format(comName))
    os.system("mv fitDiagnostics_{}{}.root {}/fitDiagnostics{}_{}_pdf{}.root".format(j,comName,newDir,comName,j,pdfi))

    gmean = G.GetParameter("Mean")
    gsig = G.GetParameter("Sigma")
    
    af.write("{},{},{},{}\n".format(j,pdfi,gmean,gsig))

af.close()

#os.system("mv *.png {}/.".format(newDir))
