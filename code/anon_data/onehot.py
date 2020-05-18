import numpy as np
import pandas as pd

from tqdm import tqdm
import yaml
import sys
import re
import xml.etree.ElementTree as et


f = open(f"{sys.argv[1]}/config.yaml")
config = yaml.load(f, Loader=yaml.FullLoader)
print(yaml.dump(config))
sys.path.append(config["analysis_name"])


def parse_range(x):
    if ":" not in x:
        x = x.split(".")
        val = int(x[0][1:])
        return val, val

    vals = re.split(':', x[1:-1])
    vals[0] = vals[0].split(".")[0]
    vals[1] = vals[1].split(".")[0]
    low = int(vals[0]) if x[0] == '[' else int(vals[0]) + 1
    high = int(vals[1]) if x[-1] == ']' else int(vals[1]) - 1
    return low, high


def get_mapping(no, algo, root, cols):
    mapping = {}
    for child, name in zip(root[3], cols):
        attr = child.attrib["name"]
        m = {}
        for v in child[0]:
            m[v.attrib["int"]] = v.attrib["cat"]
        mapping[name] = m

    return mapping


def onehot(no, algo, cols, vals, shuffled=True):
    #print(f"OneHotting for no:{no}, algo:{algo}, shuffled:{shuffled}")
    shuff = "_shuffled" if algo == "datafly" and shuffled else ""
    data = pd.read_csv(f"{config['analysis_name']}/{algo}{no}{shuff}.csv",names=cols,index_col=False)
    xml = et.parse(f"../toolbox_linux64/configs/{config['analysis_name']}/{algo}{no}{shuff}.xml")

    root = xml.getroot()
    mapping = get_mapping(no, algo, root, cols)
    new_df = pd.DataFrame()

    for c, v in zip(cols, vals):
        no_choices = v
        col = data[c]
        oh_l = []
        for x in col:
            mi, ma = parse_range(x)
            oh = [0] * no_choices
            for i in range(mi,ma+1):
                val = int(mapping[c][str(i)])
                oh[val] = 1
            oh_l.append(oh)

        cols = [c+str(i) for i in range(0, no_choices)]

        oh_df = pd.DataFrame.from_records(oh_l, columns=cols)
        new_df[cols] = oh_df

    new_df["class"] = data["class"]
    new_df.to_csv(f"{config['analysis_name']}/{algo}{no}_oh{shuff}.csv", index=False)


df = pd.read_csv(f"../../datasets/{config['dataset_path']}")
vals = []
for c in df.columns[:-1]:
    s = set(df[c])
    vals.append(len(s))
print(vals)

cols = config["cols"]
for i in tqdm(range(config["no_instances"])):

    onehot(i+1, "datafly", cols, vals,  shuffled=False)
    onehot(i+1, "mondrian", cols, vals, shuffled=True)
    onehot(i+1, "datafly", cols, vals, shuffled=True)
