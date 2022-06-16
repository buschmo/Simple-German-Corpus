#!/usr/bin/python3.10
import crawler.utilities as utl
import re
from bs4 import BeautifulSoup

""" MDR
There are three content pages on mdr.de
    - The main page contains up to 3 blocks of daily news, one block for each past day consisting of 4 articles
    - a block with 3 articles giving general information in simple german
    -
"""


def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    publication_date = str(easy_soup.find(
        "p", {"class": "webtime"}).find_all("span")[1])[6:-9].strip()

    if publication_date.endswith(","):
        publication_date = publication_date[:-1]

    normal_urls = utl.get_urls_from_soup(
        easy_soup,
        base_url,
        filter_args={
            "name": "div",
            "attrs": {"class": "con cssBoxTeaserStandard conInline"}
        },
        recursive_filter_args={
            "string": re.compile("auch in schwerer Sprache", flags=re.I)
        }
    )

    try:
        normal_url = normal_urls[0]
        normal_soup = utl.read_soup(normal_url)

        utl.save_parallel_soup(normal_soup, normal_url,
                               easy_soup, easy_url, publication_date)
    except IndexError as e:
        utl.log_missing_url(easy_url)


def daily():
    base_url = "https://www.mdr.de/"
    home_url = "https://www.mdr.de/nachrichten-leicht/index.html"

    # crawl current news articles
    main_soup = utl.read_soup(home_url)
    easy_news_urls = utl.get_urls_from_soup(
        main_soup,
        base_url,
        {"name": "div",
         "attrs": {"class": "sectionWrapper section1er audioApp cssPageAreaWithoutContent"}
         })

    for easy_url in easy_news_urls:
        print(f"[{i+1}/{len(easy_urls)}] Crawling {easy_url}")
        crawl_site(easy_news_url, base_url)


def crawling(base_url):
    home_url = "https://www.mdr.de/nachrichten-leicht/index.html"

    # crawl current news articles
    main_soup = utl.read_soup(home_url)
    easy_news_urls = utl.get_urls_from_soup(
        main_soup,
        base_url,
        {"name": "div",
         "attrs": {"class": "sectionWrapper section1er audioApp cssPageAreaWithoutContent"}
         })

    for i, easy_url in enumerate(easy_news_urls):
        print(f"[{i+1}/{len(easy_news_urls)}] Crawling {easy_url}")
        crawl_site(easy_url, base_url)

    # crawl archived articles
    archive_urls = [
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-100.html",
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-anhalt-100.html",
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-thueringen-100.html"
    ]

    for url in archive_urls:
        archive_soup = utl.read_soup(url)
        string = "targetNode-nachrichten-leichte-sprache"
        easy_information_urls = utl.get_urls_from_soup(
            archive_soup,
            base_url,
            {"name": "div",
             "attrs": {"class": string}
             })

        for i, easy_url in enumerate(easy_information_urls):
            print(f"[{i+1}/{len(easy_information_urls)}] Crawling {easy_url}")
            crawl_site(easy_url, base_url)


def filter_block(tag) -> bool:
    if tag.name == "div":
        if tag.has_attr("class"):
            s = set(["section", "sectionDetailPage", "cssBoxContent"])
            if s.issubset(set(tag["class"])):
                return True
    return False


def filter_tags(tag) -> bool:
    if tag.name == "p":
        if tag.has_attr("class"):
            if "text" in tag["class"] or "einleitung" in tag["class"]:
                return True
    elif tag.name == "span":
        if tag.has_attr("class"):
            if "headline" in tag["class"]:
                if tag.parent.name == "h1":
                    if not tag.string.endswith("."):
                        tag.string.replace_with(str(tag.string).strip() + ".")
                    return True
    elif tag.name == "ul":
        if tag.parent.name == "div" and tag.parent.has_attr("class"):
            if "paragraph" in tag.parent["class"]:
                return True
    return False


def parser(soup: BeautifulSoup) -> BeautifulSoup:
    """ Parses the headline, introduction and main text
    Omits image description and h3 type headlines as these are not present in easy german texts
    """
    article_tag = soup.find_all(filter_block)
    if len(article_tag) > 1:
        print("Unaccounted case occured. More than one article found.")
        return
    article_tag = article_tag[0]

    content = article_tag.find_all(filter_tags)
    result = BeautifulSoup("", "html.parser")
    for tag in content:
        result.append(tag)
    return result


base_url = "https://www.mdr.de/"
def main():
    crawling(base_url)
    utl.parse_soups(base_url, parser)


if __name__ == '__main__':
    main()
