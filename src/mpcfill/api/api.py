from __future__ import annotations
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from .http import client
from mpcfill.models import Card
from mpcfill.search_settings import SearchSettings


def search_cards( queries: List[Dict], search_settings: SearchSettings) -> dict[Card]:
    """
    Search for cards by query.
    Returns a list of Card objects.
    """
    payload = {**search_settings.to_dict(), "queries": queries}
    response = client.post("/2/editorSearch/", data=payload)
    ids = [card_id for types in response.get("results", {}).values() for card_ids in types.values() for card_id in card_ids]
    cards = get_card_metadata(ids)
    return cards

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
