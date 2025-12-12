"""
Search and download the best image for given queries into a folder.
"""
from pathlib import Path
from mpcfill import search_and_download_best, SearchSettings

def main():
    dest = Path("downloads")
    settings = SearchSettings(minimum_dpi=600, maximum_dpi=1500, maximum_size=30)
    paths = search_and_download_best(["Welcome to..."], dest, settings)
    for p in paths:
        print(p)

if __name__ == "__main__":
    main()
