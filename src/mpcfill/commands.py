from __future__ import annotations
from pathlib import Path
from typing import List, Dict, Iterable

from .search import search_cards
from .search_settings import SearchSettings
from .types import CardType
from .services.catalog import fetch_sources, fetch_languages, fetch_tags, fetch_dfcs


def list_sources() -> Dict:
    return fetch_sources()


def list_languages() -> List[Dict]:
    return fetch_languages()


def list_tags() -> List[Dict]:
    return fetch_tags()


def list_dfcs() -> Dict[str, str]:
    return fetch_dfcs()


def search_best(queries: Iterable[str], settings: SearchSettings, include_tokens: bool = False, include_backs: bool = True):
    q: List[Dict] = [{"query": name, "cardType": CardType.CARD} for name in queries]
    if include_tokens:
        q.extend({"query": name, "cardType": CardType.TOKEN} for name in queries)

    groups = search_cards(q, settings, fetch_backs=include_backs)
    return [g[0] for g in groups if g]


def search_and_download_best(queries: Iterable[str], dest: str | Path, settings: SearchSettings, filename_format: str = "{index}_{name}.{ext}", include_tokens: bool = False, include_backs: bool = True) -> List[Path]:
    from .utils import make_safe_path

    best = search_best(queries, settings, include_tokens=include_tokens, include_backs=include_backs)
    dest_path = Path(dest)
    dest_path.mkdir(parents=True, exist_ok=True)

    results: List[Path] = []
    for i, card in enumerate(best):
        fname = filename_format.format(index=i, name=make_safe_path(card.name), ext=card.extension, id=card.identifier)
        results.append(card.download_image(dest_path, filename=fname))
    return results