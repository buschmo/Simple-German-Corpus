import crawler.utilities as utl
import re
from bs4 import BeautifulSoup


def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    easy_soup_tags = easy_soup.find_all(name="p", xmlns="", class_=True)
    easy_soup_tags = [tag for tag in easy_soup_tags if tag.find(name="em")]
    easy_soup_tags = [
        tag for tag in easy_soup_tags if tag.find(name="a", href=True)]

    if easy_soup_tags:
        a_tags = [href_tag for easy_soup_tag in easy_soup_tags for href_tag in easy_soup_tag.find_all(
            name="a", href=True)]

        for a_tag in a_tags:
            normal_url = utl.parse_url(
                a_tag["href"],
                base_url
            )

            normal_soup = utl.read_soup(normal_url)
            utl.save_parallel_soup(
                normal_soup, normal_url, easy_soup, easy_url)
    else:
        utl.log_missing_url(easy_url)


def crawling(base_url):
    easy_url = "https://taz.de/Politik/Deutschland/Leichte-Sprache/!p5097/"

    soup = utl.read_soup(easy_url)
    soup_tags = soup.find_all(name="ul",
                              role="directory",
                              debug="x1",
                              class_="news directory")

    easy_urls = [utl.parse_url(link["href"], base_url)
                 for tag in soup_tags for link in tag.find_all(name="a", href=True)]

    easy_urls = [utl.parse_url(url[:url.find(";")], base_url)
                 for url in easy_urls]

    for i, easy_url in enumerate(easy_urls):
        print(f"{i+1:0>2}/{len(easy_urls)} Crawling {easy_url}")
        crawl_site(easy_url, base_url)


def filter_block(tag) -> bool:
    if tag.name == "article":
        if tag.has_attr("class") and tag.has_attr("itemprop"):
            if "sectbody" in tag["class"] and "articleBody" in tag["itemprop"]:
                return True
    return False


def filter_tags(tag) -> bool:
    if tag.name in ["p", "h2", "h3", "h6", "ul"]:
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
        if "──────────────────" in tag.get_text():
            continue
        result.append(tag)
    return result


base_url = "https://taz.de/"
def main():
    crawling(base_url)
    utl.parse_soups(base_url, parser)


if __name__ == '__main__':
    main()
