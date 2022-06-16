#!/usr/bin/python3.10
import crawler.utilities as utl
import re
from bs4 import BeautifulSoup

""" Lebenshilfe Main Taunus
Ignore /dokument/

"""


def crawl_site(easy_url, base_url):
    print(f"Crawling {easy_url}")
    easy_soup = utl.read_soup(easy_url)

    easy_soup_block = easy_soup.find(
        name="div",
        attrs={"class": "modul",
               "id": "mod_menue_top"}
    )

    normal_urls = utl.get_urls_from_soup(
        easy_soup_block,
        base_url,
        filter_args={"name": "li"},
        recursive_filter_args={"title": "Auf Alltags-Sprache umstellen"}
    )

    try:
        normal_url = normal_urls[0]
        normal_soup = utl.read_soup(normal_url)
        utl.save_parallel_soup(normal_soup, normal_url,
                               easy_soup, easy_url)
    except IndexError as e:
        utl.log_missing_url(easy_url)

    urls_sidemenu = utl.get_urls_from_soup(
        easy_soup, base_url,
        filter_args={
            "name": "div",
            "attrs": {"id": "sidebar"}}
    )
    urls_top_menu = utl.get_urls_from_soup(
        easy_soup, base_url,
        filter_args={
            "name": "div",
            "attrs": {"class": "modul", "id": "mod_menue_top"}}
    )
    urls_top_menu_ebene0 = utl.get_urls_from_soup(
        easy_soup, base_url,
        filter_args={
            "name": "div",
            "attrs": {"class": "modul", "id": "mod_menue_ebene0"}}
    )

    urls = urls_sidemenu + urls_top_menu + urls_top_menu_ebene0
    urls = filter_urls(urls, base_url)

    for url in urls:
        crawl_site(url, base_url)


def filter_urls(urls, base_url):
    urls = utl.filter_urls(urls, base_url)
    # remove download links of docs
    urls = [url for url in urls if (
        "index.php?menuid=" not in url) and ("/ls/" in url)]
    return urls


def crawling(base_url):
    home_url_easy = "https://www.lebenshilfe-main-taunus.de/ls/"

    crawl_site(home_url_easy, base_url)


def filter_block(tag) -> bool:
    if tag.name == "div":
        if tag.has_attr("class"):
            if "artikel_details" in tag["class"]:
                return True
    return False


def filter_tags(tag) -> bool:
    if tag.parent.has_attr("class"):
        if "inhalt" in tag.parent["class"]:
            if tag.name == "p":
                return True
            elif tag.name == "ul":
                if "paragraph" in tag.parent["class"]:
                    return True
            elif tag.name == "div":
                if tag.has_attr("class"):
                    if "box_big" in tag["class"]:
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

    content = article_tag.find_all(filter_tags)
    result = BeautifulSoup("", "html.parser")
    for tag in content:
        result.append(tag)
    return result


base_url = "https://www.lebenshilfe-main-taunus.de/"
def main():
    crawling(base_url)
    utl.parse_soups(base_url, parser)


if __name__ == '__main__':
    main()
