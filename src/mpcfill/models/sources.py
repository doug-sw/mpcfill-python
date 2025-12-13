import csv
import json
from dataclasses import dataclass, field
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List

from ..services.catalog import fetch_sources
from ..utils import dict_to_namespace

DEFAULT_SOURCES_PATH = Path(__file__).parents[1] / "data" / "sources.json"


@dataclass
class Source:
    """Lightweight wrapper over raw source metadata."""

    _data: Dict[str, Any] = field(default_factory=dict)
    _ns: SimpleNamespace = field(init=False, repr=False)

    def __post_init__(self):
        """Create a namespace for attribute-style access to metadata."""
        self._ns = dict_to_namespace(self._data)

    def __getattr__(self, item: str) -> Any:
        """Delegate attribute access to the namespace created from _data."""
        try:
            return getattr(self._ns, item)
        except AttributeError:
            raise AttributeError(
                f"{item!r} not found in metadata fields {list(self._data.keys())}"
            )

    def __getitem__(self, key: str) -> Any:
        """Dict-style access to raw metadata values."""
        return self._data[key]

    def keys(self):
        """Return metadata keys."""
        return self._data.keys()

    def items(self):
        """Return metadata (key, value) pairs."""
        return self._data.items()

    def to_dict(self) -> Dict[str, Any]:
        """Return a shallow copy of the raw metadata dict."""
        return dict(self._data)

    @property
    def id(self):
        """Convenience alias for `pk` used by the API."""
        return self.pk


class SourceCollection:
    """Hold all sources and provide ID/name lookups."""

    def __init__(self):
        """Load sources from the catalog and build lookup indices."""
        self._sources = [Source(data) for data in fetch_sources().values()]
        self._id_map = {s.id: s for s in self._sources}
        self._name_map = {s.name.lower(): s for s in self._sources}

    def get_by_id(self, sid: int) -> Source | None:
        """Return a source by numeric ID, or None if missing."""
        return self._id_map.get(sid)

    def get_by_name(self, name: str) -> Source | None:
        """Return a source by case-insensitive name, or None if missing."""
        return self._name_map.get(name.lower())

    def all_ids(self) -> list[int]:
        """Return a list of all source IDs."""
        return [s.id for s in self._sources]

    def all_names(self) -> list[str]:
        """Return a list of all source names."""
        return [s.name for s in self._sources]

    @staticmethod
    def load_sources(path: Path) -> List[Source]:
        """Load sources from a JSON or CSV/TSV file path."""
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
                        {
                            "id": int(row["id"]),
                            "name": row["name"],
                            "url": row.get("url"),
                        }
                    )
        else:
            raise ValueError(f"Unsupported file type for sources: {path.suffix}")

        sources = [Source(**item) for item in data]
        return sources
