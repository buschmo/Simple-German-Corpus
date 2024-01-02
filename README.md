# A New Aligned Simple German Corpus
This repository contains the data and code for a Simple German Corpus. 

If you use the corpus in your research, please cite our paper

```
@inproceedings{toborek-etal-2023-new,
    title = "A New Aligned Simple {G}erman Corpus",
    author = "Toborek, Vanessa  and
      Busch, Moritz  and
      Bo{\ss}ert, Malte  and
      Bauckhage, Christian  and
      Welke, Pascal",
    booktitle = "Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    month = jul,
    year = "2023",
    address = "Toronto, Canada",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2023.acl-long.638",
    pages = "11393--11412",
}

```

## About
The German language knows two versions of plain language: Einfache Sprache (Simple German) and [Leichte Sprache](https://leichte-sprache.de/), the latter being controlled by the _Netzwerk Leichte Sprache_.

Currently, there are only few works that build a parallel corpus between Simple German and German and the corresponding data is often not available. Such a (potentially expanded) corpus may be used to implement automatic machine learning translation from German to Simple German. While the data might currently not be sufficient, the goal of this work is to lay the foundations for such a corpus by:

1. Scraping websites with parallel versions for German and Simple German
2. Implementing various algorithms presented in the literature to form a corpus that contains aligned, "translated" sentences.


## Installation

We recommend creating a virtual python environment, e.g. using anaconda

```
conda create -n simple-german python=3.10
```

and installing the required packages

```
conda activate simple-german
pip install -r requirements
python -m spacy download de_core_news_lg
```

Before using the repo, you **must** edit the file `defaultvalues.py`.
Within it, you need to define the variable `repository_location`, the absolute path to the folder of this repository. E.g. `dataset=/home/bob/Simple-German-Corpus`.
You can also change any of the other variables.

You may also use the *untested* `environment.yml` for a direct conda installation
```
conda env create --file environments.yml
```

## Usage

Please note, that downloading is throttled by a 5 second delay to reduce network traffic.
You can change this in `crawler/utilities.py`


To run the whole code, simply setup the environment and run `python main.py`.
This calls both `main_crawler.py` as well as `main_matching.py`.
The crawler downloads the archived websites and parses all contents.
The matcher calculates all corresponding match distances.
**Beware that the latter might take a lot of time, even though it is parallelized**.
The end result can be found in the `results/` folder.


To run other code, i.e. `evaluate.py` in the `evaluation` folder, use `python -m evaluation.evaluate`.
For manual alignment `python -m evaluation.align_by_hand` might come in handy.
*(This tool is by no means fully fleshed out)*


## Tools/Libraries
The code was written using python version 3.10.4.\
All python packages needed to run the code can be found in the "requirements" file and installed using
`pip install -r requirements`.
We recommend using a virtualenv.
- [spacy.io](https://spacy.io/) python library for natural language processing supporting a plethora of languages, including [German](https://spacy.io/models/de)
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) python library for html parsing / crawling.
