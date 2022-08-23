import os
import json
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

from defaultvalues import *


def get_matches(files, name=None):
    results_done = set()
    results_started = set()
    if name:
        print(name)
    for comb in files:
        if os.path.exists(os.path.join(f"{results_location}/evaluated", comb + ".results")):
            with open(f"{results_location}/evaluated/" + comb + ".results", 'r') as fp:
                res = json.load(fp)

            if "finished" in res:
                results_done.add(comb)
            else:
                results_started.add(comb)

    print("RESULTS FINISHED:", len(results_done))
    print("RESULTS STARTED: ", len(results_started))

    if len(results_done):
        get_results_done(results_done, name)


def get_results_done(results, name):
    res_dict = dict()

    for comb in results:
        all_positive = 0
        with open(f"{results_location}/evaluated/" + comb + ".results", 'r') as fp:
            res = json.load(fp)
        for elem in res:
            if elem != "finished":
                for e in res[elem]:
                    if res[elem][e]:
                        all_positive += 1

        for root, dirs, files in os.walk(matching_location):
            for file in files:
                if file.startswith(comb) and file.endswith("1.5.matches"):
                    _, v1, v2, _ = file.split('--')
                    if v1 not in res_dict:
                        res_dict[v1] = dict()
                    if v2 not in res_dict[v1]:
                        res_dict[v1][v2] = {"Precision": [], "Recall": []}
                    with open(os.path.join(root, file), 'r') as fp:
                        file_res = json.load(fp)
                    file_stats = []
                    for _, (s1, s2), _ in file_res:
                        val = res[str(s1)][str(s2)]
                        if val != None:
                            file_stats.append(val)

                    # print(file_stats)
                    # print("Precision:", np.mean(file_stats))
                    if len(file_stats):
                        res_dict[v1][v2]["Precision"].append(np.mean(file_stats))
                    else:
                        res_dict[v1][v2]["Precision"].append(0.0)
                    # print("Recall:", np.sum(file_stats) / float(all_positive))
                    if all_positive:
                        res_dict[v1][v2]["Recall"].append(np.sum(file_stats) / float(all_positive))
                    else:
                        res_dict[v1][v2]["Recall"].append(0.0)

    perf = pd.DataFrame(columns=["similarity_measure", "matching_strategy", "precision", "recall", "F1"])

    for elem in res_dict:
        for elem2 in res_dict[elem]:
            print(elem, elem2)
            prec = np.mean(res_dict[elem][elem2]["Precision"])
            rec = np.mean(res_dict[elem][elem2]["Recall"])
            F1 = 2 * (prec * rec) / (prec + rec)
            print("Average precision:", prec)
            print("Average recall:", rec)
            print("F1 score:", F1)
            elem2_short = ""
            if elem2 == "max_increasing_subsequence":
                elem2_short = "*"

            sent_sim_name = elem
            if elem == "max_matching":
                sent_sim_name = "bipartite"
            elif elem == "bag_of_words":
                sent_sim_name = "bag of words"
            elif elem == "n_gram":
                sent_sim_name = "4-gram"
                
            perf = perf.append({"similarity_measure": sent_sim_name, "matching_strategy": elem2_short,
                                "precision": prec, "recall": rec, "F1": F1}, ignore_index=True)

    fig, ax = plt.subplots(figsize=(10, 10))

    plt.title(f"Evaluation of {len(results)} files from source {name}")

    perf.plot.scatter('precision', 'recall', c='F1', s=100, cmap='plasma', fig=fig, ax=ax, edgecolor='k')
    fig.get_axes()[1].set_ylabel('F1')
    for idx, row in perf.iterrows():
        ax.annotate(row['similarity_measure'] + row['matching_strategy'], row[['precision', 'recall']], fontsize=12,
                    xytext=(10, -5),
                    textcoords='offset points')
    plt.savefig(f"../../figures/{name[4:-3]}_evaluated.png")
    plt.show()

websites = ["www.apotheken-umschau.de",
            "www.behindertenbeauftragter.de",
            "www.brandeins.de",
            "www.lebenshilfe-main-taunus.de",
            "www.mdr.de",
            "www.sozialpolitik.com",
            "www.stadt-koeln.de",
            "www.taz.de"]
string = "\n".join(["0: all websites [Default]"] + [f"{i + 1}: {website}" for i, website in enumerate(websites)])
global filtered_files

# Print out number of already evaluated results per website
website_count = [0 for _ in websites]
website_evals = [[] for _ in websites]

set_evaluated = set([file[:-8] for file in os.listdir(f"{results_location}s/evaluated")])
for i, website in enumerate(websites):
    with open(os.path.join(dataset_location, f"{website}/parsed_header.json")) as fp:
        header = json.load(fp)
        website_keys = header.keys()

    with open(f"{results_location}/header_matching.json") as fp:
        header = json.load(fp)
        set_matched = set()
        for key in header:
            if key[:-4] in website_keys:
                for file in header[key]:
                    set_matched.add(file.split("--")[0].split("/")[-1])

    print(f"{website}: {len(set_evaluated & set_matched)}")
    website_evals[i] = set_evaluated & set_matched

print(website_evals)

for evals, name in zip(website_evals, websites):
    get_matches(evals, name)
