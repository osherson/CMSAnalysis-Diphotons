import os

#out_dir = "combineOutputEnvelope"
out_dir = "fb_1_loose_biasOutput"

def getXPhiAlpha(xa):
  x = int(xa[1:xa.find("A")])
  phi = float(xa[xa.find("A")+1 :].replace("p","."))
  alpha = phi/x

  return x,phi,alpha

mfile = open("BiasMeans.csv","w")
mfile.write("X Mass, Alpha, SigStrength, PdfIndex, Mean, Sigma\n")

for xa in os.listdir(out_dir):
  if(xa[0] != "X"): continue
  #if("X400" not in xa): continue
  xm,phim,alpha = getXPhiAlpha(xa)

  meanFile = "{}/{}/meaninfo_{}.csv".format(out_dir,xa,xa)
  F = open(meanFile,"r")
  for lin in F.readlines():
    mfile.write("{},{},{}".format(xm,alpha,lin))
  F.close()


