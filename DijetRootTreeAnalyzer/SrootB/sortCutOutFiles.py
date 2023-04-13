import sys
import numpy
import pandas
import os

#xmass = sys.argv[2]
#phimass = sys.argv[3]

for fil in os.listdir("CutOutFiles"):
  sig = fil[:fil.find("_")]
  print(sig)
  fname = "CutOutFiles/{}_out.csv".format(sig)
  print("\nSorting file for  {}".format(sig))
  df = pandas.read_csv(fname, index_col=None)

  df = df.sort_values(by="srootb", ascending=False)
  print(df.head())

  df.to_csv("CutOutFiles/{}_sorted.csv".format(sig),index=False)
