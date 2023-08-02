import os
import sys

clean=False
goLim = False
fast=False
doInterpo = False
fnum=999

#xmasslist = ['600','400','500','300','750','1000','1500','2000']
#xmasslist = ['600','400','500','200','300','750','1000','1500','2000','3000']
xmasslist = ['600']

year = 2018
LUMI = 13.7 * 1000  #provide lumi in PB
XS = 0.001

forc = sys.argv[1]
 
if forc == "comb":
  #dataDir = "../inputs/Shapes_DATA/PreApprovalTenPercent/10_loose/"
  dataDir = "../inputs/Shapes_DATA/Unblinding/full_tight_ndofBins/"
  #dataDir = "../inputs/Shapes_DATA/Unblinding/10_loose/"
elif forc == "all":
  #dataDir = "../inputs/Shapes_DATA/PreApprovalTenPercent/10_loose_allAlphaBins/"
  dataDir = "../inputs/Shapes_DATA/Unblinding/full_tight_OneBigBin/"
  #dataDir = "../inputs/Shapes_DATA/Unblinding/10_loose_allAlphaBins/"


alist = []
for anum in os.listdir(dataDir):
  if(not anum.isdigit()): continue
  alist.append(int(anum))

adlist = [os.path.join(dataDir,str(aa)) for aa in sorted(alist)]

#To run test on one alpha bin, add fast# to command line arg
for arg in sys.argv:
  if 'fast' in arg:
    fnum = int(arg[4:])
    fast=True
    print("Only doing alpha bin {}".format(fnum))


def MakeFolder(N):
    if not os.path.exists(N):
     os.makedirs(N)

for adir in adlist:
  anum = int(adir[adir.rfind("/")+1:])
  #if(anum != 8):continue

  rfile = open("{}/arange.txt".format(adir),"r")
  rr = rfile.readline().split(",")
  la,ha = rr[0],rr[1]
  rfile.close()
  
  print("Alpha Bin {}".format(anum))
  print("{} - {}".format(la,ha))
  
  dfname = "{}/DATA.root".format(adir)

  mycommand = "python ../python/BinnedDiphotonFit.py -c ../config/envelope2/diphoton_multi_alpha{}.config -y {} -l {} -b DIPHOM_alpha{} {} -d output --fit-spectrum --write-fit --words test  --abin {} --lowA {} --hiA {}".format(anum,year,LUMI,anum,dfname,anum,la,ha)
  print(mycommand)
  os.system(mycommand)
  #continue

