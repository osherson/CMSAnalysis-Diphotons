import os
import sys
import ROOT
import Treemaker

#year = "2016"
#want_run = '274161'
#want_lumi = '295'
#want_id = '511801563'
year = sys.argv[1]
want_run = sys.argv[2]
want_lumi = sys.argv[3]
want_id = sys.argv[4]

Treemaker.Treemaker(year, want_run, want_lumi, want_id)
exit()

if(year == "2016"):
  obj="RECO"
  flist = [
          "/DoubleEG/Run2016B-ver1_HIPM_UL2016_MiniAODv2-v1/MINIAOD",
          "/DoubleEG/Run2016B-ver2_HIPM_UL2016_MiniAODv2-v3/MINIAOD",
          "/DoubleEG/Run2016C-HIPM_UL2016_MiniAODv2-v1/MINIAOD",
          "/DoubleEG/Run2016D-HIPM_UL2016_MiniAODv2-v1/MINIAOD",
          "/DoubleEG/Run2016E-HIPM_UL2016_MiniAODv2-v1/MINIAOD",
          "/DoubleEG/Run2016F-UL2016_MiniAODv2-v1/MINIAOD",
          "/DoubleEG/Run2016F-HIPM_UL2016_MiniAODv2-v1/MINIAOD",
          "/DoubleEG/Run2016G-UL2016_MiniAODv2-v1/MINIAOD",
          "/DoubleEG/Run2016H-UL2016_MiniAODv2-v1/MINIAOD",
          ]

elif(year == "2017"):
  obj="PAT"
  flist = [
          "/DoubleEG/Run2017B-UL2017_MiniAODv2-v1/MINIAOD",
          "/DoubleEG/Run2017C-UL2017_MiniAODv2-v2/MINIAOD",
          "/DoubleEG/Run2017D-UL2017_MiniAODv2-v1/MINIAOD",
          "/DoubleEG/Run2017E-UL2017_MiniAODv2-v1/MINIAOD",
          "/DoubleEG/Run2017F-UL2017_MiniAODv2-v2/MINIAOD",
          ]

elif(year == "2018"):
  obj="PAT"
  flist = [
          "/EGamma/Run2018A-UL2018_MiniAODv2-v1/MINIAOD",
          "/EGamma/Run2018B-UL2018_MiniAODv2-v1/MINIAOD",
          "/EGamma/Run2018C-UL2018_MiniAODv2-v1/MINIAOD",
          "/EGamma/Run2018D-UL2018_MiniAODv2-v2/MINIAOD",
          ]

os.system("rm dasOutput.txt")
for ff in flist:
  os.system("dasgoclient --query \"file,run,lumi dataset={}\" >> dasOutput.txt".format(ff))

fflist = []
lc = 0
for line in open('dasOutput.txt'):
  lc += 1
  #if lc > 3: break

  line = line[:-1] # remove newline character

  linelist = line.split(" ")
  fname, runs, lumis = linelist[0], linelist[1], linelist[2]

  if(runs[0]=="["): runs = runs[1:-1]
  if(lumis[0]=="["): lumis = lumis[1:-1]

  sruns = runs.split(",")
  slumis = lumis.split(",")


  if(want_run in sruns):
    if(want_lumi in slumis):
      fflist.append(fname)

print("Trying these files:")
for ff in fflist:
  print ff

if(len(ff)==0):
  print("Could not find event with run {}, lumi {} in {} dataset".format(want_run, want_lumi, year))
for found_file in fflist:

  os.system("./makeRUCLU.sh {} {} {} {} {}".format(found_file, obj, want_run, want_lumi, want_id))

  rfile = ROOT.TFile("out.root","read")
  tree = rfile.Get("Events")
  if(tree.GetEntries()<1):
    print("Out file has 0 entries. Deleting. Trying next file")
    os.system("rm out.root")
    os.system("rm outflat.root")
  else:
    print("Success! Saving out files")
    os.system("mv out.root EventDisplayAODs/{}_{}_{}_{}.root".format(year, want_run, want_lumi, want_id))
    os.system("mv outflat.root RucluAODs/{}_{}_{}_{}.root".format(year, want_run, want_lumi, want_id))
    break


