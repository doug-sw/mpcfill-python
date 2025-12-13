"""Search for cards and print a results table.

Demonstrates using the library functions to fetch and format results.
"""

from mpcfill import CardType, SearchSettings, search_cards


def main():
    """Run a simple search and print a formatted table."""
    queries = [
        {"query": "Shoot the Sheriff", "cardType": CardType.CARD},
        {"query": "Treasure", "cardType": CardType.TOKEN},
    ]
    settings = SearchSettings(minimum_dpi=600, maximum_dpi=1500, maximum_size=30)
    groups = search_cards(queries, settings, fetch_backs=True)

    rows = []
    for g in groups:
        best = g[0]
        rows.append(
            {
                "Type": getattr(best, "cardType", ""),
                "Name": getattr(best, "name", ""),
                "ID": getattr(best, "identifier", ""),
            }
        )

    if not rows:
        print("No results.")
        return

    headers = ["Type", "Name", "ID"]
    col_widths = {h: max(len(h), max(len(r[h]) for r in rows)) for h in headers}

    def fmt_row(r):
        return "  ".join(r[h].ljust(col_widths[h]) for h in headers)

    print(fmt_row({h: h for h in headers}))
    print("  ".join("-" * col_widths[h] for h in headers))
    for r in rows:
        print(fmt_row(r))


if __name__ == "__main__":
    main()
