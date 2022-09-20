import numpy as np
import sys

if("ALL" in sys.argv):
  doAll = "ALL"
else: doAll = ""

xmin, xmax = 320, 2000
xstep = 10
#xmin, xmax = 400,550
#xstep = 50

alphamin, alphamax = 0.005, 0.03
nalphas = 25+1
#nalphas = 5+1
#alphamin, alphamax = 0.01,0.015
#nalphas = 5+1
alphalist = np.linspace(alphamin, alphamax, nalphas)
#alphalist = np.array([0.026])
#alphalist = np.array([0.01,0.02,0.026])

xlist = [xx for xx in range(xmin, xmax+xstep, xstep)]

xapairs = []

for mx in xlist:
  for aa in alphalist:
    phimass = mx * aa

    xapairs.append((mx, phimass))

shfile = open("InterpoProducerScript.sh","w")

if(doAll == False):
  for aa in range(0,9+1):
    for ii, (xx, pp) in enumerate(xapairs):
      shfile.write("python ../python/Interpolator.py X{}A{} {} alpha{}\n".format(xx, str(round(pp,3)).replace(".","p"), doAll, aa))

else:
    for ii, (xx, pp) in enumerate(xapairs):
      shfile.write("python ../python/Interpolator.py X{}A{} {} alphaALL\n".format(xx, str(round(pp,3)).replace(".","p"), doAll, aa))
