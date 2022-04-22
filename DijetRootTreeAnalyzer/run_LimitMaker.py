import os
import sys

year = sys.argv[1]

gen_signal_dir = "./inputs/Shapes_fromGen/{}/".format(year)
int_signal_dir = "./inputs/Shapes_fromInterpo/{}/".format(year)
alpha = 0.005

gen_signals = {}
int_signals = {}

for sub, dirs, files in os.walk(gen_signal_dir):
  for dd in dirs:
    if("{}X".format(gen_signal_dir) in os.path.join(sub,dd)):
      xm = int(dd[1: dd.find("A")])
      phim = float(dd[dd.find("A")+1 :].replace("p",".") )
      if(phim / xm == alpha):
        gen_signals[dd] = os.path.join(sub,dd)

for sub, dirs, files in os.walk(int_signal_dir):
  for dd in dirs:
    if("{}X".format(int_signal_dir) in os.path.join(sub,dd)):
      xm = int(dd[1: dd.find("A")])
      phim = float(dd[dd.find("A")+1 :].replace("p",".") )
      if(phim / xm == alpha):
        int_signals[dd] = os.path.join(sub,dd)

def getEff(s, d):
  effFile = "{}/{}.txt".format(d,s)
  with open(effFile) as f: 
    eff = float(f.readline().rstrip())
  return eff

ct = 0
for sig, sdir in gen_signals.items():
  ct += 1
  #if ct > 1: break
  print("\nRunning Cardmaker for {}".format(sig))
  xm = sig[1:sig.find("A")]
  eff = getEff(sig,sdir)
  #print(eff / 1000)
  os.system("python python/DiphotonCardMakerSingle.py -f dijet -l 5.99 -y {} -s {} -x {}".format(year, sig, eff/1000))
  os.system("combine output/dijet_combine_gg_{}_lumi-5.990_diphoton_dijet.txt -M AsymptoticLimits".format(xm))
  os.system("mv higgsCombineTest.AsymptoticLimits.mH120.root combineOutput/{}/X{}.root".format(year,xm))

ct = 0
for sig, sdir in int_signals.items():
  ct += 1
  #if ct > 10: break
  print("\nRunning Cardmaker for {}".format(sig))
  xm = sig[1:sig.find("A")]
  eff = getEff(sig.replace(".","p"),sdir)
  os.system("python python/DiphotonCardMakerSingle.py -f dijet -l 5.99 -y {} -s {} -x {} ".format(year, sig, eff/1000))
  os.system("combine output/dijet_combine_gg_{}_lumi-5.990_diphoton_dijet.txt -M AsymptoticLimits".format(xm))
  os.system("mv higgsCombineTest.AsymptoticLimits.mH120.root combineOutput/{}/X{}.root".format(year,xm))












