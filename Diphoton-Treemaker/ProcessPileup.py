#!/usr/bin/env python
import os
import sys
import ROOT
from importlib import import_module
from PhysicsTools.NanoAODTools.postprocessing.framework.datamodel import Collection
from PhysicsTools.NanoAODTools.postprocessing.framework.eventloop import Module
from PhysicsTools.NanoAODTools.postprocessing.modules.common.puWeightProducerMyTrees import *
from PhysicsTools.NanoAODTools.postprocessing.framework.postprocessor import *

def ProcessPileup(Inputs):

    OutputFolder = Inputs[:Inputs.rfind("/")]
    Year = Inputs[Inputs.find("_20")+1 : Inputs.find("_20")+5]
    useModules = []

    if Year == "2016":
      useModules.append(puWeight_UL2016())
    if Year == "2017":
      useModules.append(puWeight_UL2017())
    if Year == "2018":
      useModules.append(puWeight_UL2018())

    p = PostProcessor(OutputFolder, [Inputs], modules=useModules)
    p.run()
