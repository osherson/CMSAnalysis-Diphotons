import os,sys

#Copies the efficiency files from GenFiles to Int files

gdir="./Shapes_fromGen/alphaBinning/"
idir="./Shapes_fromInterpo/alphaBinning/"

for abin in os.listdir(idir):
  for xa in os.listdir(os.path.join(idir,abin)):
    effFile = os.path.join(idir,abin,xa,"{}.txt".format(xa))
    geffFile = effFile.replace("Interpo","Gen")
    stem = os.path.join(idir,abin,xa)
    gstem = stem.replace("Interpo","Gen")
    if(os.path.exists(geffFile)):
      print(xa)
      os.system("cp {} {}".format(geffFile, effFile))
      os.system("cp {}/* {}/.".format(gstem,stem))
