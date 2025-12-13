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
    """Fetch and cache the sources mapping from the service."""
    return client.get("/2/sources/")["results"]


@lru_cache(maxsize=1)
def fetch_languages() -> List[Dict]:
    """Fetch and cache the list of available languages."""
    return client.get("/2/languages/")["languages"]


@lru_cache(maxsize=1)
def fetch_tags() -> List[Dict]:
    """Fetch and cache the hierarchical tag definitions."""
    return client.get("/2/tags/")["tags"]


@lru_cache(maxsize=1)
def fetch_dfcs() -> Dict[str, str]:
    """Fetch and cache Dual-Faced Card pairs (front → back)."""
    return client.get("/2/DFCPairs")["dfcPairs"]
