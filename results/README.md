# Results folder

We share the manually created ground truth alignments used for the first evaluation and the results from our second manual evaluation. 
- `hand_aligned/`: contains two files per evaluated article with all Simple German sentences in the `.simple` file and the German sentences at the corresponding line in the corresponding `.normal` file.
- `evaluated/`: contains the results from the manual evaluation of the sentence matchings. The files should be opened as json files, containing each match of the algorithm variant and whether it was identified as false or true match by the annotators.
- `website_samples.pkl`: pickle file containing the subset of sampled articles for the hand aligned sentences.