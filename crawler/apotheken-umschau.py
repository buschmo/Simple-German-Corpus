#!/usr/bin/python3.10
import requests
from bs4 import BeautifulSoup
import crawler.utilities as utl


def filter_soup(tag):
    """
    Filters all tags for the ones containing "hier" in the attribute title, having either the value "au" or
    "dira" in "data-portal-ident" and linking to a valid site of the apotheken-umschau.de (disregarding external links
    to other sources).
    """
    return tag.name == "a" and "hier" in tag.attrs.get("title", "False") \
           and any([tag.attrs.get("data-portal-ident", False) == "au",
                    tag.attrs.get("data-portal-ident", False) == "dira"]) \
           and utl.session.get(base_url[:-1] + tag.attrs.get("href", "DOESNT_EXIST").split(".")[0],
                               headers=utl.HEADERS).status_code == 200


def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    # the final paragraph contains a link titled "hier" to the corresponding article in German
    # find the a tag containing said string
    if len(easy_soup.find_parents(name="a", attrs={"title": "hier"})) > 1:
        print("Error! More than one parent was found for the links.")
        return

    easy_url_tags = easy_soup.find_all(filter_soup)

    normals_urls = [utl.parse_url(tag["href"], base_url)
                    for tag in easy_url_tags if "einfache-sprache" not in tag["href"]]

    if len(normals_urls):
        # few simple German articles link to German articles or general websites outside apotheken-umschau.de
        if "apotheken-umschau" not in normals_urls[0]:
            return
        normal_soup = utl.read_soup(normals_urls[0])

        utl.save_parallel_soup(normal_soup, normals_urls[0],
                               easy_soup, easy_url)
    elif len(normals_urls) > 1:
        print(f"Multiple matching URLs {normals_urls}")
    else:
        utl.log_missing_url(easy_url)


def crawling(base_url):
    home_url_easy = "https://www.apotheken-umschau.de/einfache-sprache/"

    # get urls
    easy_soup = utl.read_soup(home_url_easy)

    easy_url_tags = easy_soup.find_all(
        name="a",
        href=lambda x: "einfache-sprache" in x
    )
    easy_urls = list(set([utl.parse_url(tag["href"], base_url)
                          for tag in easy_url_tags]))

    for i, easy_url in enumerate(easy_urls):
        print(f"[{i + 1:0>3}/{len(easy_urls)}] Crawling {easy_url}")
        crawl_site(easy_url, base_url)


def filter_tags(tag) -> bool:
    if tag.name == "p":
        if tag.has_attr("class"):
            if "text" in tag["class"]:
                return True
    if tag.name == "ul":
        if tag.parent.name == "div":
            if tag.parent.has_attr("class"):
                if "copy" in tag.parent["class"]:
                    return True
    return False


def parser(soup: BeautifulSoup) -> BeautifulSoup:
    article_tag = soup.find_all(name="div", class_="copy")
    if len(article_tag) > 1:
        print("Unaccounted case occurred. More than one article found.")
        return
    article_tag = article_tag[0]

    # get unwanted tags and remove them
    inverse_result = article_tag.find_all(
        lambda x: not filter_tags(x), recursive=False)
    for tag in inverse_result:
        tag.decompose()

    return article_tag


base_url = "https://www.apotheken-umschau.de/"
def main():
    crawling(base_url)
    utl.parse_soups(base_url, parser)


if __name__ == '__main__':
    main()
