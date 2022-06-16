from pathlib import Path
import os
import json

import matching.utilities as utl


def main():
    """ This function generates all alignments according to sepcific parameters
    """

    # Parameters for generation
    sim_measure = "maximum"
    sd_threshold = 1.5
    doc_matching = "max_increasing_subsequence"

    # setup
    pairs = utl.get_article_pairs()
    if not os.path.isdir("results/alignment"):
        os.makedirs("results/alignment")

    alignment = {}
    for matching_simple, matching_normal in pairs:
        # get filenames and get the path to the matching calculated by main_matching.py
        simple_file = matching_simple.split("/")[-1]
        normal_file = matching_normal.split("/")[-1]
        name = utl.make_matching_path(
            simple_file, normal_file, sim_measure, doc_matching, sd_threshold)

        easy_lines = []
        normal_lines = []
        with open(name) as fp:
            matches = json.load(fp)
            for match in matches:
                # read information of the matches
                i_normal = match[0][1]  # index of the normal sentence
                sentence_pair = match[1]
                distance = match[2]

                easy_lines.append(sentence_pair[0])
                normal_lines.append(sentence_pair[1])
                # add the alignment to logging
                if not normal_file in alignment:
                    # first alignment of the normal filee
                    alignment[normal_file] = {
                        i_normal: [{"sent": sentence_pair, "dist": distance}]
                    }
                elif not i_normal in alignment[normal_file]:
                    # first time the specific index was used
                    alignment[normal_file][i_normal] = [
                        {"sent": sentence_pair, "dist": distance}]
                else:
                    # both the normal file and the index were logged before
                    alignment[normal_file][i_normal].append(
                        {"sent": sentence_pair, "dist": distance})
        align_simple, align_normal = utl.make_alignment_path(
            simple_file, normal_file)
        with open(align_simple, "w", encoding="utf-8") as fp_simple, open(align_normal, "w", encoding="utf-8") as fp_normal:
            fp_simple.write("\n".join(easy_lines))
            fp_normal.write("\n".join(normal_lines))

    # save all logged alignments for comprehensibility reasons
    with open("results/alignments_with_distance.json", "w", encoding="utf-8") as fp:
        json.dump(alignment, fp, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
