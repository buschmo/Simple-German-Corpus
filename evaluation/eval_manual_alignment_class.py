# %%
import os
import json
import numpy as np
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from collections import defaultdict

import matching.utilities as utl
from defaultvalues import repository_location, dataset_location

websites = ["www.apotheken-umschau.de",
            "www.behindertenbeauftragter.de",
            "www.brandeins.de",
            "www.lebenshilfe-main-taunus.de",
            "www.mdr.de",
            "www.sozialpolitik.com",
            "www.stadt-koeln.de",
            "www.taz.de"]


def evaluate_manual_classification() -> list[tuple[str, pd.DataFrame]]:
    """
    Function that reads the result files in results/evaluated and calculates the precision for each combination of
    similarity measure and matching method.

    Returns:
        list[tuple[str, pd.DataFrame]]: list of tuples containing the website's name and the corresponding DataFrame
        with the results
    """
    results = []
    # header_matching.json contains for each article the names of the corresponding match files
    with open(Path(repository_location, "results/header_matching.json"), "r", encoding="utf-8") as f:
        all_matches = json.load(f)

    # load all results from the manual alignment classification
    all_evaluated_articles = [file[:-len(".results")] if file.endswith(".results") else file for file in os.listdir(Path(repository_location, "results/evaluated"))]
    used_result_files = []

    # create a lookup to get the article name given the hash
    lookup = defaultdict()
    for key, values in all_matches.items():
        for result_file in values:
            file_hash = result_file.split("--")[0].split("/")[-1]
            lookup[file_hash] = key

    # start iterating over all websites
    for site in websites:
        website_results = defaultdict(lambda: defaultdict(list))

        # get the result files for the articles from this website
        relevant_matches = [entry for entry in all_evaluated_articles if entry in lookup.keys() and site[len("www."):] in lookup[entry]]

        for result_file in relevant_matches:
            used_result_files.append(result_file)
            try:
                with open(Path(repository_location, "results/evaluated", result_file), "r", encoding="utf-8") as f:
                    eval_results = json.load(f)
            except FileNotFoundError:
                with open(Path(repository_location, "results/evaluated", result_file + ".results"), "r", encoding="utf-8") as f:
                    eval_results = json.load(f)
            # skip all evaluation files that are not finished
            if not eval_results.get("finished", False):
                # print(f"This result file is rubbish: {result_file} correspondig to {lookup[result_file]}")
                continue

            for matches in all_matches[lookup[result_file]]:
                # skip all matches not with threshold 1.5
                if not matches.endswith("1.5.matches"):
                    continue

                # TODO: incorporate changes for sbert
                # for now, skip all .matches files that contain matches from sbert
                if "sbert" in matches:
                    print()
                    continue

                # open the corresponding match file
                with open(Path(repository_location, matches), "r", encoding="utf-8") as fp:
                    match_file = json.load(fp)
                # save information from filename about used similarity measure and matching method
                _, sim, match_m, _ = matches.split("/")[-1].split("--")

                file_statistics = []
                # now iterate over all sentence pairs in the match file
                for _, (s1, s2), _ in match_file:
                    try:
                        # only append true if both sentences are as sentence pair in the results file
                        # and they are correctly matched
                        val = eval_results.get(str(s1), False).get(str(s2), False)
                        file_statistics.append(bool(val))
                    except AttributeError:
                        file_statistics.append(False)

                # calculate mean precision
                if len(file_statistics):
                    website_results[sim][match_m].append(np.mean(file_statistics))
                else:
                    website_results[sim][match_m].append(0.0)

        # create a clean DataFrame with all results
        perf = pd.DataFrame(columns=["similarity_measure", "matching_strategy", "precision"])
        for similarity in website_results:
            for matching_method in website_results[similarity]:
                precision = np.mean(website_results[similarity][matching_method])

                # do some renaming here
                sim_name = similarity
                if similarity == "max_matching":
                    sim_name = "bipartite"
                elif similarity == "bag_of_words":
                    sim_name = "bag of words"
                elif similarity == "n_gram":
                    sim_name = "4-gram"

                match_name = "MST" if matching_method == "max" else "MST-LIS"

                perf = perf.append({"similarity_measure": sim_name, "matching_strategy": match_name,
                                    "precision": precision}, ignore_index=True)

        results.append((site, perf))
    return results


# %%
if __name__ == "__main__":
    results = evaluate_manual_classification()

    # now use the results and make a nice plot out of them
    dfs = [d[1] for d in results]
    new_df = pd.concat(dfs)
    df_out = new_df.groupby(["similarity_measure", "matching_strategy"]).mean()

    fig, ax = plt.subplots(figsize=(9, 8))
    df_out.unstack().sort_values(by=[("precision", "MST-LIS")], ascending=True).plot.bar(rot=45, fig=fig, ax=ax, color=["xkcd:green", "xkcd:azure"], alpha=0.55, edgecolor=["xkcd:green", "xkcd:azure"])
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[0:], labels=["MST", "MST-LIS"])
    ax.set_ylabel("Manual Alignment Classification Accuracy")
    ax.set_xlabel("")
    plt.tight_layout()
    plt.show()
    # plt.savefig(all_accuracies.png', dpi=250)

