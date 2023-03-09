import numpy as np
import pandas as pd


df = pd.read_csv("integralInfo.csv")
#df = pd.read_csv("integralInfo.csv", nrows=100)
print(len(df))

df["min_center"] = df[['low_center_int','hi_center_int']].min(axis=1)
df["min_max"] = df[['low_max_int','hi_max_int']].min(axis=1)

df = df[df.alpha <= 0.025]
#df = df[df.min_center > 0.25]
#df = df[df.nzero > 20]

df = df.sort_values(["min_center","alpha","X"],ascending=[True,True,True])
#df = df.sort_values(["nzero","alpha","X"],ascending=[True,True,True])

#import matplotlib.pyplot as plt
#plt.hist(df["nzero"],bins=201,range=(0,200))
#plt.show()
#plt.savefig("tmp.png")

print(df.head(50))
