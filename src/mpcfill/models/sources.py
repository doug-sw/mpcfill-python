# src/mpcfill/search/sources.py

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List
import json
import csv

# -----------------------------
# Data classes
# -----------------------------

DEFAULT_SOURCES_PATH = Path(__file__).parents[1] / 'data' / 'sources.json'

@dataclass
class Source:
    id: int
    name: str
    url: str | None = None


class SourceCollection:
    """
    Holds all sources and allows convenient access by ID or name.
    """

    def __init__(self, sources: Iterable[Source] | None = None):
        self._sources: List[Source]
        if sources is None:
            sources = SourceCollection.load_sources(DEFAULT_SOURCES_PATH)
        self._sources = sources
        self._id_map = {s.id: s for s in self._sources}
        self._name_map = {s.name.lower(): s for s in self._sources}

    def get_by_id(self, sid: int) -> Source | None:
        return self._id_map.get(sid)

    def get_by_name(self, name: str) -> Source | None:
        return self._name_map.get(name.lower())

    def all_ids(self) -> list[int]:
        return [s.id for s in self._sources]

    def all_names(self) -> list[str]:
        return [s.name for s in self._sources]

    @staticmethod
    def load_sources(path: Path) -> List[Source]:
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Sources file not found: {path}")

        if path.suffix.lower() == ".json":
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        elif path.suffix.lower() in [".csv", ".tsv"]:
            data = []
            with open(path, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    data.append(
                        {"id": int(row["id"]), "name": row["name"], "url": row.get("url")}
                    )
        else:
            raise ValueError(f"Unsupported file type for sources: {path.suffix}")

        sources = [Source(**item) for item in data]
        return sources

    @classmethod
    def from_path(cls, path: Path) -> "SourceCollection":
        """
        Load the sources from a JSON or CSV/TSV file.
        Returns a SourceCollection.
        """
        
        return cls(sources)