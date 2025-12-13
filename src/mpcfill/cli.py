import argparse
import os
import signal
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Dict, List

from . import (
    CardType,
    SearchSettings,
    fetch_dfcs,
    fetch_languages,
    fetch_sources,
    search_cards,
)


def _build_queries(raw_items: List[str]) -> List[Dict]:
    """Build search queries supporting token prefix 't:' per item."""
    q: List[Dict] = []
    for raw in raw_items:
        is_token = raw.lower().startswith("t:")
        name = raw[2:] if is_token else raw
        q.append(
            {"query": name, "cardType": CardType.TOKEN if is_token else CardType.CARD}
        )
    return q


def _apply_source_preferences(args: argparse.Namespace, settings: SearchSettings):
    """Apply source preferences.

    Disable first, then prefer order (enabling if needed).
    """
    if getattr(args, "disable_sources", None):
        for key in args.disable_sources:
            settings.disable_source(key)
    if getattr(args, "prefer_sources", None):
        for idx, key in enumerate(args.prefer_sources):
            settings.enable_source(key)
            settings.set_source_priority(key, idx)


def _print_table(headers: List[str], rows: List[Dict[str, str]]):
    if not rows:
        return
    col_widths = {
        h: max(len(h), max(len(str(r.get(h, ""))) for r in rows)) for h in headers
    }

    def fmt_row(r: Dict[str, str]):
        return "  ".join(str(r.get(h, "")).ljust(col_widths[h]) for h in headers)

    print(fmt_row({h: h for h in headers}))
    print("  ".join("-" * col_widths[h] for h in headers))
    for r in rows:
        print(fmt_row(r))


def cmd_search(args: argparse.Namespace):
    """Search for cards and print best candidates."""
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
    _apply_source_preferences(args, settings)
    queries = _build_queries(args.query)
    groups = search_cards(queries, settings, fetch_backs=not args.no_backs)
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
        return

    if getattr(args, "json", False):
        import json

        print(json.dumps(rows, ensure_ascii=False))
        return

    _print_table(["Type", "Name", "ID"], rows)


def cmd_download(args: argparse.Namespace):
    """Search and download best images to a folder."""
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
    _apply_source_preferences(args, settings)

    from .search import search_cards
    from .utils import make_safe_path

    queries = _build_queries(args.query)

    dest = Path(args.dest)
    groups = search_cards(queries, settings, fetch_backs=not args.no_backs)
    dest.mkdir(parents=True, exist_ok=True)

    def _download_one(idx: int, card):
        fname = f"{idx}_{make_safe_path(card.name)}.{card.extension}"
        return card.download_image(dest, filename=fname)

    if getattr(args, "threads", 1) and args.threads > 1:
        with ThreadPoolExecutor(max_workers=args.threads) as ex:
            futures = {
                ex.submit(_download_one, i, g[0]): i for i, g in enumerate(groups) if g
            }
            for fut in as_completed(futures):
                print(fut.result())
    else:
        for i, g in enumerate(groups):
            if not g:
                continue
            print(_download_one(i, g[0]))


def cmd_list_sources(_: argparse.Namespace):
    """List available sources as a simple table."""
    sources = list(fetch_sources().values())
    if not sources:
        return
    rows = [{"ID": str(s.get("pk", "")), "Name": s.get("name", "")} for s in sources]
    _print_table(["ID", "Name"], rows)


def cmd_list_languages(_: argparse.Namespace):
    """List available languages as a simple table."""
    langs = fetch_languages()
    if not langs:
        return
    rows = [
        {"Code": lang.get("code", ""), "Name": lang.get("name", "")} for lang in langs
    ]
    _print_table(["Code", "Name"], rows)


def cmd_list_tags(_: argparse.Namespace):
    """Render the tag hierarchy as an ASCII tree."""
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
    """List Dual-Faced Card pairs (front ↔ back)."""
    dfcs = fetch_dfcs()
    if not dfcs:
        return
    rows = [{"Front": f or "", "Back": b or ""} for f, b in dfcs.items()]
    _print_table(["Front", "Back"], rows)


def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argparse parser for the CLI."""
    p = argparse.ArgumentParser(prog="mpcfill", description="MPCFill helper CLI")
    sub = p.add_subparsers(dest="command")

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
    sp.add_argument(
        "--prefer-sources",
        nargs="*",
        help="Source names to prefer. Priority inferred from order (left to right).",
    )
    sp.add_argument("--disable-sources", nargs="*", help="Source names to disable")
    sp.add_argument(
        "--json", action="store_true", help="Output results as JSON (Type, Name, ID)"
    )
    sp.set_defaults(func=cmd_search)

    dp = sub.add_parser(
        "download", help="Search and download best images to a folder"
    )
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
    dp.add_argument(
        "--prefer-sources",
        nargs="*",
        help="Source names to prefer. Priority inferred from order (left to right).",
    )
    dp.add_argument("--disable-sources", nargs="*", help="Source names to disable")
    dp.add_argument(
        "--threads", type=int, default=1, help="Parallel download threads (default: 1)"
    )
    dp.set_defaults(func=cmd_download)

    lp = sub.add_parser("list", help="List catalog data")
    lp.add_argument(
        "what", choices=["sources", "languages", "tags", "dfcs"], help="What to list"
    )

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
    """CLI entrypoint: parse arguments and dispatch commands."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except Exception:
        pass

    try:
        if getattr(args, "command", None):
            args.func(args)
            return
        parser.print_help()
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
        os._exit(0)
