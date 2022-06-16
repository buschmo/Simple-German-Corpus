import crawler.utilities as utl
import re
from bs4 import BeautifulSoup

def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    normal_url = utl.parse_url(
        easy_soup.find(name="a", hreflang="de-DE", class_="underline easy",
                       string=re.compile("Standardsprache", flags=re.I))["href"],
        base_url
    )
    if normal_url:
        normal_soup = utl.read_soup(normal_url)
        utl.save_parallel_soup(normal_soup, normal_url, easy_soup, easy_url)
    else:
        utl.log_missing_url(easy_url)


def crawling(base_url):
    easy_url = "https://www.sozialpolitik.com/es/"

    soup = utl.read_soup(easy_url)
    easy_urls = utl.get_urls_from_soup(
        soup,
        base_url,
        filter_args={"name": "section",
                     "class_": "element-col bg-weiss"
                     }
    )

    for i, easy_url in enumerate(easy_urls):
        print(f"{i+1:0>2}/{len(easy_urls)} Crawling {easy_url}")
        crawl_site(easy_url, base_url)


def filter_block(tag) -> bool:
    if tag.name == "main":
        return True
    return False


def filter_tags(tag) -> bool:
    if tag.name == "p":
        return True
    elif tag.name == "ul":
        return True
    elif tag.name == "h3":
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


base_url = "https://www.sozialpolitik.com/"
def main():
    crawling(base_url)
    utl.parse_soups(base_url, parser)


if __name__ == '__main__':
    main()
