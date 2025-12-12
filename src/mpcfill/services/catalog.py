from __future__ import annotations
from functools import lru_cache
from typing import Dict, List
from ..http.client import client

__all__ = [
    "fetch_sources",
    "fetch_languages",
    "fetch_tags",
    "fetch_dfcs",
]

@lru_cache(maxsize=1)
def fetch_sources() -> Dict:
    return client.get("/2/sources/")["results"]

@lru_cache(maxsize=1)
def fetch_languages() -> List[Dict]:
    return client.get("/2/languages/")["languages"]

@lru_cache(maxsize=1)
def fetch_tags() -> List[Dict]:
    return client.get("/2/tags/")["tags"]

@lru_cache(maxsize=1)
def fetch_dfcs() -> Dict[str, str]:
    return client.get("/2/DFCPairs")["dfcPairs"]
