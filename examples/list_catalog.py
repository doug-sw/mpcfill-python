"""
List catalog data: sources, languages, tags, dfcs using the library API.
"""
from mpcfill import list_sources, list_languages, list_tags, list_dfcs

def main():
    print("Sources:")
    for s in list_sources().values():
        print(f"  {s['pk']}: {s['name']}")

    print("\nLanguages:")
    for l in list_languages():
        print(f"  {l['code']}: {l['name']}")

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
