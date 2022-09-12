import sys
sys.path.append('.')
import main_crawler
import main_matching


def main():
    """ Calls all necessary main functions to calculate everything except the end alignment
    """
    print("Downloading and parsing.")
    main_crawler.main(from_archive=True)
    print("Calculating results.\n\tThis might take a while and should not be aborted.\n\tThe calculation would start anew.")
    main_matching.main()


if __name__ == "__main__":
    main()
