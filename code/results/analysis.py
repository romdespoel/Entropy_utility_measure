import pandas as pd
import numpy as np
import xml.etree.ElementTree as et
import xmltodict as xdict

import sys
import yaml

f = open(sys.argv[1])
config = yaml.load(f, Loader=yaml.FullLoader)
print(config)
sys.path.append(config["analysis_name"])

from metrics.diameter_metric import diam_metric
from metrics.classification_metric import class_metric
from metrics.entropy import cond_entr_metric
from metrics.hierarchy_metrics import precision_metric
from metrics.information_loss_metrics import discern_metric, IL_metric
from RFCs_train import train_test

def load_csv(algo, no, original_oh=False, bounded=False):
    if original_oh:
        data = pd.read_csv(f"../anon_data/{config['analysis_name']}/original_oh.csv")
    elif bounded:
        cols = config["cols"]
        data = pd.read_csv(f"../anon_data/{config['analysis_name']}/{algo}{no}.csv",
            names=cols)
    else:
        data = pd.read_csv(f"../anon_data/{config['analysis_name']}/{algo}{no}_oh.csv")
    if not bounded:
        data.drop("Unnamed: 0", axis=1, inplace=True)
    return data

def load_config(algo, no):
    xml = et.parse(f"../toolbox_linux64/configs/{config['analysis_name']}/{algo}{no}.xml")
    root = xml.getroot()
    return root

QIs = config["cols"][:-1]

orig_data = load_csv("", 0, original_oh=True)
full_anon = orig_data.copy()
full_anon.replace(0, 1, inplace=True)

max_H = cond_entr_metric(orig_data, full_anon, QIs)

results = {}
for no in range(1, config["no_instances"]+1):

    for algo in config["algos_used"]:
        r = {}
        anon_data = load_csv(algo, no)
        conf = load_config(algo, no)
        bounded_data = load_csv(algo, no, bounded=True)

        r["precision"] = precision_metric(bounded_data, algo, no, conf)
        r["dm"] = diam_metric(anon_data)
        r["cm"] = class_metric(anon_data)
        r["entropy"] = cond_entr_metric(orig_data, anon_data, QIs)/max_H
        r["discern"] = discern_metric(anon_data)
        r["ilm"] = IL_metric(anon_data, QIs)
        #r["acc"] = train_test(orig_data, anon_data)


        print(no, algo, r)
        results[(algo, no)] = r

print(results)
df = pd.DataFrame.from_dict(results, orient='index')
df.to_csv(f"{config['analysis_name']}/metrics.csv",
            index_label=["algo","no"])
