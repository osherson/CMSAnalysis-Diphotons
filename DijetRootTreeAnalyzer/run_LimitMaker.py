import os
import sys
import time

ts = time.time()

LUMI = {}
LUMI["2016"] = 36.050
LUMI["2017"] = 39.670
LUMI["2018"] = 59.320
LUMI["RunII"] = sum(LUMI[yr] for yr in["2016","2017","2018"])

year = sys.argv[1]

gen_signal_dir = "./inputs/Shapes_fromGen/{}/".format(year)
int_signal_dir = "./inputs/Shapes_fromInterpo/{}/".format(year)
#int_signal_dir = "./inputs/Shapes_fromInterpo/withAlphaCut/{}/".format(year)
alpha = 0.005

gen_signals = {}
int_signals = {}

have = [ff for s,d,ff in os.walk("combineOutput/{}/".format(year))][0]
have_x = [int(f[1:f.find(".")]) for f in have]

print("Already have {} files. Skipping these.".format(len(have_x)))
time.sleep(1)

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
      if(xm in have_x): continue
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
  os.system("python python/DiphotonCardMakerSingle.py -f dijet -l {} -y {} -s {} -x {}".format(LUMI[year]/10, year, sig, eff/1000))
  os.system("combine output/dijet_combine_gg_{}_lumi-5.990_diphoton_dijet.txt -M AsymptoticLimits".format(xm))
  os.system("mv higgsCombineTest.AsymptoticLimits.mH120.root combineOutput/{}/X{}.root".format(year,xm))

ct = 0
for sig, sdir in int_signals.items():
  ct += 1
  #if ct > 10: break
  print("\nRunning Cardmaker for {}".format(sig))
  xm = sig[1:sig.find("A")]
  eff = getEff(sig.replace(".","p"),sdir)
  os.system("python python/DiphotonCardMakerSingle.py -f dijet -l {} -y {} -s {} -x {} ".format(LUMI[year]/10, year, sig, eff/1000))
  os.system("combine output/dijet_combine_gg_{}_lumi-5.990_diphoton_dijet.txt -M AsymptoticLimits".format(xm))
  os.system("mv higgsCombineTest.AsymptoticLimits.mH120.root combineOutput/{}/X{}.root".format(year,xm))



tf = time.time()

print("Total Elapsed Time: {:.2f} min".format((tf-ts)/60))








