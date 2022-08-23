import os
from urllib.request import urlopen
import urllib.parse
import pickle
import os
import json

from defaultvalues import *

""" This files is an example file for automatically archiving websites.
    As it is not intended to be used, it will not be documented.
"""


def main():
    # for path,dirs,files in os.walk("Datasets"):
    #     if "archive_header.json" in files:
    #         print(path)
    #         print(dirs)
    #         print(files)

    url = "sozialpolitik.com/arbeitsrecht"

    data = urllib.parse.urlencode({"url":url})
    data = data.encode("ascii")
    if not os.path.exists("jonk.pkl"):
        with open("jonk.pkl", "rb") as fp:
            conn = pickle.load(fp)
            print(conn.decode("utf-8"))
            print(conn.url)
            
    else:
        # with urlopen("http://web.archive.org/save/", data) as conn:
        with urlopen(f"http://web.archive.org/save/{url}") as conn:
            print(conn.url)
            # with open("jonk.pkl", "wb") as fp:
            #     pickle.dump(conn.read(), fp)


def header_to_archive():
    utl = crawler.utilities
    for name in sorted(crawler.__all__):
        # if name != "mdr":
        #     continue

        base_url = getattr(crawler, name).base_url
        foldername, _ = utl.get_names_from_url(base_url)
        with open(dataset_location + '/' + foldername + "/header.json") as fp:
            header = json.load(fp)

        path_archive_header = dataset_location + '/' + foldername + "/archive_header.json"
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
                            # if counter >= 10:
                            print(f"Stopping {url}")
                            with open("ERROR", "a") as fp:
                                fp.write(url+"\n  "+str(err)+"\n\n")
                            not_downloaded = False