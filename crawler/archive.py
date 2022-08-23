#!/usr/bin/env python3.10
import os
import time
import json
import argparse
import urllib.parse
from pathlib import Path
from urllib.request import urlopen

import crawler
import utilities as utl
from defaultvalues import dataset_location

parser = argparse.ArgumentParser(description="Script to either archive the links of a certain source and create the "
                                             "corresponding archive_header.json or check and update the entire dataset "
                                             "folder.")
parser.add_argument('--update', action='store_true', help="Use --update to update all the archive_header.json files of"
                                                          "the entire dataset")
parser.add_argument('--archive', help="Use --archive {crawler-name} to archive the URLs associated with this crawler in"
                                      "the dataset folder")


def main(args):
    update = args.update
    archive_crawler = args.archive

    if update and archive_crawler:
        print("Please specify either --update OR --archive {crawler-name}")
        exit()
    elif archive_crawler:
        header_to_archive(archive_crawler)
    elif update:
        raise NotImplementedError
    else:
        print("Please specify either --update OR --archive {crawler-name}")


def header_to_archive(name: str):
    """
    Function to archive all URLs provided by the header.json of the respective crawler.
    Saves all archived URLs in the archive_header.json.

    Args:
        name (str): name of the crawler, e.g. stadt-koeln
    """
    if name not in crawler.__all__:
        print(f"{name} does not seem to be a crawler script in the crawler folder.")
    else:
        base_url = getattr(crawler, name).base_url
        # transforms e.g. "https://www.apotheken-umschau.de/"
        # to foldername = www.apotheken-umschau.de
        foldername, _ = utl.get_names_from_url(base_url)

        with open(Path(dataset_location, foldername, "header.json")) as fp:
            header = json.load(fp)

        path_archive_header = Path(dataset_location, foldername, "archive_header.json")
        if os.path.isfile(path_archive_header):
            with open(path_archive_header, "r") as fp:
                archive_header = json.load(fp)
        else:
            archive_header = {}

        for key in header:
            if key in archive_header.keys():
                continue
            url = header[key]["url"]
            try:
                with urllib.request.urlopen(f"http://web.archive.org/{url}") as f:
                    print(f"Already archived: {f.url}")
                    # TODO: add checksum for article content?
                    archive_header[key] = {
                        "url": f.url,
                        "crawl_date": header[key]["crawl_date"],
                        "easy": header[key]["easy"],
                        "publication_date": header[key]["publication_date"],
                        "matching_files": header[key]["matching_files"]
                    }
                    with open(path_archive_header, "w") as fp:
                        json.dump(archive_header, fp, indent=4)

            except:
                not_downloaded = True
                counter = 0
                while not_downloaded:
                    try:
                        with urllib.request.urlopen(f"http://web.archive.org/save/{url}") as f:
                            print(f"Newly archived: {f.url}")
                            # TODO: add checksum for article content?
                            archive_header[key] = {
                                "url": f.url,
                                "crawl_date": header[key]["crawl_date"],
                                "easy": header[key]["easy"],
                                "publication_date": header[key]["publication_date"],
                                "matching_files": header[key]["matching_files"]
                            }
                            with open(path_archive_header, "w") as fp:
                                json.dump(archive_header, fp, indent=4)
                            not_downloaded = False
                    except urllib.error.HTTPError as err:
                        time.sleep(60)
                        counter += 1
                        if counter > 4:
                            print(
                                f"{counter} failed to archive: {url}\n  {str(err)}\n")
                            print(f"Stopping {url}")
                            with open("ERROR", "a") as fp:
                                fp.write(url + "\n  " + str(err) + "\n\n")
                            not_downloaded = False


if __name__ == "__main__":
    args = parser.parse_args("--archive apotheken-umschau".split())
    main(args)
