#!/usr/bin/python3.10
import crawler.utilities as utl
import re
from bs4 import BeautifulSoup


def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    # find the a tag containing said string
    easy_url_tag = easy_soup.find(
        name="a",
        string=re.compile("Diese Seite in Alltags-Sprache lesen", flags=re.I)
    )
    # convert the tag class to BeautifulSoup class
    easy_url_soup = BeautifulSoup(str(easy_url_tag), "html.parser")

    # get the url from this
    normal_urls = utl.get_urls_from_soup(
        easy_url_soup,
        base_url
    )

    try:
        normal_url = normal_urls[0]
        normal_soup = utl.read_soup(normal_url)

        utl.save_parallel_soup(normal_soup, normal_url,
                               easy_soup, easy_url)
    except IndexError as e:
        utl.log_missing_url(easy_url)


def filter_urls(urls, base_url):
    urls = utl.filter_urls(urls, base_url)
    # remove download links of docs
    urls = [url for url in urls if (
        "index.php?menuid=" not in url) and ("/ls/" in url)]
    return urls


def crawling(base_url):
    home_url_easy = "https://www.stadt-koeln.de/leben-in-koeln/soziales/informationen-leichter-sprache"

    # get urls
    easy_soup = utl.read_soup(home_url_easy)
    easy_urls = utl.get_urls_from_soup(
        easy_soup,
        base_url,
        {"name": "section",
         "attrs": {"class": "trefferliste_flex trefferliste"}}
    )

    for i, easy_url in enumerate(easy_urls):
        print(f"[{i+1:0>2}/{len(easy_urls)}] Crawling {easy_url}")
        crawl_site(easy_url, base_url)


def filter_block(tag) -> bool:
    if tag.name == "main":
        if tag.has_attr("id") and tag.has_attr("role"):
            if "inhalt" in tag["id"] and "main" in tag["role"]:
                return True
    return False


def filter_tags(tag) -> bool:
    if tag.parent.name == "div" and tag.parent.has_attr("class"):
        if "accordionhead" in tag.parent["class"] or "accordionpanel" in tag.parent["class"] or "tinyblock" in tag.parent["class"]:
            if tag.name in ["p", "h2", "h3", "ul"]:
                return True
    return False


def parser(soup: BeautifulSoup) -> BeautifulSoup:
    article_tag = soup.find_all(filter_block)
    if len(article_tag) > 1:
        print("Unaccounted case occured. More than one article found.")
        return
    elif len(article_tag) == 0:
        print("Unaccounted case occured. No article found.")
        return
    article_tag = article_tag[0]

    if article_tag.find(name="section", id="produktbeschreibung"):
        article_tag = article_tag.find(name="section", id="produktbeschreibung")

    content = article_tag.find_all(filter_tags)
    result = BeautifulSoup("", "html.parser")
    for tag in content:
        result.append(tag)
    return result


base_url = "https://www.stadt-koeln.de/"
def main():
    crawling(base_url)
    utl.parse_soups(base_url, parser)


if __name__ == '__main__':
    main()
