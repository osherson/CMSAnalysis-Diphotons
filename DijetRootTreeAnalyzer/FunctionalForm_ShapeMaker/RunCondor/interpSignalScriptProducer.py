import numpy as np
import sys

xmin, xmax = 300, 3000
xmin, xmax = 2400, 3000
xstep = 10
#xmin, xmax = 400,550
#xstep = 50
xlist = [xx for xx in range(xmin, xmax+xstep, xstep)]

alphamin, alphamax = 0.005, 0.025
alphastep = 0.001
alphalist = [round(aa,4) for aa in np.arange(alphamin, alphamax+alphastep, alphastep)]
alphalist = [0.01]

xapairs = []

for mx in xlist:
  for aa in alphalist:
    xapairs.append((mx, aa))

shfile = open("InterpoProducerScript.sh","w")

for ii, (xx, pp) in enumerate(xapairs):
  shfile.write("python ../MakeShapes_Condor.py {} {} \n".format(xx, round(pp,3)))
