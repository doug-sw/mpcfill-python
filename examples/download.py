"""Search and download best images into a folder."""

from pathlib import Path

from mpcfill import SearchSettings, search_and_download_best


def main():
    """Run a sample download of best-matching images."""
    dest = Path("downloads")
    settings = SearchSettings(minimum_dpi=600, maximum_dpi=1500, maximum_size=30)
    paths = search_and_download_best(["Welcome to..."], dest, settings)
    for p in paths:
        print(p)


if __name__ == "__main__":
    main()
