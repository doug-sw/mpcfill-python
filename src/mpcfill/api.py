from __future__ import annotations
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .http import client
from mpcfill.models.card import Card
from mpcfill.filters import CardType
import json
from functools import lru_cache

def search_cards( queries: List[Dict], search_settings: "SearchSettings", fetch_backs: bool = True) -> dict[Card]:
    """
    Search for cards by query.
    Returns a list of Card objects.
    """
    if fetch_backs:
        queries.extend(_get_card_backs(queries))
    payload = {**search_settings.to_dict(), "queries": queries}
    response = client.post("/2/editorSearch/", data=payload)
    ids = [card_id for types in response.get("results", {}).values() for card_ids in types.values() for card_id in card_ids]
    cards = get_card_metadata(ids)
    return cards

def _get_card_backs(queries: List[Dict], fetch_backs: bool = True) -> List[Dict[str, str]]:
    """ Helper function to generate queries for card backs. """
    names = set(q['query'] for q in queries)
    dfc_name_map = fetch_dfcs()
    new_queries = []
    for front_name in names:
        back_name = dfc_name_map.get(front_name)
        if back_name is None:
            continue
        new_queries.append({'query': back_name, 'cardType': CardType.CARD})
    return new_queries


def get_card_metadata(card_ids: List[str]) -> List[Card]:
    """
    Fetch full metadata for a list of card identifiers.
    """
    if not card_ids:
        return []

    payload = {"cardIdentifiers": card_ids}
    response = client.post("/2/cards/", data=payload)

    cards: List[Card] = []
    for card_id, data in response.get("results", {}).items():
        cards.append(Card(data))

    return cards

@lru_cache(maxsize=1)
def fetch_sources() -> List[Dict]:
    """Fetch available sources from MPCFill."""
    return client.get("/2/sources/")["results"]

@lru_cache(maxsize=1)
def fetch_languages() -> List[Dict]:
    """Fetch supported languages from MPCFill."""
    return client.get("/2/languages/")["languages"]

@lru_cache(maxsize=1)
def fetch_tags() -> List[Dict]:
    """Fetch available tags (e.g., NSFW, Full-Art)."""
    return client.get("/2/tags/")["tags"] 

@lru_cache(maxsize=1)
def fetch_dfcs() -> Dict[str, str]:
    """Fetch dfc card names, organized as {'name:card_front': 'name:card_back', ...}"""
    return client.get("/2/DFCPairs")["dfcPairs"]

