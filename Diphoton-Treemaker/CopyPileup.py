import ROOT
from ROOT import *
import sys
import os
from array import array
import shutil

def CopyPileup(fname):

  f = ROOT.TFile.Open(fname, "read")

  myTree = f.Get("pico_nom")

  pulist = [entry.puWeight for entry in myTree]
  puUplist = [entry.puWeightUp for entry in myTree]
  puDownlist = [entry.puWeightDown for entry in myTree]

  newfname = "{}".format(fname[fname.rfind("/")+1 : ].replace(".root", "_temp.root"))
  newfile = ROOT.TFile(newfname, "RECREATE")
  newfile.cd()

  new_nom = myTree.CloneTree()
  new_nom.Write()

  for stree in ["pico_scale_up","pico_scale_down"]:
    new_scale = f.Get(stree).CloneTree()

    apu = array('f',[0])
    apuUp = array('f',[0])
    apuDown = array('f',[0])
    branch = new_scale.Branch('puWeight', apu, 'puWeight/F')
    branchUp = new_scale.Branch('puWeightUp', apuUp, 'puWeightUp/F')
    branchDown = new_scale.Branch('puWeightDown', apuDown, 'puWeightDown/F')

    for ii in range(0, myTree.GetEntries()):
      apu[0] = pulist[ii]
      apuUp[0] = puUplist[ii]
      apuDown[0] = puDownlist[ii]
      branch.Fill()
      branchUp.Fill()
      branchDown.Fill()

    new_scale.Write()

  newfile.Close()

  os.remove(fname)
  shutil.move(newfname, "/cms/xaastorage-2/DiPhotonsTrees/{}".format(newfname.replace("_temp","")))
