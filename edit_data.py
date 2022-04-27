import os
import pandas as pd

df = pd.read_csv("final.csv")

for idx, row in df.iterrows():
    os.rename("txt/" + row["filename"], "txt/" + str(idx + 1) + ".txt")
    df.at[idx, "filename"] = str(idx + 1)+'.txt'

df.to_csv("final_1.csv")
