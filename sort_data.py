import os
import pandas as pd

# for idx, it in enumerate(sorted(os.listdir("txt"))):
#     new_name = str(idx + 1) + ".txt"
#     os.rename(os.path.join("txt", it), os.path.join("txt", new_name))
a = []
for filename in sorted(os.listdir("txt")):
    stt = filename.split(".")[0]
    a.append(stt)

stt = []
years = []
title = []

df = pd.read_csv("metadata.csv")

with open("metadata.csv", "r+") as f:
    all_file = f.readlines()
    for idx, text_file in enumerate(all_file):
        if idx == 0:
            continue
        file_ele = text_file.split(",")
        print(file_ele)
        if file_ele[0] in a:
            stt.append(str(file_ele[0]) + ".txt")
            line_2 = df.values[idx - 1][2]
            # line_2 = file_ele[2].translate({ord(c): None for c in '"'})
            years.append(line_2)
            line = df.values[idx - 1][3]
            title.append(line)
            print(text_file)

dict = {"filename": stt, "years": years, "title": title}

df = pd.DataFrame(dict)
df.to_csv("final.csv")
