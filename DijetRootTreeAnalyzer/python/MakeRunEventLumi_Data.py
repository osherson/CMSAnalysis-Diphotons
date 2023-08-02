import ROOT
from ROOT import *
import csv
import numpy
import os
import math
import sys
import time

dir_path = os.path.dirname(os.path.realpath(__file__))
RDF = ROOT.RDataFrame.RDataFrame
sys.path.append(dir_path+"/../../.")
gROOT.SetBatch()

xaastorage = "/cms/xaastorage-2/DiPhotonsTrees/"

#############################
#Get DATA
#years = ["2016","2017","2018"]
years = ["2016"]

for yy in years:
  print("Starting year: {}".format(yy))
  DATA = []
  for ff in os.listdir(xaastorage):
    #if("Run" in ff and year in ff): #one year data
    if("Run" in ff and yy in ff): #All Run II Data
      dset = ff[:ff.find(".")]
      DATA.append((dset,os.path.join(xaastorage,ff)))
  
  for(dset, fil) in DATA:
    if(yy == "2018" and "part2" in dset): continue
    if(yy == "2018" and "part3" in dset): continue
    print(dset)
    oFile = open("RunEventLumiFiles/{}/{}.csv".format(yy,dset),"w")
    chain = ROOT.TChain("pico_full")
    chain.Add(fil)
    if(yy == "2018" and "part1" in dset): 
      chain.Add("/cms/xaastorage-2/DiPhotonsTrees/Run_D_part2_2018.root")
      chain.Add("/cms/xaastorage-2/DiPhotonsTrees/Run_D_part3_2018.root")
    rdf = RDF(chain)

    npas = rdf.AsNumpy(["run","id","lumiSec"])
    rrs = npas["run"]
    iis = npas["id"]
    lls = npas["lumiSec"]
    for (rr,ii,ll) in zip(rrs,iis,lls):
      oFile.write("{},{}\n".format(rr,ll))
      #oFile.write("{},{},{}\n".format(rr,ii,ll))
    oFile.close()
