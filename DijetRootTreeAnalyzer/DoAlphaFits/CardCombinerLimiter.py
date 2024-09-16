import os 
import sys

#card_dir = "./output/combineCards"
card_dir = "./saveOutput/ThreeParams/combineCards"
card_dir = "./saveOutput/ThreeParams/output_10fb/combineCards"
shape_dir = "./ShapeCombinedCards"

gx = [300,400,500,600,750,1000,1500,2000,3000]
ga = [0.005, 0.01, 0.015, 0.02, 0.025, 0.03]

xas = []
alphas = []
funcs = []
for cc in os.listdir(card_dir):
  if(cc.startswith("CARD") and cc.endswith(".txt")):
    ss = cc.split("_")
    salph = ss[1]
    ialpha = int(salph[salph.rfind("a")+1:])
    sax = ss[2]
    func = ss[-1]
    func = func[:func.find(".")]

    xm = int(sax[1 : sax.find("A")])
    phim = float(sax[sax.find("A")+1 : ].replace("p","."))
    alp = phim/xm
    if(xm not in gx or alp not in ga): continue

    alphas.append(ialpha)
    xas.append(sax)
    funcs.append(func)

alphas = set(alphas)
xas = set(xas)
funcs = set(funcs)

print(alphas)
print(xas)
print(funcs)

ct=0
for XA in xas:
  for func in funcs:
    ct +=1 
    #if(ct > 1): continue

    mycommand = "combineCards.py {}/CARD_*_{}*_{}.txt -S > {}/shape_{}_{}.txt".format(card_dir, XA, func, shape_dir, XA, func)
    print("Running: {}".format(mycommand))
    os.system(mycommand)

#sed_command = "sed -i \"s/\.\/output\/combineCards\///g\" {}/*.txt".format(shape_dir)
#sed_command = "sed -i \"s/\.\/saveOutput\/ThreeParams\/output_10fb\/combineCards\///g\" {}/*.txt".format(shape_dir)
#print("Now Running: {}".format(sed_command))
#os.system(sed_command)
