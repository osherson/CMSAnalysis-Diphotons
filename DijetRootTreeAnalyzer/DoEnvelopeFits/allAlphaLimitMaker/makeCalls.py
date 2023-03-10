import sys
import os
import stat

if("clean" in sys.argv):
  print("Deleting Call Files")
  os.system("rm CallFiles/*")
  print("Done deleting")

dir_path = os.path.dirname(os.path.realpath(__file__))

wd = "Interpo/int_1_fb"
card_dir = "../AllAlphaCards/{}".format(wd)

ct = 0
for card in os.listdir(card_dir):
  #if(ct > 10): break
  if(ct % 100 == 0): print(ct)

  mass = card.split("_")[-2]
  newCardName = "CallFiles/Call_{}.sh".format(ct)
  newCard = open(newCardName,"w")

  template = open("Call_template.sh","r")
  for line in template.readlines():
    line = line.replace("DIRNAME", wd)
    line = line.replace("CARDNAME", card)
    line = line.replace("MASSPOINT", mass)
    newCard.write(line)
  newCard.close()
  template.close()

  os.chmod(newCardName, 0o755)
  ct += 1


DIR = "CallFiles"
ncalls = len([name for name in os.listdir(DIR) if os.path.isfile(os.path.join(DIR, name))])
print("Number files: {}".format(ncalls))
os.system("sed -i \"s/ Queue.*/ Queue {}/g\" runCondor.jdl".format(ncalls))




