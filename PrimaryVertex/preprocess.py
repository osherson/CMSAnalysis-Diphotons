#!/usr/bin/env python
import os
import sys
import ROOT
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetmetHelperRun2 import *
from PhysicsTools.NanoAODTools.postprocessing.modules.jme.jetRecalib import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducerMyTrees import *
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *
from PhysicsTools.NanoAODTools.postprocessing.modules.common.PrefireCorr import *

# JEC dict


def preprocess(Inputs, OutputFolder, Year):
    #useModules = [PrefCorr()]
    useModules = []
    if Year == "2016":
      useModules.append(puWeight_UL2016())
    if Year == "2017":
      useModules.append(puWeight_UL2017())
    if Year == "2018":
      useModules.append(puWeight_UL2018())

#    preproc_cuts = "PV_npvsGood>0&&("
    preproc_cuts = ""

    p = PostProcessor(OutputFolder, [Inputs], preproc_cuts, modules=useModules, provenance=False)#, outputbranchsel="keepfile.txt", jsonInput=JSON)
    p.run()

preprocess(sys.argv[1], sys.argv[2], sys.argv[3])
