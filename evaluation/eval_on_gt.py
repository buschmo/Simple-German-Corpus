import os
import json
import spacy
import pickle
import pandas as pd
from itertools import product
from matplotlib import pyplot as plt


import matching.utilities as utl
# from defaultvalues import *
# from align_by_hand import prep_text

with open(website_sample_location, "rb") as f:
    samples = pickle.load(f)

sim_measures = ["average", "bag_of_words", "cosine", "CWASA", "max_matching", "maximum", "n_gram"]
matching_methods = ["max", "max_increasing_subsequence"]
sd_thresholds = [0.0, 1.5]

nlp = spacy.load("de_core_news_lg")

# results = pd.DataFrame(columns=["sim_measure", "matching_method", "thres", "correct", "precision", "recall", "F1"])
results = []


def create_gt_dict(simple_path, normal_path) -> dict:
    """
    Creates a dictionary of aligned sentences for one article.
    Args:
        path_names: list of two path names [simple article, article]

    Returns:
        Dictionary à la {simple_German_sentence: corresponding_German_sentence}
    """
    hash_easy_path, hash_normal_path = utl.make_hand_aligned_path(simple_path, normal_path)
    with open(ground_truth_location+"/".join(hash_easy_path.split("/")[1:])) as f:
        simple_article = f.read()

    with open(ground_truth_location+"/".join(hash_normal_path.split("/")[1:])) as f:
        article = f.read()

    simple_sents = simple_article.split("\n")
    normal_sents = article.split("\n")


    if len(simple_sents) != len(normal_sents):
        print(f"len(simple_sents) != len(normal_sents): "
              f"Simple {len(simple_sents)} vs. German {len(normal_sents)} "
              f"for {simple_path} or {os.path.split(hash_easy_path)[1]}")

    gt = {}
    for s, n in zip(simple_sents, normal_sents):
        gt[s] = n
    return gt


def evaluate():
    not_found = 0
    nothing_correct = 0

    # for each article from samples
    for simple_article, article in samples:
        simple_article_name = os.path.split(simple_article)[1]
        article_name = os.path.split(article)[1]

        # create ground truth dict: {simple sentence: normal sentence}
        article_gt = create_gt_dict(simple_article, article)

        # for each combination of sim_measure, matching_method, sd_threshold
        for sim, match_m, thres in product(sim_measures, matching_methods, sd_thresholds):
            name = utl.make_matching_path(simple_article_name, article_name, sim, match_m, thres)
            correct_alignments = 0
            try:
                with open(os.path.join(matching_location, os.path.split(name)[1])) as f:
                    alignments = json.load(f)
            except FileNotFoundError:
                print(f">> FileNotFoundError: for article '{article_name}' with matching path '{name}'")
                not_found += 1
                continue

            for a in alignments:
                simple_sent = a[1][0]
                normal_sent = a[1][1]
                try:
                    if article_gt[simple_sent] == normal_sent:
                        correct_alignments += 1
                except KeyError:
                    pass

            if correct_alignments > 0:
                precision = correct_alignments / len(alignments)
                recall = correct_alignments / len(article_gt)
                F1 = 2 * (precision * recall) / (precision + recall)
            else:
                precision = 0
                recall = 0
                F1 = 0
                nothing_correct += 1

            results.append({"website": article.split("/")[0],
                            "article": article_name,
                            "sim_measure": sim,
                            "matching_method": match_m,
                            "thres": thres,
                            "correct": correct_alignments,
                            "precision": precision,
                            "recall": recall,
                            "F1": F1})

    print(f"Number of files not found: {not_found}")
    print(f"Number of instances with not a single correct alignment: {nothing_correct}")
    return pd.DataFrame(results)


if __name__ == "__main__":
    results_df = evaluate()
    grouped = results_df.groupby(["sim_measure", "matching_method", "thres"]).mean()

    grouped_results = results_df.groupby(["sim_measure", "matching_method", "thres"]).mean()
    fig, ax = plt.subplots(figsize=(12, 8))
    grouped_results.plot.scatter('precision', 'recall', c='F1', s=100, cmap='plasma', fig=fig, ax=ax, edgecolor='k')
    fig.get_axes()[1].set_ylabel('F1')

    for ix, df in grouped_results.groupby(level=[0, 1, 2]):
        name = " ".join([str(entry) for entry in ix]).replace(" max_increasing_subsequence", "*").replace(
            "max_matching", "bipartite").replace(" max", " ").replace("n_gram", "4-gram").replace("bag_of_words",
                                                                                                  "bag of words")
        xy = (df["precision"].item(), df["recall"].item())
        ax.annotate(text=name, xy=xy, xytext=(10, -5), textcoords='offset points', fontsize=12)

    plt.show()