import os
import sys

dir_path = os.path.dirname(os.path.realpath(__file__))

year = sys.argv[1]
func=sys.argv[2]

LUMI = {}
LUMI["2016"] = 3.59
LUMI["2017"] = 4.15
LUMI["2018"] = 5.99
LUMI["RunII"] = sum([LUMI[yy] for yy in LUMI.keys()])

alphalist = []
this_dir = dir_path + "/inputs/Interpolations/{}/".format(year)

for ff in os.listdir(this_dir):
  xm = int(ff[1 : ff.find("A")])
  if(xm != 600): continue
  am = float(ff[ff.find("A")+1 : ])
  alpha = round(am/xm,3)
  alphalist.append(alpha)

alphas = set(alphalist)

for ii,aa in enumerate(alphas):
  #if(ii > 0): break
  lumi = LUMI["RunII"]
  phi = 600*aa
  if(phi.is_integer()): phi = int(phi)
  masspoint = "X600A{}".format(phi)
  os.system("python python/DiphotonSimpleFitter.py -f {} -y {} -l {} -s {} -w test".format(func, year, lumi, masspoint))
  os.system("mv output/fit_mjj_Full_diphoton_{}_{}.png combineOutput/FitPlots/{}/fit_mjj_Full_diphoton_{}_{}_alpha{}.png".format(func,year,year,func,year,str(aa).replace(".","p")))
  #os.system("mv output/fit_mjj_Full_diphoton_dijet_{}.C combineOutput/FitPlots/{}/fit_mjj_Full_diphoton_dijet_{}_alpha{}.C".format(year,year,year,aa))

