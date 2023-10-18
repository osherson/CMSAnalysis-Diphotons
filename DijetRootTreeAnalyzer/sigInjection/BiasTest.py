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
    print(anum)
    anums.append(anum)
  cc.close()
  return anums

infile = sys.argv[1]
print(infile)
usefunction = sys.argv[2]
cps = infile[infile.rfind("/"):]
cps = cps.split("_")
an = "alphaAll"

for c in cps:
  if(c.startswith("/")): c=c[1:]
  if(c.startswith("X")):
    mm = c
    break

if(mm.endswith(".txt")):
  mm = mm[0:mm.rfind(".")]

#mm = cps[0][1:]
print(an, mm)
xmass = int(mm[1 : mm.find("A")])
amass = float(mm[mm.find("A") + 1 :].replace("p","."))
print(xmass, amass)
anum = an

#comName = "_new_{}_{}".format(an,mm)
#comFuncName = "_new_{}_{}_pdf{}".format(an,mm,usefunction)
comName = "_exp_{}_{}".format(an,mm)
comFuncName = "_exp_{}_{}_pdf{}".format(an,mm,usefunction)
print(comFuncName)

#PT.PlotTogether(infile, False)

#newDir = "combineOutputEnvelope/{}/".format(mm)
#newDir = "noDijet/{}/".format(mm)
newDir = "newSetParams/{}/".format(mm)
#newDir = "output100/{}/".format(mm)
if(not os.path.exists(newDir)):
  os.system("mkdir -p {}".format(newDir))

#PT.PlotTogether(infile, False)

os.system("combine "+sys.argv[1]+" -M Significance --name {}".format(comFuncName))
os.system("combine "+sys.argv[1]+" -M AsymptoticLimits --name {}".format(comFuncName))

F = ROOT.TFile("higgsCombine{}.AsymptoticLimits.mH120.root".format(comFuncName))
T = F.Get("limit")
T.GetEntry(2)
exp = T.limit
T.GetEntry(4)
p2 = T.limit - exp
Lc = [0., exp, exp+p2]
Ln = ["null", "exp", "sig2"]

#Lc = [exp, exp+p2]
#Ln = ["exp", "sig2"]

#Lc = [0.]
#Ln = ["null"]

Lc = [exp]
Ln = ["exp"]

#Lc = [exp+p2]
#Ln = ["sig2"]
#os.system("combine "+sys.argv[1]+" -M FitDiagnostics --cminDefaultMinimizerStrategy=0 --saveShapes --saveWithUncertainties --name {}".format(comFuncName))

print Lc
print Ln

#ntoys=1000
#ntoys=1
ntoys=500
aslices = getAlphaSlices(sys.argv[1])
print("A slices:")
print(aslices)

"""
For sig2: 
If alpha = 0.025, rmin=0, rmax=10
If X300A1p5 (alpha=0.005, Mx = 300 only) rmin=0, rmax=20

"""

def getExpPM(xx,aa):
  print(xx,aa)
  alpha = round(aa/xx,3)
  print(alpha)
  for line in open("../DoEnvelopeFits/allAlphaLimitMaker/LimitCSV/limits.csv","r").readlines():
    sl = line.split(",")
    #if(int(float(sl[0]))==xx and float(sl[1])==alpha):
    if(int(float(sl[0]))==xx and float(sl[1])==alpha):
        exp = float(sl[4])
        p1 = float(sl[5])
        m1 = float(sl[6])
        p2 = float(sl[7])
        m2 = float(sl[8])
        return [exp,p1,m1,p2,m2]

  print("NEVER GOT IT")

  return 


expvals = getExpPM(xmass, amass)
print(expvals)
#rmin = expvals[-1] #Expected - 2sigma
#rmax = expvals[-2] #Expected + 2sigma

#For x=300
if(xmass < 500):
  rmin = -1*expvals[3]
  #rmax = expvals[3]
  rmax = max(expvals[3],2*Lc[0])

else: 
  rmin=0
  #rmax = expvals[3]
  rmax = max(expvals[3],2*Lc[0])

print("Exp r: {}".format(expvals[0]))
print("rmin = {}".format(rmin))
print("rmax = {}".format(rmax))

def getPNames(func):
  pnames = {
    0:",p1_DIPHOM_alphaNUM=VAL1,p2_DIPHOM_alphaNUM=VAL2",
    1:",pa1_DIPHOM_alphaNUM=VAL1,pa2_DIPHOM_alphaNUM=VAL2",
    2:",pmd1_DIPHOM_alphaNUM=VAL1,pmd2_DIPHOM_alphaNUM=VAL2",
    3:",pdp1_DIPHOM_alphaNUM=VAL1,pdp2_DIPHOM_alphaNUM=VAL2",
    4:",pmyx1_DIPHOM_alphaNUM=VAL1,pmyx2_DIPHOM_alphaNUM=VAL2,pmyx3_DIPHOM_alphaNUM=VAL3"
  }
  return pnames[func]

def getOneBinSetParams(func, onebin):
  fnmap = {
    0:"dijet",
    1:"atlas",
    2:"moddijet",
    3:"dipho",
    4:"power"
  }
  
  names = getPNames(func)
  names=names.replace("NUM",str(onebin))
  fname = fnmap[func]

  for lin in open("biasInitializations.csv","r").readlines():
    sl = lin.strip().split(",")
    if(sl[0]==fname and sl[1]==str(onebin)):
      vals=sl[3:]
      if(vals[-1]==""):
        vals=vals[:-1]
      vals = [float(v) for v in vals]
      break

  vc = 1
  for vv in vals:
    names=names.replace("VAL{}".format(vc),str(vv))
    vc += 1
  return names

def getSetParams(func, abinlist):


  if(len(abinlist)==1):
    names = getOneBinSetParams(func, abinlist[0])
  else:
    names=""
    for mybin in abinlist:
      names += getOneBinSetParams(func, mybin)

  return names

for i,j in zip(Lc,Ln):
  print(i,j)
  #for pdfi in [0,1,2,3,4]:
  for pdfi in [int(usefunction)]:
  #for pdfi in [0,1]:
  #for pdfi in [1,2,3,4]:
    if(len(aslices)==1):
      fpstring = "--freezeParameters pdf_index_DIPHOM_alpha%i --setParameters pdf_index_DIPHOM_alpha%i=%s"%(aslices[0],aslices[0],pdfi)
      #fpstring = "--freezeParameters pdf_index_DIPHOM_alpha%i --setParameters pdf_index_DIPHOM_alpha%i=%s,pmd1_DIPHOM_alpha8=6.0306e+00,pmd2_DIPHOM_alpha8=4.7111e+00"%(aslices[0],aslices[0],pdfi)
      fpstring += getSetParams(int(usefunction),aslices)
    else:
      fstring = " --freezeParameters "
      setstring = " --setParameters "
      for asl in aslices:
        fstring += "pdf_index_DIPHOM_alpha%i,"%(asl)
        setstring += "pdf_index_DIPHOM_alpha%i=%s,"%(asl,pdfi)
        #fstring += "pdf_index,"
        #setstring += "pdf_index=%s,"%(pdfi)
      fstring = fstring[:-1]
      setstring = setstring[:-1]
      setstring += getSetParams(int(usefunction),aslices)
      fpstring = fstring + setstring
    print(fpstring)
    print("combine "+sys.argv[1]+" -M GenerateOnly -t %i -s 100 --saveToys --toysFrequentist --bypassFrequentistFit  --expectSignal %s -n _%s%s %s"% (ntoys, i, j, comFuncName, fpstring))
    os.system("combine "+sys.argv[1]+" -M GenerateOnly -t %i -s 100 --saveToys --toysFrequentist --bypassFrequentistFit  --expectSignal %s -n _%s%s %s"% (ntoys, i, j, comFuncName, fpstring))
#    if(j!="sig2"):
#      os.system("combine "+sys.argv[1]+" -M FitDiagnostics --cminDefaultMinimizerStrategy=0 -t %i --toysFile higgsCombine_%s%s.GenerateOnly.mH120.123456.root --rMin %f --rMax %f --saveWorkspace -n _%s%s "%(ntoys, j,comName, rmin, rmax, j,comName))
#    else:
    print("combine "+sys.argv[1]+" -M FitDiagnostics --bypassFrequentistFit --skipBOnlyFit --cminDefaultMinimizerStrategy=0 -t %i --toysFile higgsCombine_%s%s.GenerateOnly.mH120.100.root --rMin %f --rMax %f --saveWorkspace -n _%s%s "%(ntoys, j,comFuncName, rmin, rmax, j,comFuncName))
    os.system("combine "+sys.argv[1]+" -M FitDiagnostics --bypassFrequentistFit --skipBOnlyFit --cminDefaultMinimizerStrategy=0 -t %i --toysFile higgsCombine_%s%s.GenerateOnly.mH120.100.root --rMin %f --rMax %f --saveWorkspace -n _%s%s "%(ntoys, j,comFuncName, rmin, rmax, j,comFuncName))

#####

  #Works on individual card
  #os.system("combine "+sys.argv[1]+" -M GenerateOnly -t 100 --saveToys --toysFrequentist  --expectSignal "+str(i)+" -n _{}{} --bypassFrequentistFit ".format(j,comName))
  #os.system("combine "+sys.argv[2]+" -M FitDiagnostics --bypassFrequentistFit --skipBOnlyFit -t 100 --toysFile higgsCombine_{}{}.GenerateOnly.mH120.123456.root --rMin -10 --rMax 10 --saveWorkspace -n_{}{} --cminDefaultMinimizerStrategy=0 ".format(j,comName,j,comName))

####

    print("READING FILE")
    print("fitDiagnostics_{}{}.root".format(j,comFuncName))
    F = ROOT.TFile("fitDiagnostics_{}{}.root".format(j,comFuncName))
    T = F.Get("tree_fit_sb")
    H = ROOT.TH1F("Bias Test, injected r="+j, ";(#mu_{measured} - #mu_{injected})/#sigma_{#mu};toys", 50, -5., 5.)
    #T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test, injected r=" + j)
    #T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test, injected r=" + j)
    T.Draw("(r-%f)"%i+"/(0.5*(rHiErr+rLoErr))>>Bias Test, injected r=" + j, "fit_status>=0")
    #T.Draw("(r-%f)/((rHiErr*(r-%f<0)+rLoErr*(r-%f>0)))"%(i,i,i)+">>Bias Test, injected r=" + j, "fit_status>0")
    #T.Draw("(r-%f)/((rHiErr*(r-%f<0)+rLoErr*(r-%f>0)))"%(i,i,i)+">>Bias Test, injected r=" + j, "fit_status>=0")

    ccc = ROOT.TCanvas()
    ccc.cd()
    H.Draw("e0")
    sname = newDir+"/"+j+"_{}_{}_pdf{}_nofit".format(an,mm,pdfi)
    ccc.Print("{}.png".format(sname))
    ccc.Print("{}.root".format(sname))
    print("Saving as: {}".format(sname))

    os.system("mv fitDiagnostics_{}{}.root {}/fitDiagnostics{}_{}_pdf{}.root".format(j,comFuncName,newDir,comFuncName,j,pdfi))

#os.system("mv *.png {}/.".format(newDir))
