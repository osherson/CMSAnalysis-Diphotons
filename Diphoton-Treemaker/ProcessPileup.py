#!/usr/bin/env python
import os
import sys
import ROOT
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducer import *
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *

def ProcessPileup(InputFile):

    useModules = []

    OutputFolder = "/cms/xaastorage-2/DiPhotonsTrees"

    if "2016" in InputFile:
      useModules.append(puWeight_2016())
    if "2017" in InputFile:
      useModules.append(puWeight_2017())
    if "2018" in InputFile:
      useModules.append(puWeight_2018())


    p = PostProcessor(OutputFolder, [InputFile], modules=useModules)
    p.run()

#ProcessPileup("/cms/xaastorage-2/DiPhotonsTrees/X200A1_2018.root")
