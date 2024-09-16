import ROOT
import numpy as np
import sys,os
from array import array

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = round(phi/x,4)
  return x,phi,alpha

def DSCB(x, par):
  a1 = par[0]
  a2 = par[1]
  n1 = par[2]
  n2 = par[3]
  mean = par[4]
  sigma = par[5]
  N = par[6]

  if(sigma == 0): return -999
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

def getParams(param,xm,am):
  pfile = open("{}/X{}A{}/params_alpha_i.txt".format(int_dir,int(xm),am),"r")

  for lin in pfile.readlines():
    sl = lin.split(",")
    pvals = [float(pp) for pp in sl]

  pfile.close()

  return pvals

anoms = []
anfile = "fix0p01/CorrectedParams/a1.txt"
for lin in open(anfile,"read").readlines():
    v = lin.strip().split(",")
    anoms.append((int(v[0]), float(v[1])))

##############################################################

ROOT.gROOT.SetBatch()

int_dir = "../inputs/Shapes_fromInterpo/unBinned/"
smear_SF = 1 + 0.23
smear_SF_up = 1 + 0.23
smear_SF_down = 1 - 0.23

AfineB = list(np.linspace(0.0,0.03, 10000))
AlphaBins = [ 0.003, 0.00347, 0.00395, 0.00444, 0.00494, 0.00545, 0.00597, 0.0065, 0.00704, 0.00759, 0.00815, 0.00872, 0.0093, 0.01049, 0.01505, 0.03]
for aa in AlphaBins:
  if(aa not in AfineB): AfineB.append(aa)
AfineB = sorted(AfineB)

pnames = ["a1","a2","n1","n2","mean","sigma","N"]
count = 0

#xmin, xmax = 300, 3000
xmin, xmax = 310, 2990
xstep = 10
xlist = [xx for xx in range(xmin, xmax+xstep, xstep)]
alphamin, alphamax = 0.005, 0.025
alphastep = 0.001
alphalist = [round(aa,4) for aa in np.arange(alphamin, alphamax+alphastep, alphastep)]

params = ["a1","a2","n1","n2","mean","sigma","N"]

for xm in xlist:
  for alpha in alphalist:
    amass = round(xm*alpha,3)
    samass = str(amass).replace(".","p")
    salpha=str(alpha).replace(".","p")
    if(samass.endswith("p0")): samass = samass[:-2]
    if(salpha.endswith("p0")): salpha = salpha[:-2]
    count += 1

#    if((xm,alpha) not in anoms):
#      continue
#    else:
#      print(xm,amass)

    #if(xm <= 2150): continue
    if(count % 100 == 0): print(count)

    print(xm, amass, alpha)

    mypars = getParams(int_dir,xm, samass)

    #mypars[5] = mypars[5] * smear_SF 
    dscb_up = ROOT.TF1("dscb_fit_up",DSCB, 0., 0.03, 7)
    dscb_up.SetParameters(mypars[0],mypars[1],mypars[2],mypars[3],mypars[4],mypars[5]*smear_SF_up,mypars[6])

    dscb_down = ROOT.TF1("dscb_fit_down",DSCB, 0., 0.03, 7)
    dscb_down.SetParameters(mypars[0],mypars[1],mypars[2],mypars[3],mypars[4],mypars[5]*smear_SF_down,mypars[6])

    #cc = ROOT.TCanvas()
    #cc.cd()
    #dscb.SetLineColor(ROOT.kRed)
    #dscb.Draw()
    #cc.Print("InterpoFunctionShapes/X{}alpha{}.png".format(xm,salpha))
    #cc.Print("temp.png".format(xm,salpha))

    hfname = int_dir + "/X" + str(int(xm)) + "A" + samass + "/Sig_nominal.root"
    hfile = ROOT.TFile(hfname, "update")
    #hfile = ROOT.TFile("temp.root","recreate")

    Su = ROOT.TH1F("h_alpha_su", "Smeared Up #alpha;#alpha", len(AfineB)-1, np.array(AfineB))
    #Su.FillRandom("test"+str(xm)+samass, 10000)
    Su.FillRandom("dscb_fit_up",10000)
    Suint = Su.Integral()
    Su.Scale(1/Suint)
    Su.Write()

    Sd = ROOT.TH1F("h_alpha_sd", "Smeared Up #alpha;#alpha", len(AfineB)-1, np.array(AfineB))
    #Sd.FillRandom("test"+str(xm)+samass, 10000)
    Sd.FillRandom("dscb_fit_down",10000)
    Sdint = Sd.Integral()
    Sd.Scale(1/Sdint)
    Sd.Write()

    hfile.Close()

