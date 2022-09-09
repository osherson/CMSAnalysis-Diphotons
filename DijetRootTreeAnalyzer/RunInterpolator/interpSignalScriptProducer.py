import numpy as np
import sys

xmin, xmax = 290, 2000
xstep = 20
#xmin, xmax = 400,550
#xstep = 50

alphamin, alphamax = 0.005, 0.03
#nalphas = 25+1
nalphas = 5+1
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

for ii, (xx, pp) in enumerate(xapairs):
  #if(ii > 10):break
  shfile.write("python ../python/Interpolator.py X{}A{}\n".format(xx, str(round(pp,3)).replace(".","p")))
