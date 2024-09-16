import sys,os

if("clean" in sys.argv):
  print("Deleting CallFiles")
  os.system("rm CallPost*")
  print("Done Deleting")

xm = [310, 400, 500, 600, 750, 1000, 1500, 2000, 2990]
funcs = [0,1,2,3,4]
alphas = [0.005, 0.01, 0.015, 0.02, 0.025]
alphas = [0.005]

ct = 0
for xx in xm:
  for ff in funcs:
    for aa in alphas:
      os.system("cp Call_template.sh   CallPostProcess_{}.sh".format(ct))
      os.system("sed \'s/XXX/{}/g\' -i CallPostProcess_{}.sh".format(xx, ct))
      os.system("sed \'s/FFF/{}/g\' -i CallPostProcess_{}.sh".format(ff, ct))
      os.system("sed \'s/AAA/{}/g\' -i CallPostProcess_{}.sh".format(aa, ct))
      ct += 1

print("Total Files: {}".format(ct))
os.system("cp runCondor_template.sh runCondor_all.sh")
os.system("sed \'s/NNN/{}/g\' -i runCondor_all.sh".format(ct))

