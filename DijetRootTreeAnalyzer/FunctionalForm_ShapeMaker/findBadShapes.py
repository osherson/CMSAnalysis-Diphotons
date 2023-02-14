import numpy as np
import ROOT
import sys,os
from array import array

ROOT.gROOT.SetBatch()
ROOT.gRandom.SetSeed(0)

dir_path = os.path.dirname(os.path.realpath(__file__))

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = phi/x
  return x,phi,alpha

def MakeFolder(N):
   import os
   if not os.path.exists(N):
    os.makedirs(N)

int_dir = "../../inputs/Shapes_fromInterpo/unBinned"

xmin, xmax = 300, 2500
xstep = 10
#xmin, xmax = 400,550
#xstep = 50
xlist = [xx for xx in range(xmin, xmax+xstep, xstep)]

alphamin, alphamax = 0.005, 0.025
alphastep = 0.001
alphalist = [round(aa,4) for aa in np.arange(alphamin, alphamax+alphastep, alphastep)]
alphalist = [0.005]

shape = "alpha"

known_x = [300,400,500,600,750,1000,1500,2000,2500]

if("clean" in sys.argv):
  print("Deleting old plots")
  os.system("rm -rf Plots/alpha*")

xapairs = []
for mx in xlist:
  for aa in alphalist:
    xapairs.append((mx, aa))

def getNearestX(inx):
  for ii in range(0,len(known_x)-1):
    if(known_x[ii] <= inx and known_x[ii+1] > inx):
      return known_x[ii], known_x[ii+1]

def getstr(phim):
  sphim = str(phim).replace(".","p")
  if(sphim.endswith("p0")):sphim=sphim.replace("p0","")
  return sphim

pnames = ["a1","a2","n1","n2","mean","sigma", "N"]
def getParam(signal, pname):
  fname = "./inputs/Shapes_fromInterpo/unBinned/{}/params_alpha.txt".format(signal)
  pind = pnames.index(pname)

  fil = open(fname,"r")
  lin = fil.readline()
  param = float(lin.split(",")[pind])
  return param

bfile = open("badsignals.txt","w")
for ii in range(1,len(xapairs)-1):
  (xm,alpha) = xapairs[ii]
  phim = getstr(xm*alpha)
  xdown,xup = getNearestX(xm)
  phidown,phiup = getstr(xdown*alpha),getstr(xup*alpha)

  sig = "X{}A{}".format(xm, phim)
  sigdown = "X{}A{}".format(xdown,phidown)
  sigup = "X{}A{}".format(xup,phiup)

  for mypar in pnames:
    if(mypar != "a2"):continue
    pp,pd,pu = getParam(sig,mypar),getParam(sigdown,mypar),getParam(sigup,mypar)

    maxp,minp = max(pd,pu),min(pd,pu)

    if("run" in sys.argv):
      count = 0
      while(pp < minp or pp > maxp):
        count += 1
        if(count >9):
          print("Too many loops. Giving Up")
          break
        print("Retrying")
        print("python MakeShapes_Condor.py {} {} quick".format(xm,alpha))
        os.system("python MakeShapes_Condor.py {} {} quick".format(xm,alpha))
        pp = getParam(sig,mypar)
        print("NEW Param: {}".format(pp))

    else:
      if(pp < minp or pp > maxp):
        print("Found bad signal: {} {}".format(xm,alpha))
        bfile.write("Bad signal: {} variable.\n{} {}\n".format(mypar,xm,alpha))



