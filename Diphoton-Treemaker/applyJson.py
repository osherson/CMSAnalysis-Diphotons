import os
import ROOT
from ROOT import *
import math
from math import *
import sys
import glob
import shutil
from FWCore.PythonUtilities.LumiList import LumiList

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(dir_path+"/../.")
import PlottingPayload as PL

JFiles = {}
JFiles["2016"] = "{}/JSonFiles/Cert_271036-284044_13TeV_Legacy2016_Collisions16_JSON.txt".format(dir_path)
JFiles["2017"] = "{}/JSonFiles/Cert_294927-306462_13TeV_UL2017_Collisions17_GoldenJSON.txt".format(dir_path)
JFiles["2018"] = "{}/JSonFiles/Cert_314472-325175_13TeV_Legacy2018_Collisions18_JSON.txt".format(dir_path)

def ApplyJson(inputFile, treeNames):

  yl = inputFile.find("20")
  year = inputFile[ yl : yl+4]

  fdir = inputFile[ : inputFile.rfind("/")+1]
  froot = inputFile[inputFile.rfind("/")+1 : inputFile.rfind(".")]

  # get json file
  injfile = JFiles[year]
  jlist = LumiList (filename = injfile)
  # initialize output lumilist
  myrunlumi =[]

  print "Working on " + inputFile
  F = ROOT.TFile.Open(inputFile,"read")
  newFname = inputFile.replace(".root","_temp.root")
  newF = ROOT.TFile.Open(newFname,"recreate")
	
  if F:
    print('is open')
  else:
	  print('oops')

  for treeName in treeNames:
	  # initialize event count for skipping events below
    nevt=0
    T = F.Get(treeName)
    newT = T.CloneTree(0)
    print("Initial Events: {}".format(T.GetEntries()))

    pcount = 0
    for e in T:
      # Check that events for data pass the golden json file
      passJson = False

      passJson = jlist.contains(T.run,T.lumiSec)

      if not(passJson): continue
      else:
        myrunlumi.append((T.run,T.lumiSec))
        pcount += 1
        newT.Fill()

    print("Pass events: {}".format(pcount))

    if("full" in treeName):
      PL.MakeFolder("{}/outJson".format(fdir))
      outjfile="{}/outJson/{}.json".format(fdir, froot)
      outList = LumiList(lumis = myrunlumi)
      outList.writeJSON(outjfile)

    #newT.Print()
    newF.Write()

  os.remove(inputFile)
  shutil.move(newFname, newFname.replace("_temp.root",".root"))

#ApplyJson("/cms/xaastorage-2/DiPhotonsTrees/Run_B_2017.root", ["pico_skim","pico_full"]) 
