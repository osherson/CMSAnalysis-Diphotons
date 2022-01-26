
def getNEvents(year, xamass):
  xmass = xamass[ xamass.find("X")+1 : xamass.find("A")]
  amass = xamass[ xamass.find("A")+1 : ].replace("p",".")

  if("16" in year): fname="HelperFiles/Signal_NEvents_2016.csv"
  if("17" in year): fname="HelperFiles/Signal_NEvents_2017.csv"
  if("18" in year): fname="HelperFiles/Signal_NEvents_2018.csv"

  myFile = open(fname, "r")
  Lines = myFile.readlines()
  nevt = 0
  for line in Lines:
    s=line.split(",")
    if(s[0]==xmass and s[1]==amass):
      nevt = int(s[2])

  return nevt

def getTrigIndex(year, run):
  myFile = open("HelperFiles/TriggerIndices_forPico.csv","r")
  Lines = myFile.readlines()
  for line in Lines:
    params = line.split(",")
    if(params[0]==year and params[1]==run):
      return (params[2], params[3])

  return

keeplist = ['lumiSec','run','id', 
            "weight",
            "HLT_DoublePhoton", "HLT_EleTrig",
            "clu1_pt",
            "clu1_eta",
            "clu1_phi",
            "clu1_energy",
            "clu1_moe",
            "clu1_iso",
            "clu1_monopho",
            "clu1_dipho",
            "clu1_hadron",
            "clu2_pt",
            "clu2_eta",
            "clu2_phi",
            "clu2_energy",
            "clu2_moe",
            "clu2_iso",
            "clu2_monopho",
            "clu2_dipho",
            "clu2_hadron",
            'masym', 'deta','aM', 'XM', 'alpha']

def MakeFolder(N):
    import os
    if not os.path.exists(N):
     os.makedirs(N)

