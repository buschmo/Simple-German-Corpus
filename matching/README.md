# Matching folder
This folder contains all files for the calculation of sentence similarity and matching sentences.
As it stands, various preprocessing options, six similarity measures and two alignment strategies have been implemented:

#### Preprocessing options in `utility.py`
- remove_hyphens: removes hyphens of the form '-[A-Z]' (often found in Simple German) from the text. E.g., Bürger-Meister becomes Bürgermeister
- lowercase: lowercases the text
- remove_gender: removes German gendering endings like \*in, \*innen (with \*, _, : and "Binnen-I" (BäckerInnen))
- lemmatization: lemmatizes the text
- spacy_sentences: should be the standard behavior: Lets spacy determine sentence borders
- remove_stopwords: removes stopwords (very common words) for German as defined internally by spacy
- remove_punctuation: Removes punctuation marks

#### Similarity measures in `SimilarityMeasures.py`
- bag of words similarity with TF*IDF weighting
- character n-gram similarity with TF*IDF weighting
- cosine similarity with averaged word embedding vectors
- average similarity with averaged similarities between all pairs of words
- maximal similarity with max matching in both directions and average of the two obtained values
- maximum matching similarity, calculating a maximum matching between the sentences and averaging its similarity
- CWASA similarity, that calculates maximum matchings for each word, does not allow i-j and j-i matchings, and averages the obtained similarity values (see paper for details)

#### Alignment strategies in `DocumentsMatching.py`
- Maximal alignment, that matches each sentence of the Simple sentences to its maximal match in the standard sentences
- Maximal increasing alignment, that works like Maximal alignment, but forces the alignment to keep the order of information

Both alignment strategies allow to introduce a minimum matching threshold, i.e., the minimal similarity value for which we allow matching between sentences. This can be set either as an absolute value or as dependent on mean and standard deviation of the data (i.e., mean + factor*std, where factor can be set by the user) 
