import numpy as np
import sys

xmin, xmax = 300, 3000
xstep = 10
#xmin, xmax = 400,550
#xstep = 50

alphamin, alphamax = 0.005, 0.03
nalphas = 25+1
#nalphas = 5+1
alphalist = np.linspace(alphamin, alphamax, nalphas)
#alphalist = np.array([0.026])
#alphalist = np.array([0.01,0.02,0.026])

xlist = [xx for xx in range(xmin, xmax+xstep, xstep)]

xapairs = []

for mx in xlist:
  for aa in alphalist:
    xapairs.append((mx, aa))

shfile = open("InterpoProducerScript.sh","w")

for ii, (xx, pp) in enumerate(xapairs):
  shfile.write("python ../MakeShapes_Condor.py {} {} \n".format(xx, round(pp,3)))
