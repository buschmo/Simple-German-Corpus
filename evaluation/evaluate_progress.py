import os
import json
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
import pandas as pd
import matplotlib.pyplot as plt

from defaultvalues import *

file_matchings = set()

for root, dirs, files in os.walk(matching_location):
    for file in files:
        if file.endswith(".matches"):
            filepath = os.path.join(root, file)
            combination = file.split('--')[0]
            file_matchings.add(combination)


def get_results_done(results):
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
                    print("\t".join(file.split('--')[1:]))
                    _, v1, v2, _ = file.split('--')
                    if v1 not in res_dict:
                        res_dict[v1] = dict()
                    if v2 not in res_dict[v1]:
                        res_dict[v1][v2] = {"Precision": [], "Recall": [], "Correct sims": [], "Incorrect sims": []}
                    with open(os.path.join(root, file), 'r') as fp:
                        file_res = json.load(fp)
                    file_stats = []

                    for _, (s1, s2), sim in file_res:
                        val = res[str(s1)][str(s2)]
                        if val != None:
                            file_stats.append(val)
                            if val:
                                res_dict[v1][v2]["Correct sims"].append(sim)
                            else:
                                res_dict[v1][v2]["Incorrect sims"].append(sim)

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

    perf = pd.DataFrame(columns=["similarity_measure", "matching_strategy", "precision", "recall", "F1", "sim correct matches", "sim incorrect matches"])

    for elem in res_dict:
        for elem2 in res_dict[elem]:
            print(elem, elem2)
            print(res_dict[elem][elem2])
            prec = np.mean(res_dict[elem][elem2]["Precision"])
            rec = np.mean(res_dict[elem][elem2]["Recall"])
            F1 = 2 * (prec * rec) / (prec + rec)
            sim_correct = np.mean(res_dict[elem][elem2]["Correct sims"])
            sim_incorrect = np.mean(res_dict[elem][elem2]["Incorrect sims"])
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
                                "precision": prec, "recall": rec, "F1": F1,
                                "sim correct matches": sim_correct,
                                "sim incorrect matches": sim_incorrect}, ignore_index=True)

    print(perf.groupby(["similarity_measure"]).mean().round(2).to_latex(index=True))

    fig, ax = plt.subplots(figsize=(10, 10))

    perf.plot.scatter('precision', 'recall', c='F1', s=100, cmap='plasma', fig=fig, ax=ax, edgecolor='k')
    fig.get_axes()[1].set_ylabel('F1')
    for idx, row in perf.iterrows():
        ax.annotate(row['similarity_measure'] + row['matching_strategy'], row[['precision', 'recall']], fontsize=18,
                    xytext=(10, -5),
                    textcoords='offset points')

    plt.savefig(f"../../figures/all_evaluated.png")

    plt.show()

    for elem in res_dict:
        all_corr = []
        all_incorr = []
        for elem2 in res_dict[elem]:
            all_corr.extend(res_dict[elem][elem2]["Correct sims"])
            all_incorr.extend(res_dict[elem][elem2]["Incorrect sims"])

        plt.hist(x = [all_corr, all_incorr], label=["Correct matches", "Incorrect matches"])
        plt.title(elem)
        plt.legend()
        plt.savefig(f"../../figures/{elem}_match_stats.png")
        plt.show()

def get_matches():
    results_done = set()
    results_started = set()
    for comb in file_matchings:
        if os.path.exists(os.path.join(f"{results_location}/evaluated", comb + ".results")):
            with open(f"{results_location}/evaluated/" + comb + ".results", 'r') as fp:
                res = json.load(fp)

            if "finished" in res:
                results_done.add(comb)
            else:
                results_started.add(comb)

    print("RESULTS FINISHED:", len(results_done))
    print("RESULTS STARTED: ", len(results_started))

    get_results_done(results_done)


if __name__ == '__main__':
    get_matches()
