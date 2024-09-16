import numpy as np
import os,sys
#from drawDiagnostics import *

def getXPhiAlpha(signal):
  x = int(signal[1 : signal.find("A")])
  phi = float(signal[signal.find("A")+1 : ].replace("p","."))
  alpha = round(phi/x,4)
  return x,phi,alpha

def runFitDiagnostics(xm, alpha, wdir):
  phi = xm * alpha
  sphi = str(phi).replace(".","p")
  if(sphi[-2:]=="p0"): sphi=sphi.replace("p0","")
  signal = "X{}A{}".format(xm,sphi)
  print(signal)

  combine_card = "../AllAlphaCards/Interpo/{}/dipho_combine_multipdf_lumi-13.700_RunII_X{}A{}_Allalpha.txt".format(wdir,xm,sphi)
  if(not os.path.exists(combine_card)):
    print("Problem getting {}".format(combine_card))
    return

  fdcom = "combine -M FitDiagnostics {} --cminDefaultMinimizerStrategy 0 > out.txt".format(combine_card)
  print(fdcom)

  os.system(fdcom)
  os.system("rm *.root ")
  os.system("rm *.out ")

  for line in open("out.txt","r").readlines():
    if("fail" in line or "Fail" in line):
      failed=True
      return failed

  return False



#wds = ["int_1_fb","int_0p1_fb","int_0p01_fb","int_10_fb","int_100_fb"]
wds = ["int_1_fb"]

gfile = open("fitSuccesses.txt","r")
goods = []
for lin in gfile.readlines():
  goods.append(lin[:-1])
gfile.close()

for wd in wds:
  print("-----------------------------")
  print("Starting {}".format(wd))
  card_dir = "../AllAlphaCards/Interpo/{}/".format(wd)
  xs = wd.split("_")[1]
  count = 0
  for card in os.listdir(card_dir):
    #if(count >= 6): exit()
    signal = card.split("_")[-2]
    #if(signal != "X500A4"): continue
    xm,phim,alpha = getXPhiAlpha(signal)
    if(xm >= 700): continue
    if("{},{},{}".format(xm,alpha,xs) in goods):
      print("Already done {}, {}, {}".format(xm,alpha,xs))
      continue
    print(xm,phim,alpha)
    count += 1
    failed = runFitDiagnostics(xm, alpha, wd)
    if(failed==True):
      failfile = open("fitFailures.txt","a")
      failfile.write("{},{},{}\n".format(xm,alpha,xs))
      failfile.close()
    else:
      goodfile = open("fitSuccesses.txt","a")
      goodfile.write("{},{},{}\n".format(xm,alpha,xs))
      goodfile.close()


