import sys
import os

AlphaBins = [0.003,0.00347,0.00395,0.00444,0.00494,0.00545,0.00597,0.0065,0.00704,0.00759,0.00815,0.00872,0.0093,0.00989,0.01049,0.0111,0.01173,0.01237,0.01302,0.01368,0.01436,0.01505,0.01575,0.01647,0.0172,0.01794,0.0187,0.01947,0.02026,0.02106,0.02188,0.02271,0.02356,0.02443,0.02531,0.02621,0.02713,0.02806,0.02901,0.03]

for anum in range(0, len(AlphaBins)):
  os.system("cp diphoton_multi_template.config diphoton_multi_alpha{}.config".format(anum))
  os.system("sed -i \"s/TEMPLATE/alpha{}/g\" diphoton_multi_alpha{}.config".format(anum,anum) )

print("done")
