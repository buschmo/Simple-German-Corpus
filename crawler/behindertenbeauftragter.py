import crawler.utilities as utl
import re
from bs4 import BeautifulSoup


def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    easy_soup_tag = easy_soup.find(name="a",
                                   title=re.compile(
                                       "Lesen Sie den Artikel .* in Alltagssprache", flags=re.I),
                                   class_="c-language-switch__l c-language-switch__l--as",
                                   string="Alltagssprache"
                                   )

    if easy_soup_tag:
        normal_url = utl.parse_url(
            easy_soup_tag["href"],
            base_url
        )
        normal_soup = utl.read_soup(normal_url)
        utl.save_parallel_soup(normal_soup, normal_url, easy_soup, easy_url)
    else:
        utl.log_missing_url(easy_url)


def crawling(base_url):
    easy_url = "https://www.behindertenbeauftragter.de/DE/LS/startseite/startseite-node.html"

    soup = utl.read_soup(easy_url)
    soup_tags = soup.find_all(name="div", class_="menu fl-1")
    easy_urls = [link["href"]
                 for tag in soup_tags for link in tag.find_all(name="a", href=True)]

    easy_urls = [utl.parse_url(url[:url.find(";")], base_url)
                 for url in easy_urls]

    for i, easy_url in enumerate(easy_urls):
        print(f"{i+1:0>2}/{len(easy_urls)} Crawling {easy_url}")
        crawl_site(easy_url, base_url)


def filter_block(tag) -> bool:
    if tag.name == "div":
        if tag.has_attr("id"):
            if "content" in tag["id"]:
                if tag.has_attr("class"):
                    if "content" in tag["class"]:
                        return True
    return False


def filter_tags(tag) -> bool:
    if tag.name == "p":
        return True
    elif tag.name == "h2":
        return True
    elif tag.name == "ul":
        return True
    if tag.name == "div":
        if tag.has_attr("class"):
            if "abstract" in tag["class"]:
                return True
    return False


def parser(soup: BeautifulSoup) -> BeautifulSoup:
    article_tag = soup.find_all(filter_block)
    if len(article_tag) > 1:
        print("Unaccounted case occured. More than one article found.")
        return
    article_tag = article_tag[0]

    content = article_tag.find_all(filter_tags, recursive=False)
    result = BeautifulSoup("", "html.parser")
    for tag in content:
        result.append(tag)
    return result


base_url = "https://www.behindertenbeauftragter.de/"
def main():
    crawling(base_url)
    utl.parse_soups(base_url, parser)


if __name__ == '__main__':
    main()
