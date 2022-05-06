import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))

for ff in os.listdir("condor_submitFiles"):
    if("template" in ff): continue
    os.system("condor_submit condor_submitFiles/{}".format(ff))



