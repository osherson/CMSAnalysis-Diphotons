import numpy as np

year = 2018

xmin, xmax = 250, 2000
xstep = 10

alphamin, alphamax = 0.005, 0.03
nalphas = 25+1
alphalist = np.linspace(alphamin, alphamax, nalphas)
print(alphalist)

xlist = [xx for xx in range(xmin, xmax+xstep, xstep)]

xapairs = []

for mx in xlist:
  for aa in alphalist:
    phimass = mx * aa

    xapairs.append((mx, phimass))

shfile = open("InterpoProducerScript.sh","w")

for ii, (xx, pp) in enumerate(xapairs):
  shfile.write("python MakeDiphotonShapes.py --year {} --mass X{}A{}\n".format(year, xx, str(round(pp,3)).replace(".","p")))
