# %%
import re
import spacy
import matching.utilities as util
nlp = spacy.load("de_core_news_lg")


def prep_text(text):
    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    sents = [str(sent) for sent in nlp(text).sents]
    return sents


def read_articles(article_list: list[tuple[str, str]], sentence_split: bool = True) -> list[list[list[str], list[str]]]:
    """
    Takes a list of tuples with (path_to_simple_article, path_to_everyday_language_article) reads the articles'
    contents, performs some additional sentence splitting and returns the texts.

    Args:
        article_list (list[tuple[str,str]]): list of tuples in the form of (easy_article, everyday_article)

    Returns:
        list[list[list[str], list[str]]]: list of article pairs, where the entry for each article pair consists either
        of a list of sentences (if sentence_split==True) or a string of text.
    """
    articles = []
    for simple_path, everyday_path in article_list:
        with open(simple_path, "r", encoding="utf-8") as fs, open(everyday_path, "r", encoding="utf-8") as fe:

            if sentence_split:
                articles.append([prep_text(fs.read()), prep_text(fe.read())])
            else:
                articles.append([fs.read(), fe.read()])

    return articles

# STEP 1 - get the paths to the article pairs that we want
# get_article_pairs() always returns a list of tuples in the following form:
# (easy_article, everyday_language_article)

# only get articles from the source "taz"
taz_articles = util.get_article_pairs(source="taz")
print(f"Loaded {len(taz_articles)} article pairs from the source 'taz'.")

# only get articles from the sources "brandeins" and "apotheken-umschau"
bra_apo = util.get_article_pairs(source=["brandeins", "apotheken-umschau"])
print(f"Loaded {len(bra_apo)} article pairs from the sources 'brandeins' and 'apotheken-umschau'.")

# only get article pairs where the simple form is in "Einfache Sprache"
# (currently that's only articles from the apotheken-umschau)
# could also be "LS" for "Leichte Sprache"
einfache_sprache_articles = util.get_article_pairs(type="ES")
print(f"Loaded {len(einfache_sprache_articles)} article pairs in 'Einfache Sprache'.\n")

# STEP 2 - use the function read_articles() to get either sentence pairs (if sentence_split==True)
taz_text = read_articles(taz_articles)
print(f"Loaded {sum(len(entry[0]) for entry in taz_text)} sentences in simple language and "
      f"{sum(len(entry[1]) for entry in taz_text)} sentences in everyday language for all articles of the 'taz'\n")

# or the entire article in one string (if sentence_split==False)
einfache_sprache_text = read_articles(einfache_sprache_articles, sentence_split=False)
print(f"Loaded the text for the {len(einfache_sprache_text)} articles in 'Einfache Sprache'")
print(f"See as example in 'Einfache Sprache':\n\n{einfache_sprache_text[0][0][:300]}(...)\n\nand the corresponding "
      f"article in everyday language:\n\n{einfache_sprache_text[0][1][:300]}(...)")
