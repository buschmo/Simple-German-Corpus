import re

import matching.utilities as util
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from defaultvalues import *
import pandas as pd


def test_number_of_files():
    with open(f"{results_location}/header_matching.json") as fp:
        header = json.load(fp)
        print(f"Total number of evaluated files: {len(set(header.keys()))}")

    total_simple_set = set()
    total_normal_set = set()

    for root, dirs, files in os.walk(dataset_location):
        for name in files:
            if name == 'parsed_header.json':
                with open(os.path.join(root, name), 'r') as fp:
                    data = json.load(fp)
                root_set_simple = set()
                root_set_normal = set()
                for fname in data:
                    if 'matching_files' not in data[fname]:
                        continue
                    if 'easy' not in data[fname]:
                        continue
                    if not data[fname]['easy']:
                        continue
                    total_simple_set.add(fname)
                    root_set_simple.add(fname)
                    total_normal_set = total_normal_set.union(set(data[fname]['matching_files']))
                    root_set_normal = root_set_normal.union(set(data[fname]['matching_files']))

                print(f"For source {root} we have {len(root_set_simple)} simple and {len(root_set_normal)} "
                      f"normal articles")

    print(
        f"There are {len(total_simple_set)} Simple German and {len(total_normal_set)} normal German articles in the dataset.")


def test_identical():
    article_pairs = util.get_article_pairs()

    different_articles = []

    not_found = 0

    for (art1, art2) in article_pairs:
        try:
            with open(art1, 'r') as fp:
                article1 = fp.read()
            with open(art2, 'r') as fp:
                article2 = fp.read()
        except FileNotFoundError:
            not_found += 1
            continue

        if article1 == article2:
            continue
        else:
            different_articles.append((art1, art2))

    percentage_correct = len(different_articles) / (float(len(article_pairs)) - not_found)

    print(
        f"There are {len(different_articles)} article pairs that are not identical, which is {round(percentage_correct * 100, 2)} "
        f"percent of all found article pairs.")

    return percentage_correct, different_articles


def test_lengths(article_pairs=None, plot=False):
    if not article_pairs:
        _, article_pairs = test_identical()

    stats = dict()

    len_simple = []
    len_normal = []

    sents_simple = []
    sents_normal = []

    length_sents_simple = []
    length_sents_normal = []

    length_sents_words_simple = []
    length_sents_words_normal = []

    words_simple = []
    words_normal = []

    len_words_simple = []
    len_words_normal = []

    for (art_simple, art_complex) in article_pairs:
        url = art_simple.split('/')[-1][:8]
        if url not in stats:
            stats[url] = {"len_simple": [], "len_normal": [], "sents_simple": [],
                          "sents_normal": [], "length_sents_simple": [],
                          "length_sents_normal": [], "length_sents_words_simple": [],
                          "length_sents_words_normal": [], "words_simple": [], "words_normal": [],
                          "len_words_simple": [], "len_words_normal": [],
                          "tokens_simple": [], "tokens_normal": []}
        with open(art_simple, 'r') as fp:
            article1 = fp.read()
            len_simple.append(len(article1))
            stats[url]["len_simple"].append(len(article1))
            article1 = article1.replace('\n', ' ')
            article1 = re.sub('\s+', ' ', article1)

            nlp1 = util.nlp(article1)
            sents_simple.append(len(list(nlp1.sents)))
            stats[url]["sents_simple"].append(len(list(nlp1.sents)))
            length_sents_simple.extend([len(str(x)) for x in nlp1.sents])
            stats[url]["length_sents_simple"].extend([len(str(x)) for x in nlp1.sents])
            length_sents_words_simple.extend([len(x) for x in nlp1.sents])
            stats[url]["length_sents_words_simple"].extend([len(x) for x in nlp1.sents])
            words = set()
            for word in nlp1:
                if word.is_punct:
                    continue
                words.add(str(word))
                len_words_simple.append(len(str(word)))
                stats[url]["len_words_simple"].append(len(str(word)))
                stats[url]["tokens_simple"].append(str(word))
            words_simple.append(len(words))
            stats[url]["words_simple"].append(len(words))

        with open(art_complex, 'r') as fp:
            article2 = fp.read()
            len_normal.append(len(article2))
            stats[url]["len_normal"].append(len(article2))
            article2 = article2.replace('\n', ' ')
            article2 = re.sub('\s+', ' ', article2)

            nlp2 = util.nlp(article2)
            sents_normal.append(len(list(nlp2.sents)))
            stats[url]["sents_normal"].append(len(list(nlp2.sents)))
            length_sents_normal.extend([len(str(x)) for x in nlp2.sents])
            stats[url]["length_sents_normal"].extend([len(str(x)) for x in nlp2.sents])
            length_sents_words_normal.extend([len(x) for x in nlp2.sents])
            stats[url]["length_sents_words_normal"].extend([len(x) for x in nlp2.sents])
            words = set()
            for word in nlp2:
                if word.is_punct:
                    continue
                words.add(str(word))
                len_words_normal.append(len(str(word)))
                stats[url]["len_words_normal"].append(len(str(word)))
                stats[url]["tokens_normal"].append(str(word))
            words_normal.append(len(words))
            stats[url]["words_normal"].append(len(words))

    print(f"The average length of the Simple German articles is {np.round(np.mean(len_simple), 1)} characters "
          f"(std: {np.round(np.std(len_simple), 1)}, median: {np.round(np.median(len_simple), 1)}).\n"
          f"The average length of the standard German articles is {np.round(np.mean(len_normal), 1)} characters "
          f"(std: {np.round(np.std(len_normal), 1)}, median: {np.round(np.median(len_normal), 1)}).\n"
          f"Only non-duplicate articles are taken into account.")

    print(f"The average number of words in Simple German articles is {np.round(np.mean(words_simple), 1)}. "
          f"(std: {np.round(np.std(words_simple), 1)}, median: {np.round(np.median(words_simple), 1)}).\n"
          f"The average number of words in standard German articles is {np.round(np.mean(words_normal), 1)} "
          f"(std: {np.round(np.std(words_normal), 1)}, median: {np.round(np.median(words_normal), 1)}).\n"
          f"Only non-duplicate articles are taken into account.")

    print(
        f"The average length of the words in Simple German articles is {np.round(np.mean(len_words_simple), 1)} characters "
        f"(std: {np.round(np.std(len_words_simple), 1)}, median: {np.round(np.median(len_words_simple), 1)}).\n"
        f"The average length of the words in standard German articles is {np.round(np.mean(len_words_normal), 1)} characters "
        f"(std: {np.round(np.std(len_words_normal), 1)}, median: {np.round(np.median(len_words_normal), 1)}).\n"
        f"Only non-duplicate articles are taken into account.")

    print(
        f"The average number of sentences in Simple German articles is {np.round(np.mean(sents_simple), 1)} "
        f"(std: {np.round(np.std(sents_simple), 1)}, median: {np.round(np.median(sents_simple), 1)}).\n"
        f"The average number of sentences in standard German articles is {np.round(np.mean(sents_normal), 1)} "
        f"(std: {np.round(np.std(sents_normal), 1)}, median: {np.round(np.median(sents_normal), 1)}).\n"
        f"Only non-duplicate articles are taken into account.")

    print(
        f"The average length of sentences in Simple German articles is {np.round(np.mean(length_sents_simple), 1)} characters "
        f"(std: {np.round(np.std(length_sents_simple), 1)}, median: {np.round(np.median(length_sents_simple), 1)}).\n"
        f"The average length of sentences in standard German articles is {np.round(np.mean(length_sents_normal), 1)} characters "
        f"(std: {np.round(np.std(length_sents_normal), 1)}, median: {np.round(np.median(length_sents_normal), 1)}).\n"
        f"Only non-duplicate articles are taken into account.")

    print(
        f"The average length of sentences in words in Simple German articles is {np.round(np.mean(length_sents_words_simple), 1)} "
        f"(std: {np.round(np.std(length_sents_words_simple), 1)}, median: {np.round(np.median(length_sents_words_simple), 1)}).\n"
        f"The average length of sentences in words in standard German articles is {np.round(np.mean(length_sents_words_normal), 1)} "
        f"(std: {np.round(np.std(length_sents_words_normal), 1)}, median: {np.round(np.median(length_sents_words_normal), 1)}).\n"
        f"Only non-duplicate articles are taken into account.")

    """
        \\begin{tabular}{lll}
      \\toprule
            name &    mask &    weapon \\\\
      \\midrule
         Raphael &     red &       sai \\\\
       Donatello &  purple &  bo staff \\\\
     \\bottomrule
     \end{tabular}
    """

    print("\\begin{tabular}{lllllllllllll}")
    print("\\toprule")
    options = ["len_simple", "len_normal", "sents_simple",
                          "sents_normal", "length_sents_simple",
                          "length_sents_normal", "length_sents_words_simple",
                          "length_sents_words_normal", "words_simple", "words_normal",
                          "len_words_simple", "len_words_normal", "tokens_simple", "tokens_normal"]
    print(" & ".join(options) + " \\\\")
    for elem in stats.keys():
        print(elem + " & " + " & ".join([str(np.round(np.mean(stats[elem][x]))) for x in options[:-2]]) + f" & {len(stats[elem]['tokens_simple'])} & {len(stats[elem]['tokens_normal'])}" + " \\\\")

    print("\\bottomrule\n\\end{tabular}")
    print()


    if plot:
        combined_data = [len_simple, len_normal]
        plt.hist(combined_data, bins=20, range=(0, 20000), label=['Simple German', 'Standard German'],
                 color=['red', 'blue'], stacked=False)
        plt.legend()
        plt.title('Length of German articles')

        plt.show()

        combined_data = []
        combined_data.append(words_simple)
        combined_data.append(words_normal)

        plt.hist(combined_data, bins=20, range=(0, 3000), label=['Simple German', 'Standard German'],
                 color=['red', 'blue'], stacked=False)
        plt.legend()
        plt.title('Number of words in German articles')

        plt.show()

        combined_data = []
        combined_data.append(len_words_simple)
        combined_data.append(len_words_normal)

        plt.hist(combined_data, range=(0, 25), label=['Simple German', 'Standard German'],
                 color=['red', 'blue'], stacked=False)
        plt.legend()
        plt.title('Length of words in German articles')

        plt.show()


if __name__ == '__main__':
    print("Working")

    test_number_of_files()

    percentage_correct, different_arts = test_identical()

    test_lengths(different_arts, plot=False)

import sys

sys.exit(0)
