"""List catalog data using the library API.

Shows sources, languages, tags, and DFC pairs.
"""

from mpcfill import list_dfcs, list_languages, list_sources, list_tags


def main():
    """Print catalog data tables to stdout."""
    print("Sources:")
    for s in list_sources().values():
        print(f"  {s['pk']}: {s['name']}")

    print("\nLanguages:")
    for lang in list_languages():
        print(f"  {lang['code']}: {lang['name']}")

    print("\nDFC Pairs:")
    for front, back in list_dfcs().items():
        print(f"  {front} -> {back}")

    print("\nTags (roots):")
    tags = list_tags()
    # Show only top-level names for brevity (structure may be nested)
    for t in tags[:10]:
        print(f"  {t.get('name', '')}")


if __name__ == "__main__":
    main()
