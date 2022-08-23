import os
import re
import spacy
import matching.utilities as utl
from defaultvalues import *
import json

nlp = spacy.load("de_core_news_lg")

def get_tokens(text):
    text = "".join(text).replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    # all_tokens = []
    # for s in nlp(text).sents:
    #     all_tokens += [token.text for token in s if not token.is_punct]

    all_tokens = [str(w) for w in nlp(text) if not w.is_punct]
    return all_tokens


""" Prints the number of aligned sentences
"""

website_hashes = utl.get_website_hashes()
counter = {}
counter_tokens = {}
total_tokens = 0
sentences = 0
for website in website_hashes:
    counter[website] = 0
    counter_tokens[website] = 0
    for hash in website_hashes[website]:
        path = f"{results_location}/alignment/{hash}.normal"
        if os.path.exists(path):
            with open(path) as fp:
                lines = fp.readlines()
                # counter[website] += len(lines)
                counter[website] += len(set(lines))
                # tokens = len(get_tokens(lines))
                tokens = len(get_tokens(set(lines)))
                counter_tokens[website] += tokens
                # sentences += len(lines)
                sentences += len(set(lines))
                total_tokens += tokens
        # else:
        #     print(f"Not found {hash}")
    print(f"{website} = {counter[website]} sentences and {counter_tokens[website]} tokens")

print(f"Overall sentences: {sentences}\nOverall tokens: {total_tokens}")