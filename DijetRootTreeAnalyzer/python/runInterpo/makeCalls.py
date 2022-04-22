import os
import os.path
import sys
import glob

needlist = []

for subdir, dirs, files in os.walk("."):
  for ff in files:
    if("single" in ff):
      needlist.append(ff)

for nn in needlist:
  ext = nn[nn.find(".")+1:]

  callfile = open("template_call.sh", "r")
  
  fext = ext.lstrip("0")
  if fext=="": fext="0"
  outcall = open("CallFiles/Call_{}.sh".format(fext), "w")

  Lines = callfile.readlines()
  for line in Lines:
    if ("ext" in line):
      line = line.replace("ext",ext)
    outcall.write(line)

