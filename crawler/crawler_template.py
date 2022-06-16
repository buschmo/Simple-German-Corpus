import crawler.utilities as utl

# base_url is used for creating the main folder and as a start point for crawling
base_url = "homepage"

def crawl_site(easy_url: str, base_url: str):
    """ Saves the parallel articles

    Args:
        easy_url (str): the easy article to find the normal article in
        base_url (str): the base hostname of the website
    """
    easy_soup = utl.read_soup(easy_url)

    # Find the corresponding normal url in the easy soup

    if normals_url:
        # save the parallel articles
        utl.save_parallel_soup(normal_soup, normal_url, easy_soup, easy_url)
    else:
        utl.log_missing_url(easy_url)


def crawling(base_url: str):
    """ Starts the crawling process

    Args:
        base_url (str): the base hostname of the website
    """
    home_url_easy = ""

    easy_soup = utl.read_soup(home_url_easy)

    # Suggested steps:
    #   get urls from easy main page
    #   use crawl_site to traverse the found urls and make recursive calls

    # read the corresponding articles
    for i, easy_url in enumerate(easy_urls):
        print(f"[{i+1}/{len(easy_urls)}] Crawling {easy_url}")
        crawl_site(easy_url, base_url)


def parser(soup: BeautifulSoup) -> BeautifulSoup:
    """ Parse the texts from the previously downloaded articles
    Given a soup, parse the contents into a result soup.
    Most of the time 

    Args:
        soup (BeautifulSoup): BeautifulSoup object of the webpage to be parsed

    Returns:
        BeautifulSoup: BeautifulSoup object containing the the text to be extracted (See utl.parse_soups() for context)
    """

    content = soup

    # add functionality to parse draw useable content from the soup
    results = BeautifulSoup(content, "html.parser")
    return result
