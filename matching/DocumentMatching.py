import numpy as np
from spacy.tokens.doc import Doc

import matching.SimilarityMeasures as measures


def match_documents(matching: str, simple_doc: list[Doc], normal_doc: list[Doc], match_matrix, threshold=0.0, sd_threshold=0.0) \
        -> list[list[tuple[str, str], tuple[str, str]]]:
    """ Wrapper for choosing max matching or max increasing subsequence matching
    """
    if matching == "max":
        return match_documents_max(simple_doc, normal_doc, match_matrix, threshold, sd_threshold)
    elif matching == "max_increasing_subsequence":
        return match_documents_max_increasing_subsequence(simple_doc, normal_doc, match_matrix, threshold, sd_threshold)


# TODO: Add possibility to link original sentences to preprocessed ones!
def match_documents_max(simple_doc: list[Doc], normal_doc: list[Doc], match_matrix: np.ndarray, threshold: float = 0.0, sd_threshold: float = 0.0) \
        -> list[list[tuple[int, int], tuple[str, str], float]]:
    """ Calculates maximum matches for each simple sentence and returns the list of matched sentences.
    Please note that this only allows 1-to-n-matching. Taken from CATS

    Args:
        simple_doc (list[Doc]): The simple document in preprocessed format
        normal_doc (list[Doc]): The normal document in preprocessed format
        match_matrix (np.ndarray): A matrix with similarity scores for the sentences in the documents (simple_sentence x normal_sentence)
        threshold (float, optional): Minimum matching threshold, is different for different kinds of matching algorithms.
        sd_threshold (float, optional): Calculates the mean and standard deviation of all sentence similarities and sets the threshold to mean+(sd_threshold*std)

    Returns:
        list[list[tuple[int, int], tuple[str, str], float]]: A list of matched sentences with their indices and their similarity value
            Form: ((i,j), (simple_i, normal_j), distance)
    """

    if sd_threshold > 0.0:
        std = np.std(match_matrix)
        mean = np.mean(match_matrix)
        threshold = max(threshold, mean + (sd_threshold * std))

    max_values = np.argmax(match_matrix, axis=1)

    # converting to int makes them serializable
    return [[(int(i), int(j)), (str(simple_doc[i]), str(normal_doc[j])), match_matrix[i, j]] for i, j in enumerate(max_values) if
            match_matrix[i, j] > threshold]


def match_documents_max_increasing_subsequence(simple_doc: list[Doc], normal_doc: list[Doc], match_matrix: np.ndarray, threshold: float = 0.0, sd_threshold: float = 0.0) \
        -> list[list[tuple[int, int], tuple[str, str], float]]:
    """
    Calculates maximum matches for each simple sentence, then returns the longest increasing subsequence
    (assumes order of information is kept)
    Please note that this only allows 1-to-n-matching. Taken from CATS

    Args:
        simple_doc (list[Doc]): The simple document in preprocessed format
        normal_doc (list[Doc]): The normal document in preprocessed format
        match_matrix (np.ndarray): A matrix with similarity scores for the sentences in the documents
        threshold (float, optional): Minimum matching threshold, is different for different kinds of matching algorithms.
        sd_threshold (float, optional): Calculates the mean and standard deviation of all sentence similarities and sets the threshold to mean+(sd_threshold*std). If > 0, overwrites threshold

    Returns:
        list[list[tuple[int, int], tuple[str, str], float]]: A list of matched sentences with their indices and their similarity value
            Form: ((i,j), (simple_i, normal_j), distance)
    """

    # Overwrite threshold, when sd_threshold is given
    if sd_threshold > 0.0:
        std = np.std(match_matrix)
        mean = np.mean(match_matrix)
        threshold = max(threshold, mean + (sd_threshold * std))

    simple_matchings = match_documents_max(
        simple_doc, normal_doc, match_matrix, threshold, sd_threshold)

    simple_indices = [match[0][0] for match in simple_matchings]
    normal_indices = [match[0][1] for match in simple_matchings]

    if len(simple_matchings) == 0:
        return []

    simple_longest_indices, normal_longest_indices = get_longest_increasing_subsequence(
        simple_matchings)

    final_matching = []

    start_border = 0
    end_border = normal_longest_indices[0]
    last_found = -1

    for i, elem in enumerate(simple_indices):
        # if simple index appears in longest subseq
        if elem in simple_longest_indices:
            assert match_matrix[elem][normal_indices[i]] > threshold
            final_matching.append((elem, normal_indices[i]))
            last_found += 1
            start_border = normal_longest_indices[last_found]
            # if not all have been found yet
            if last_found < len(normal_longest_indices) - 1:
                # border interval lies between two indices
                end_border = normal_longest_indices[last_found + 1]
            else:
                # border interval lies between last index and end
                end_border = len(match_matrix[0]) - 1
        # align unaligned snippet (see CATS for details)
        else:
            max_val_ind = np.argmax(
                match_matrix[i][start_border:end_border + 1])
            val = match_matrix[i][start_border + max_val_ind]
            if val > threshold:
                final_matching.append((elem, start_border + max_val_ind))
                start_border += max_val_ind

    # converting i and j to int makes them json serializable
    return [[(int(i), int(j)), (str(simple_doc[i]), str(normal_doc[j])), match_matrix[i, j]] for i, j in final_matching if
            match_matrix[i, j] > threshold]


def get_longest_increasing_subsequence(simple_matchings: list[tuple[tuple[str, str], tuple[str, str], float]]) \
        -> tuple[list[str], list[str]]:
    """ Calculates the longest increasing subsequence within a given matching

    Args:
        simple_matching (list[tuple[tuple[str, str], tuple[str, str], float]]): list containing matching information of the form
            ((simple_index, normal_index), (simple_sentence, normal_sentence), distance)
    Returns:
        tuple[list[str], list[str]]: list of index matching tuples giving the longest increasing subsequence
    """
    simple_indices = [match[0][0] for match in simple_matchings]
    normal_indices = [match[0][1] for match in simple_matchings]

    lis = [1] * len(normal_indices)

    # calculate the length of every sequence by looking at the previous indices
    for i in range(1, len(normal_indices)):
        for j in range(0, i):
            # if a previous index is non increasing, increment the sequence length if the found one is longer
            if normal_indices[i] >= normal_indices[j] and lis[i] < lis[j] + 1:
                lis[i] = lis[j] + 1

    start = np.argmax(lis)

    simple_ind_subseq = []
    subseq = []

    val = normal_indices[start]
    current_lis = lis[start] + 1

    # find the subsequence's indices by reverse walking through the lists
    for i in range(start, -1, -1):
        # added to subsequence if it's value is non increasing and it's longest sequence position is one less than the current one
        if normal_indices[i] <= val and lis[i] == current_lis - 1:
            subseq.insert(0, normal_indices[i])
            simple_ind_subseq.insert(0, simple_indices[i])
            # update current value, reduce length of missing sequence
            val = normal_indices[i]
            current_lis = lis[i]

    return simple_ind_subseq, subseq


def calculate_similarity_matrix(simple_doc: list[Doc], normal_doc: list[Doc], similarity_measure: str, n:int=4,
                                tf1: dict[str, float] = None, tf2: dict[str, float] = None, idf: dict[str, float] = None) -> np.ndarray:
    """ Calculates the matrix of similarity scores for each sentence pairing

    Args:
        simple_doc (list[Doc]): A preprocessed document in simple German
        normal_doc (list[Doc]): A preprocessed document in normal German
        similarity_measure (str): A similarity measure from the list of possible similarity measures, can be n_gram, bag_of_words, cosine, average, maximum, max_matching, and CWASA
        n (int, optional): needed for n-grams
        tf1 (dict[str, float], optional): Needed for tfidf similarity measures
        tf2 (dict[str, float], optional): Needed for tfidf similarity measures
        idf (dict[str, float], optional): Needed for tfidf similarity measures

    Returns:
        np.ndarray: A len(doc1), len(doc2)-Matrix with similarity scores for both documents
    """
    match_matrix = np.zeros(shape=(len(simple_doc), len(normal_doc)))

    for i, sent1 in enumerate(simple_doc):
        for j, sent2 in enumerate(normal_doc):

            value = 0.0

            if similarity_measure == "n_gram":
                assert tf1 is not None and tf2 is not None and idf is not None
                value = measures.n_gram_similarity(
                    sent1, sent2, tf1, tf2, idf, n)
            elif similarity_measure == "bag_of_words":
                assert tf1 is not None and tf2 is not None and idf is not None
                value = measures.bag_of_words_tf_idf_similarity(
                    sent1, sent2, tf1, tf2, idf)
            elif similarity_measure == "cosine":
                value = measures.cosine_similarity(sent1, sent2)
            elif similarity_measure == "average":
                value = measures.average_similarity(sent1, sent2)
            elif similarity_measure == "maximum":
                value = measures.max_similarity(sent1, sent2)
            elif similarity_measure == "max_matching":
                value = measures.max_matching_similarity(sent1, sent2)
            elif similarity_measure == "CWASA":
                value = measures.CWASA_similarity(sent1, sent2)
            else:
                print(
                    f"Similarity measure {similarity_measure} not known and/or not implemented")

            match_matrix[i, j] = value

    return match_matrix
