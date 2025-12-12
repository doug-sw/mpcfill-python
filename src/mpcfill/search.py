from __future__ import annotations
from typing import List, Dict
from .http.client import client
from .models.card import Card
from .search_settings import SearchSettings
from .utils import normalize_query
from collections import defaultdict
from .services.catalog import fetch_dfcs
from .types import CardType

def search_cards(queries: List[Dict], search_settings: SearchSettings, fetch_backs: bool = True) -> List[List[Card]]:
    """
    Search for cards by query.
    Returns a list of Card objects.
    """
    if fetch_backs:
        queries.extend(_get_card_backs(queries))

    for query in queries:
        query['query'] = normalize_query(query['query'])

    payload = {**search_settings.to_dict(), "queries": queries}
    response = client.post("/2/editorSearch/", data=payload)
    ids = [card_id for types in response.get("results", {}).values() for card_ids in types.values() for card_id in card_ids]
    cards = get_card_metadata(ids)

    cards_by_type = {CardType.CARD: defaultdict(list), CardType.TOKEN: defaultdict(list)}
    for card in cards:
        cards_by_type[card.cardType][card.searchq].append(card)

    card_groups = [card_list for searchqs in cards_by_type.values() for searchq, card_list in searchqs.items()]
    for card_group in card_groups:
        card_group.sort(key=lambda card: card.priority)

    card_groups.sort(key=lambda card_group: card_group[0].searchq)
    return card_groups

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
