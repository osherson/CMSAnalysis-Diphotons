import os 
import sys

card_dir = "./output/combineCards"
shape_dir = "./ShapeCombinedCards"

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

sed_command = "sed -i \"s/\.\/output\/combineCards\///g\" {}/*.txt".format(shape_dir)
print("Now Running: {}".format(sed_command))
os.system(sed_command)

#ToDo: 
"""

Then do combineCards.py CARD_alpha*_XxAa_function*.txt -S > shape_newCardName.txt
Then combine shape_newCardName.txt -M AsymptoticLimits
"""

