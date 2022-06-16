import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet
import os
import urllib
from pathlib import Path
import json
import re
from collections.abc import Callable

from datetime import datetime, timedelta, date
import time


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'}

SCRAPE_DELAY = 5

LAST_SCRAPE = None

from_archive = False


def read_soup(url: str) ->BeautifulSoup:
    """ Read soup given by url
    Reads the file of the soup and returns it.
    Downloads the soup if necessary.
    Beware that get_soup_from_url does not handle request denials of the website!

    Args:
        url (str): url to be read

    Returns:
        BeautifulSoup: the requested soup
    """    
    filepath = get_crawled_path_from_url(url)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, 'html.parser')
    else:
        soup = get_soup_from_url(url)

    return soup


def save_parallel_soup(normal_soup:BeautifulSoup, normal_url: str, easy_soup:BeautifulSoup, easy_url: str, publication_date:str=None):
    """ Save parallel normal and easy webpage
    Given parallel BeautifulSoups, this methods saves both and setups the needed header file information.

    Args:
        normal_soup (BeautifulSoup): normal soup
        normal_url (str): url of the normal soup
        easy_soup (BeautifulSoup): easy soup
        easy_url (str): url of the easy soup
        publication_date (str, optional): String of the webpage's date of publication. Defaults to None.
    """    
    normal_filepath = get_crawled_path_from_url(normal_url)
    easy_filepath = get_crawled_path_from_url(easy_url)

    save_soup(normal_soup, normal_filepath)
    save_header(normal_filepath, normal_url,
                easy_filepath, False, publication_date)

    save_soup(easy_soup, easy_filepath)
    save_header(easy_filepath, easy_url,
                normal_filepath, True, publication_date)


def save_soup(soup:BeautifulSoup, filepath: Path):
    """ Saves a given soup under given path

    Args:
        soup (BeautifulSoup): soup to be saved
        filepath (Path): Path where to save
    """    
    if not os.path.exists(filepath.parent):
        os.makedirs(filepath.parent)

    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(soup.prettify())


def load_header(url: str) -> dict:
    """ Loads and returns the header file for a given webpage.
    The header is determined by the base url of the webpage.

    Args:
        url (str): url for which the header is to be loaded

    Returns:
        dict: header's content
    """    
    headerpath = get_headerpath_from_url(url)
    # save header information
    if os.path.exists(headerpath):
        with open(headerpath, "r") as f:
            header = json.load(f)
    else:
        header = {}
    return header


def save_header(filepath : Path, url: str, matching_filepath: Path, bool_easy: bool = False, publication_date:str=None):
    """ Saves the given information to the header file determined by url

    Args:
        filepath (Path): Path to file. Filename is used as key in header
        url (str): Url, that determines the header file. The full url is saved in header
        matching_filepath (Path): Path to parallel file, i.e. simple file for a given normal one and vice versa
        bool_easy (bool, optional): Indicates if given file has easy german content or not. Defaults to False.
        publication_date (str, optional): The webpage's date of publication. Defaults to None.
    """    
    key = filepath.name
    headerpath = get_headerpath_from_url(url)

    if not os.path.exists(filepath.parent):
        os.makedirs(filepath.parent)

    # save header information
    if os.path.exists(headerpath):
        with open(headerpath, "r") as f:
            header = json.load(f)
    else:
        header = {}

    # if the file was already downloaded and used, simply append to the list
    if key in header.keys():
        if matching_filepath.name not in header[key]["matching_files"]:
            header[key]["matching_files"].append(matching_filepath.name)
    else:
        header[key] = {
            "url": url,
            "crawl_date": str(date.today()),
            "easy": bool_easy,
            "publication_date": publication_date,
            "matching_files": [matching_filepath.name]
        }
    with open(headerpath, "w", encoding="utf-8") as f:
        json.dump(header, f, indent=4)


def remove_header_entry(url: str, key: str):
    """ Removes an entry and deletes all corresponding files.

    Args:
        url (str): url to determine header file
        key (str): key to be removed from header
    """    
    header = load_header(url)
    # already deleted
    if not key in header.keys():
        return

    # delete crawled file
    crawled_path = get_crawled_path_from_url(header[key]["url"])
    if os.path.exists(crawled_path):
        os.remove(crawled_path)
    # delete parsed file
    parsed_path = get_parsed_path_from_url(header[key]["url"])
    if os.path.exists(parsed_path):
        os.remove(parsed_path)

    matching_files = header[key]["matching_files"]
    for k in matching_files:
        header[k]["matching_files"].remove(key)
        # remove files with no matching files
        if not header[k]["matching_files"]:
            # delete crawled file
            crawled_path = get_crawled_path_from_url(header[k]["url"])
            if os.path.exists(crawled_path):
                os.remove(crawled_path)
            # delete parsed file
            parsed_path = get_parsed_path_from_url(header[k]["url"])
            if os.path.exists(parsed_path):
                os.remove(parsed_path)
            del header[k]

    del header[key]
    headerpath = get_headerpath_from_url(url)
    with open(headerpath, "w", encoding="utf-8") as f:
        json.dump(header, f, indent=4)


def get_names_from_url(url: str) -> tuple[str, str]:
    """ Converts an url to the corresponding foldername and filename.

    Args:
        url (str): url to be converted

    Returns:
        tuple[str, str]: the foldername and filename of the url's file
    """    
    if from_archive:
        if "//web.archive.org/web/" in url:
            url = re.sub("\w+://web.archive.org/web/\d+/", "", url)
    if not url.startswith("http"):
        print(f"{url} did not specify a scheme, thus it will be added.")
        url = "https://" + url
    parsed_url = urllib.parse.urlparse(url)
    foldername = parsed_url.netloc
    filename = parsed_url.netloc + parsed_url.path.replace("/", "__")
    if not filename.endswith(".html"):
        filename += ".html"
    if filename.endswith("__.html"):
        filename = filename[:-len("__.html")] + ".html"
    if filename.startswith("www."):
        filename = filename[4:]
    if not foldername.startswith("www."):
        foldername = "www." + foldername
    return foldername, filename


def get_headerpath_from_url(url: str, parsed: bool = False) -> Path:
    """ Returns the corresponding header's path of a given url

    Args:
        url (str): url indicating the header
        parsed (bool, optional): whether to return the path to parsed_header.json or header.json. Defaults to False.

    Returns:
        Path: path to the respective header file
    """    
    foldername, _ = get_names_from_url(url)
    if parsed:
        return Path("Datasets", foldername, "parsed_header.json")
    elif from_archive:
        # from_archive indicated if archive_header.json is to be used.
        # This option is only needed for the publication of the paper
        return Path("Datasets", foldername, "archive_header.json")
    else:
        return Path("Datasets", foldername, "header.json")


def get_log_path_from_url(url: str)->Path:
    """ Path to the log file

    Args:
        url (str): url for path finding

    Returns:
        Path: path to log.txt
    """    
    foldername, _ = get_names_from_url(url)
    return Path("Datasets", foldername, "log.txt")


def get_parsed_path_from_url(url: str) -> Path:
    """ Returns path to the url's parsed file

    Args:
        url (str): url to determine file

    Returns:
        Path: Path to parsed file
    """    
    foldername, filename = get_names_from_url(url)
    return Path("Datasets", foldername, "parsed", filename + ".txt")


def get_crawled_path_from_url(url: str) -> Path:
    """ Returns path to the url's crawled file

    Args:
        url (str): url to determine file

    Returns:
        Path: Path to crawled file
    """    
    foldername, filename = get_names_from_url(url)
    return Path("Datasets", foldername, "crawled", filename)


def get_soup_from_url(url: str) -> BeautifulSoup:
    """ Downloads the BeautifulSoup from url
    Beware that this does not handle request denials of the website

    Args:
        url (str): url to be downloaded

    Returns:
        BeautifulSoup: downloaded BeautifulSoup
    """    
    global LAST_SCRAPE
    if LAST_SCRAPE is not None:
        time_since_last = datetime.now() - LAST_SCRAPE

        sleep_time = timedelta(0, SCRAPE_DELAY) - time_since_last

        if sleep_time >= timedelta(0):
            time.sleep(sleep_time.seconds)

    response = requests.get(url, headers=HEADERS)
    LAST_SCRAPE = datetime.now()

    return BeautifulSoup(response.text, 'html.parser')


# TODO this function should be removed as its usage is unnecessary. Some crawlers need to be rewritten
def get_urls_from_soup(soup, base_url: str, filter_args: dict = {}, recursive_filter_args: dict = {}) -> list[str]:
    if filter_args:
        blocks = soup.find_all(**filter_args)
        if recursive_filter_args:
            blocks = [block for block in blocks if block.find(
                **recursive_filter_args)]
    else:
        blocks = [soup]

    links = []
    for block in blocks:
        links.extend(block.find_all("a", href=True))

    urls = []
    for l in links:
        link = parse_url(l["href"], base_url)
        urls.append(link)

    urls = list(set(urls))
    return urls


def parse_url(url:str, base_url:str) -> str:
    """ Adds the base_url to url
    Some webpages only yield /some_page as url instead of base_url.domain/some_page

    Args:
        url (str): some url
        base_url (str): base url to be added to url if necessary

    Returns:
        str: new url
    """    
    if base_url not in url:
        url = urllib.parse.urljoin(base_url, url)
    return url


def parse_soups(base_url :str, parser: Callable[[BeautifulSoup], BeautifulSoup]):
    """ Traverses all downloaded files for a given url and parses the content.

    Args:
        base_url (str): url indicating the header file
        parser (Callable[[BeautifulSoup], BeautifulSoup]): the specific parser for the website. This probably needs to be unique for every website
    """    
    header = load_header(base_url)
    parsed_header_path = get_headerpath_from_url(base_url, parsed=True)
    parsed_header = {}
    l_remove = [] # saves webpages that generated no content after parsing

    # parse every file
    for filename in header.keys():
        url = header[filename]["url"]
        path = get_parsed_path_from_url(url)
        # skip already if already parsed
        # if os.path.exists(path):
        #     continue

        # get soup for parsing
        soup = read_soup(url)
        parsed_content = parser(soup)

        # filter out empty results as no parsable entry exists
        if parsed_content and parsed_content.contents:
            if not os.path.exists(path.parent):
                os.makedirs(path.parent)

            string = ""
            for tag in parsed_content.contents:
                text = tag.get_text()
                # clean up of text
                text = re.sub("\s+", " ", text)
                text = text.strip()
                # # remove empty lines
                if not text:
                    continue
                for sentence in re.split(r"([?.:!] )", text):
                    # Move punctuation to the correct position, i.e. the previous line
                    if sentence in [". ", ": ", "? ", "! "]:
                        string = string[:-1]
                    string += f"{sentence}\n"
            if string:
                with open(path, "w", encoding="utf-8") as fp:
                    fp.write(string)
                parsed_header[filename] = header[filename]
                continue
        print(
            f"No content for {url}. No header entry is created.\n\tCorresponding matching entries will be adapted.")
        l_remove.append(filename)

    # clean-up of empty files
    for filename in l_remove:
        for matching in header[filename]["matching_files"]:
            # check if it was parsed
            if matching in parsed_header:
                parsed_header[matching]["matching_files"].remove(filename)
                if not parsed_header[matching]["matching_files"]:
                    # delete the entry and its parsed file, if no matching files remain
                    parsed_path = get_parsed_path_from_url(
                        parsed_header[matching]["url"])
                    os.remove(parsed_path)
                    del parsed_header[matching]
                    print(
                        f"Removed {matching}, as no matching file remained after {filename} was removed.")
    with open(parsed_header_path, "w", encoding="utf-8") as fp:
        json.dump(parsed_header, fp, indent=4)


def filter_urls(urls: list[str], base_url: str) -> list[str]:
    """ Removes urls that have already been downloaded

    Args:
        urls (list[str]): list of urls to be filtered
        base_url (str): base url of the website

    Returns:
        list[str]: filtered list of urls
    """    
    file_path = get_crawled_path_from_url(urls[0])
    header_path = get_headerpath_from_url(urls[0])

    # remove urls leaving the website
    urls = [url for url in urls if base_url in url]
    if os.path.exists(header_path):
        with open(header_path, "r", encoding="utf-8") as f:
            header = json.load(f)
            keys = header.keys()
            # remove already downloaded urls
            urls = [url for url in urls if get_crawled_path_from_url(
                url).name not in keys]
    return urls


### LOGGING UTILITIES ###
### These can savely be ignored ###
### Pythons logging utilities should be used instead ###

def log_missing_url(url: str):
    if not already_logged(url):
        path = get_log_path_from_url(url)
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)

        with open(path, "a", encoding="utf-8") as f:
            current_time = datetime.now().isoformat(timespec="seconds")
            f.write(f"{current_time} No matching url found for: {url}\n")


def log_multiple_url(url: str):
    if not already_logged(url):
        path = get_headerpath_from_url(url)
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)
        with open(path, "a", encoding="utf-8") as f:
            current_time = datetime.now().isoformat(timespec="seconds")
            f.write(
                f"{current_time} More than one matching url found for: {url}\n")


# TODO this method may be removed
def log_resaving_file(filepath: Path):
    foldername = filepath.parent
    filename = filepath.name
    if not already_logged(filename):
        path = get_headerpath_from_url(url)
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)
        with open(path, "a", encoding="utf-8") as f:
            current_time = datetime.now().isoformat(timespec="seconds")
            f.write(
                f"{current_time} The file is used for several matches: {filename}\n")


def already_logged(url: str) -> bool:
    path = get_headerpath_from_url(url)
    if os.path.exists(path):_description_
        with open(path, "r") as f:
            content = f.read()
            return bool(url in content)
