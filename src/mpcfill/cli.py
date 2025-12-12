import argparse
import os
import sys
import signal
from pathlib import Path
from typing import List, Dict
from . import (
    search_cards,
    SearchSettings,
    CardType,
    fetch_sources,
    fetch_languages,
    fetch_dfcs,
)
 
 


def cmd_search(args: argparse.Namespace):
    settings = SearchSettings(
        minimum_dpi=args.minimum_dpi,
        maximum_dpi=args.maximum_dpi,
        maximum_size=args.maximum_size,
        fuzzy_search=args.fuzzy,
        filter_cardbacks=args.filter_cardbacks,
        languages=args.languages or [],
        includes_tags=args.include_tags or [],
        excludes_tags=args.exclude_tags or [],
    )
    # Build queries; support mixed types via prefix "t:" for tokens
    queries: List[Dict] = []
    for raw in args.query:
        is_token = raw.lower().startswith("t:")
        name = raw[2:] if raw.lower().startswith("t:") else raw
        queries.append({"query": name, "cardType": CardType.TOKEN if is_token else CardType.CARD})
    groups = search_cards(queries, settings, fetch_backs=not args.no_backs)
    rows = []
    for g in groups:
        best = g[0]
        rows.append({
            "Type": getattr(best, "cardType", ""),
            "Name": getattr(best, "name", ""),
            "ID": getattr(best, "identifier", ""),
        })

    if not rows:
        return

        # JSON output if requested
        if getattr(args, "json", False):
            import json
            print(json.dumps(rows, ensure_ascii=False))
            return

    headers = ["Type", "Name", "ID"]
    col_widths = {h: max(len(h), max(len(r[h]) for r in rows)) for h in headers}
    def fmt_row(r):
        return "  ".join(r[h].ljust(col_widths[h]) for h in headers)

    print(fmt_row({h: h for h in headers}))
    print("  ".join("-" * col_widths[h] for h in headers))
    for r in rows:
        print(fmt_row(r))


def cmd_download_best(args: argparse.Namespace):
    settings = SearchSettings(
        minimum_dpi=args.minimum_dpi,
        maximum_dpi=args.maximum_dpi,
        maximum_size=args.maximum_size,
        fuzzy_search=args.fuzzy,
        filter_cardbacks=args.filter_cardbacks,
        languages=args.languages or [],
        includes_tags=args.include_tags or [],
        excludes_tags=args.exclude_tags or [],
    )
    # Mixed-type query support: parse prefixes here and handle per-item types
    from .search import search_cards
    from .utils import make_safe_path

    queries: List[Dict] = []
    for raw in args.query:
        is_token = raw.lower().startswith("t:")
        name = raw[2:] if raw.lower().startswith("t:") else raw
        queries.append({"query": name, "cardType": CardType.TOKEN if is_token else CardType.CARD})

    dest = Path(args.dest)
    groups = search_cards(queries, settings, fetch_backs=not args.no_backs)
    dest.mkdir(parents=True, exist_ok=True)
    for i, g in enumerate(groups):
        best = g[0]
        fname = f"{i}_{make_safe_path(best.name)}.{best.extension}"
        print(best.download_image(dest, filename=fname))


def cmd_list_sources(_: argparse.Namespace):
    sources = list(fetch_sources().values())
    if not sources:
        return
    rows = [{"ID": str(s.get("pk", "")), "Name": s.get("name", "")} for s in sources]
    headers = ["ID", "Name"]
    col_widths = {h: max(len(h), max(len(r[h]) for r in rows)) for h in headers}
    def fmt_row(r):
        return "  ".join(r[h].ljust(col_widths[h]) for h in headers)
    print(fmt_row({h: h for h in headers}))
    print("  ".join("-" * col_widths[h] for h in headers))
    for r in rows:
        print(fmt_row(r))


def cmd_list_languages(_: argparse.Namespace):
    langs = fetch_languages()
    if not langs:
        return
    rows = [{"Code": l.get("code", ""), "Name": l.get("name", "")} for l in langs]
    headers = ["Code", "Name"]
    col_widths = {h: max(len(h), max(len(r[h]) for r in rows)) for h in headers}
    def fmt_row(r):
        return "  ".join(r[h].ljust(col_widths[h]) for h in headers)
    print(fmt_row({h: h for h in headers}))
    print("  ".join("-" * col_widths[h] for h in headers))
    for r in rows:
        print(fmt_row(r))


def cmd_list_tags(_: argparse.Namespace):
    from .filters.tags import TagHierarchy
    th = TagHierarchy()

    def print_tree(nodes, prefix=""):
        for idx, node in enumerate(nodes):
            is_last = idx == len(nodes) - 1
            connector = "└── " if is_last else "├── "
            print(f"{prefix}{connector}{node.name}")
            if node.children:
                extension = "    " if is_last else "│   "
                print_tree(node.children, prefix + extension)

    print_tree(th.roots)


def cmd_list_dfcs(_: argparse.Namespace):
    dfcs = fetch_dfcs()
    if not dfcs:
        return
    rows = [{"Front": f or "", "Back": b or ""} for f, b in dfcs.items()]
    headers = ["Front", "Back"]
    col_widths = {h: max(len(h), max(len(r[h]) for r in rows)) for h in headers}
    def fmt_row(r):
        return "  ".join(r[h].ljust(col_widths[h]) for h in headers)
    print(fmt_row({h: h for h in headers}))
    print("  ".join("-" * col_widths[h] for h in headers))
    for r in rows:
        print(fmt_row(r))


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="mpcfill", description="MPCFill helper CLI")
    sub = p.add_subparsers(dest="command")

    # search
    sp = sub.add_parser("search", help="Search for cards and print best candidates")
    sp.add_argument("query", nargs="+", help="Card name(s) to search")
    sp.add_argument("--languages", nargs="*", help="Language codes (e.g., ENGLISH)")
    sp.add_argument("--include-tags", nargs="*")
    sp.add_argument("--exclude-tags", nargs="*")
    sp.add_argument("--minimum-dpi", type=int, default=600)
    sp.add_argument("--maximum-dpi", type=int, default=1500)
    sp.add_argument("--maximum-size", type=int, default=30)
    sp.add_argument("--fuzzy", action="store_true")
    sp.add_argument("--filter-cardbacks", action="store_true")
    sp.add_argument("--no-backs", action="store_true")
    sp.add_argument("--json", action="store_true", help="Output results as JSON (Type, Name, ID)")
    sp.set_defaults(func=cmd_search)

    # token queries are supported by prefixing with "t:" in the query list

    # download-best
    dp = sub.add_parser("download-best", help="Search and download best images to a folder")
    dp.add_argument("query", nargs="+", help="Card name(s) to search")
    dp.add_argument("--dest", required=True, help="Destination folder")
    dp.add_argument("--languages", nargs="*")
    dp.add_argument("--include-tags", nargs="*")
    dp.add_argument("--exclude-tags", nargs="*")
    dp.add_argument("--minimum-dpi", type=int, default=600)
    dp.add_argument("--maximum-dpi", type=int, default=1500)
    dp.add_argument("--maximum-size", type=int, default=30)
    dp.add_argument("--fuzzy", action="store_true")
    dp.add_argument("--filter-cardbacks", action="store_true")
    dp.add_argument("--no-backs", action="store_true")
    dp.set_defaults(func=cmd_download_best)

    # lists are handled via the unified `list` subcommand below

    # single `list` command with choices
    lp = sub.add_parser("list", help="List catalog data")
    lp.add_argument("what", choices=["sources", "languages", "tags", "dfcs"], help="What to list")
    def _dispatch_list(args: argparse.Namespace):
        if args.what == "sources":
            cmd_list_sources(args)
        elif args.what == "languages":
            cmd_list_languages(args)
        elif args.what == "tags":
            cmd_list_tags(args)
        elif args.what == "dfcs":
            cmd_list_dfcs(args)
    lp.set_defaults(func=_dispatch_list)

    return p


def main(argv: List[str] | None = None):
    parser = build_parser()
    args = parser.parse_args(argv)

    # Ensure proper SIGPIPE handling when piping output (e.g., to `head`)
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except Exception:
        pass

    try:
        # If a subcommand is provided, run it; otherwise print help
        if getattr(args, "command", None):
            args.func(args)
            return

        # No subcommand provided
        parser.print_help()
    except BrokenPipeError:
        # When piping to commands like `head`, the pipe may close early.
        # Silently exit to avoid noisy tracebacks.
        try:
            sys.stdout.close()
        except Exception:
            pass
        os._exit(0)
