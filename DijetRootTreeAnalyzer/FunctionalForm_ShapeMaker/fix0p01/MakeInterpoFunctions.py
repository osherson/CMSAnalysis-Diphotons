import numpy as np
import ROOT
import sys,os
from array import array

ROOT.gROOT.SetBatch()

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = phi/x
  return x,phi,alpha

def DSCB(x, par):
  a1 = par[0]
  a2 = par[1]
  n1 = par[2]
  n2 = par[3]
  mean = par[4]
  sigma = par[5]
  N = par[6]

  t = (x[0]-mean)/sigma

  fact1TLessMinosAlphaL = a1/n1
  fact2TLessMinosAlphaL = (n1/a1) - a1 -t
  fact1THihgerAlphaH = a2/n2
  fact2THigherAlphaH = (n2/a2) - a2 +t

  if (-a1 <= t and a2 >= t):
      result = np.exp(-0.5*t*t)
  elif (t < -a1):
      result = np.exp(-0.5*a1*a1)*np.power(fact1TLessMinosAlphaL*fact2TLessMinosAlphaL, -n1)

  elif (t > a2):
      result = np.exp(-0.5*a2*a2)*np.power(fact1THihgerAlphaH*fact2THigherAlphaH, -n2)
  else:
    return 0

  return N*result


#def getParams(param,xm,alpha):
#  pfile = open("InterpoParamFiles/{}.txt".format(param),"r")
#  pval=-999

#  for lin in pfile.readlines():
#    sl = lin.split(",")
#    if(int(sl[0])==xm and float(sl[1])==alpha):
#      pval = float(sl[-1][:-1])
#      break

#  pfile.close()

#  return pval

def getNewParams(param,xm,alpha):
  pfile = open("InterpoParamFiles/{}.txt".format(param),"r")
  pval=-999

  found=False

  for lin in pfile.readlines():
    sl = lin.split(",")
    if(int(sl[0])==xm and float(sl[1])==alpha):
      pval = float(sl[-1][:-1])
      found=True
      break
  pfile.close()
  if(found):
    return pval
  amass = alpha*xm
  amass = str(amass).replace(".","p")
  if(amass.endswith("p0")): amass=amass[:-2]

  pkfile = open("../../inputs/Shapes_fromInterpo/unBinned/X{}A{}/params_alpha.txt".format(xm,amass),"r")
  idx = pnames.index(param)
  lin = pkfile.readline().split(",")
  pval = float(lin[idx])
  pfile.close()

  return pval


AfineB = list(np.linspace(0.0,0.03, 10000))
AlphaBins = [ 0.003, 0.00347, 0.00395, 0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.00872, 0.0093, 0.01049, 0.01505, 0.03]
for aa in AlphaBins:
  if(aa not in AfineB): AfineB.append(aa)
AfineB = sorted(AfineB)


pnames = ["a1","a2","n1","n2","mean","sigma","N"]
count = 0

badsigs = []
for pname in pnames:
  inF = open('BadSignals/badsignals_{}.txt'.format(pname))
  for lin in inF.readlines():
    xx,aa = int(lin.split(",")[0]), float(lin.split(",")[1][:-1])
    badsigs.append((xx,aa))

print(len(badsigs))
badsigs = list(set(badsigs))
#print(len(badsigs))
#exit()

for (xm,alpha) in badsigs:
  #if(xm != 300 or alpha != 0.02): continue
  amass = xm*alpha
  samass = str(amass).replace(".","p")
  salpha=str(alpha).replace(".","p")
  if(samass.endswith("p0")): samass = samass[:-2]
  if(salpha.endswith("p0")): salpha = salpha[:-2]
  print(xm,salpha,samass)
  count += 1

  mypardic={}
  for pname in pnames:
    mypardic[pname]=getNewParams(pname, xm, alpha)

  mypars = [mypardic[pp] for pp in pnames]
  dscb = ROOT.TF1("dscb_fit",DSCB, 0., 0.03, 7)
  print(mypars)
  #exit()

  dscb.SetParameters(mypars[0],mypars[1],mypars[2],mypars[3],mypars[4],mypars[5],mypars[6])
  cc = ROOT.TCanvas()
  cc.cd()
  dscb.SetLineColor(ROOT.kRed)
  dscb.Draw()
  cc.Print("InterpoFunctionShapes/X{}alpha{}.png".format(xm,salpha))

  pfile = open("../../inputs/Shapes_fromInterpo/unBinned/X{}A{}/params_alpha_i.txt".format(xm,samass),"w")
  pfile.write("{},{},{},{},{},{},{}".format(mypars[0],mypars[1],mypars[2],mypars[3],mypars[4],mypars[5],mypars[6]))
  pfile.close()
  continue

  oF = ROOT.TFile("../../inputs/Shapes_fromInterpo/unBinned/X{}A{}/Sig_nominal.root".format(xm,samass), "update")
  print(oF.GetName())
  oF.cd()
  S1 = ROOT.TH1F("h_alpha_fine_i", ";#alpha", len(AfineB)-1, np.array(AfineB))
  #S1.FillRandom("test"+str(xm)+samass, 10000)
  S1.FillRandom("dscb_fit",10000)
  s1int = S1.Integral()
  S1.Scale(1/s1int)
  S1.Write()
  oF.Close()



