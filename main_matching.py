import matching.utilities as utl
import matching.DocumentMatching as dm
import json
import os
import sys
from pathlib import Path
from multiprocessing import Pool

from typing import Iterator

from defaultvalues import *

# setup lists for all settings
similarity_measures = ["n_gram", "bag_of_words",
                       "cosine", "average", "maximum", "max_matching", "CWASA"]
sd_thresholds = [0.0, 1.5]
doc_matchings = ["max", "max_increasing_subsequence"]

header_file = f"{results_location}/header_matching.json"

# preprocessing arguments for gram and embeddings
kwargs_gram = utl.make_preprocessing_dict(remove_punctuation=True)
kwargs_embeddings = utl.make_preprocessing_dict(
    lowercase=False, remove_punctuation=True)

# output folder setup
if not os.path.exists(matching_location):
    os.makedirs(matching_location)

# check if some matchings have already been calculated
if not Path(header_file).exists():
    header = dict()
else:
    with open(header_file, 'r') as fp:
        header = json.load(fp)

# n for n-gram
n = 4

print("Start working")

articles = utl.get_article_pairs()
unnested_articles = utl.get_unnested_articles(articles)

# concatenate all article names and hash it
idf_article_string = ''.join([art.split('/')[-1]
                             for art in sorted(list(unnested_articles))])
idf_article_hash = utl.get_hash(idf_article_string)

print("ARTICLE HASH", idf_article_hash)

# check for word idf (and calculate if necessary)
found = False
word_idf = dict()
if Path(f"{results_location}/word_idf.json").exists():
    with open(f"{results_location}/word_idf.json", 'r') as fp:
        hash, word_idf = json.load(fp)
        if hash == idf_article_hash:
            found = True
            print("Word idf was already computed!")
if not found:
    word_idf = utl.calculate_full_word_idf(
        unnested_articles, **kwargs_gram)
    print("Calculated new word idf")
    with open(f"{results_location}/word_idf.json", 'w') as fp:
        json.dump([idf_article_hash, word_idf], fp, ensure_ascii=False)

# check for n-gram idf (and calculate if necessary)
found = False
n_gram_idf = dict()
if Path(f"{results_location}/{n}_gram_idf.json").exists():
    with open(f"{results_location}/{n}_gram_idf.json", 'r') as fp:
        hash, n_gram_idf = json.load(fp)
        if hash == idf_article_hash:
            found = True
            print("n_gram idf was already computed!")
if not found:
    n_gram_idf = utl.calculate_full_n_gram_idf(
        unnested_articles, n, **kwargs_gram)
    print("Calculated new n gram idf")
    with open(f"{results_location}/{n}_gram_idf.json", 'w') as fp:
        json.dump([idf_article_hash, n_gram_idf], fp, ensure_ascii=False)


def article_generator_parallel(matched_article_list: list[tuple[str, str]]) -> Iterator[tuple[str, str, str, str]]:
    """ Generator function that iteratively returns preprocessed articles.

    Args:
        matched_article_list (list[tuple[str, str]]): List of article pairs that is iterated through

    Yields:
        Iterator[[str, str,str,str]]: simple and normal link to file and preprocessed articles in the form
            simple_preprocessed(option_1), (..., simple_preprocessed(option_n)), normal_preprocessed(option_1), (..., normal_preprocessed(option_n))
    """

    for simple, normal in matched_article_list:

        with open(simple, 'r') as fp:
            simple_text = fp.read()
        with open(normal, 'r') as fp:
            normal_text = fp.read()

        # don't process exact copies
        if simple_text == normal_text:
            continue
        yield simple, normal, simple_text, normal_text


def article_preprocess(simple_text: str, normal_text: str) -> [str, str, list[str], list[str]]:
    """ Returns the preprocessed articles

    Args:
        simple_text (str): original simple text
        normal_text (str): original normal text

    Returns:
        [str,str,list[str],list[str]]: preprocessed original texts, followed by list of different preprocessing variants for both articles
    """
    simple_original = utl.get_original_text_preprocessed(simple_text)
    normal_original = utl.get_original_text_preprocessed(normal_text)
    simple_arts = []
    normal_arts = []
    preprocessing_options = [kwargs_gram, kwargs_embeddings]
    for kwargs in preprocessing_options:
        simple_arts.append(utl.preprocess(simple_text, **kwargs))
        normal_arts.append(utl.preprocess(normal_text, **kwargs))

    return simple_original, normal_original, *simple_arts, *normal_arts


def parallel(simple_name: str, normal_name: str, simple_text: str, normal_text: str) -> dict[str, list[str]]:
    """ The actual matching calculation
    This function is called by main() with multi-processing.

    Args:
        simple_name (str): name of the simple file
        normal_name (str): name of the normal file
        simple_text (str): text of the simple file
        normal_text (str): text of the normal file

    Returns:
        dict[str, list[str]]: key is a simple filename, item is a list of filenames containing corresponding results 
    """
    # get simple/normal text in original, n-gram and embedding form
    simple_original, normal_original, simple_gram, simple_embedding, normal_gram, normal_embedding = article_preprocess(
        simple_text, normal_text)

    simple_file = simple_name.split('/')[-1]
    normal_file = normal_name.split('/')[-1]

    # check if the file has already been matched
    if simple_file in header:
        finished = True
        for sim_measure in similarity_measures:
            for matching in doc_matchings:
                for sd_threshold in sd_thresholds:
                    #
                    filename = utl.make_matching_path(
                        simple_file, normal_file, sim_measure, matching, sd_threshold)
                    if filename not in header[simple_file]:
                        finished = False
                        break
                if finished == False:
                    break
            if finished == False:
                break

        # it has already been matched completely
        if finished == True:
            # no updates need to be done
            return {}
    else:
        # create a new entry for the file
        header_extension = {simple_file: []}

    # start the calculation
    for sim_measure in similarity_measures:
        if sim_measure == "n_gram":
            simple_n_tf = utl.calculate_n_gram_tf(simple_gram, n)
            normal_n_tf = utl.calculate_n_gram_tf(normal_gram, n)
            sim_matrix = dm.calculate_similarity_matrix(simple_gram, normal_gram, sim_measure, n,
                                                        simple_n_tf, normal_n_tf, n_gram_idf)

        elif sim_measure == "bag_of_words":
            simple_word_tf = utl.calculate_word_tf(simple_gram)
            normal_word_tf = utl.calculate_word_tf(normal_gram)
            sim_matrix = dm.calculate_similarity_matrix(simple_gram, normal_gram, sim_measure, n,
                                                        simple_word_tf, normal_word_tf, word_idf)

        else:
            sim_matrix = dm.calculate_similarity_matrix(
                simple_embedding, normal_embedding, sim_measure)

        for matching in doc_matchings:
            for sd_threshold in sd_thresholds:
                # get the filename
                filename = utl.make_matching_path(
                    simple_file, normal_file, sim_measure, matching, sd_threshold)
                if not os.path.exists(filename):
                    try:
                        # calculate the distance according to parameters
                        results = dm.match_documents(matching, simple_original, normal_original,
                                                     sim_matrix, sd_threshold=sd_threshold)
                    except ValueError as err:
                        print(
                            f"ValueError raised by {simple_file} - {normal_file}")
                        with open("error_log.txt", "a", encoding="utf-8") as fp:
                            fp.write(
                                f"simple_file:{simple_file} - normal_file:{normal_file}\n\tsim_measure:{sim_measure} - matching:{matching} - thresh:{sd_threshold}\n")
                            fp.write(f"{sim_matrix}")
                            fp.write("\n\n\n#####\n\n\n")
                        continue

                    # write the end result of the distance calculation
                    with open(filename, 'w') as fp:
                        json.dump(results, fp, ensure_ascii=False, indent=2)

                # add the file to the header
                header_extension[simple_file].append(filename)

    return header_extension


def main():
    """
    Calculates all pairings of similarity measures and alignment methods.

    BEWARE! Even though this calculation is computed in parallel it takes a lot of time.
    Also there are no checkpoints.
    """
    # start multi-processed matching calculation
    with Pool() as p:
        header_extensions = p.starmap(parallel, article_generator_parallel(
            articles))

        # merge all results, given a list of many headers
        for ext in header_extensions:
            for key in ext:
                if key in header.keys():
                    # merge if the key already exists
                    header[key] = header[key] + ext[key]
                else:
                    # create a new key
                    header[key] = ext[key]
        # save header with results. This could be moved elsewhere for checkpointing
        with open(header_file, 'w') as fp:
            json.dump(header, fp, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
