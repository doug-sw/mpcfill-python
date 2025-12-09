import re
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import List, Dict, Any, Iterator
from mpcfill.api import fetch_tags
from mpcfill.utils import dict_to_namespace

# ------------------------------------------------------------
# Normalize a human-readable name into a Python-safe identifier
# ------------------------------------------------------------
def normalize_python_identifier(name: str) -> str:
    """
    Normalize a human-readable tag name into a valid Python identifier.
    Produces UPPER_SNAKE_CASE identifiers.

    Assumption: input always starts with a letter.
    """

    ident = name.upper()
    ident = re.sub(r"[^A-Z0-9_]", "_", ident)
    ident = re.sub(r"_+", "_", ident)
    ident = ident.strip("_")
    return ident

@dataclass
class Tag:
    id: int
    name: str
    parent_id: int | None = None

@dataclass
class TagNode:
    """
    Recursive dataclass for MPCFill tag trees.
    Wraps the raw dict and exposes keys as attributes with dot-access.
    Children automatically become TagNode instances.
    """

    _data: Dict[str, Any] = field(default_factory=dict)
    _ns: SimpleNamespace = field(init=False, repr=False)
    children: List["TagNode"] = field(init=False, default_factory=list)

    def __post_init__(self):
        # Extract children before namespace so they don't collide.
        raw_children = self._data.get("children", [])

        # Build namespace from all non-children fields
        non_child_data = {k: v for k, v in self._data.items() if k != "children"}
        self._ns = SimpleNamespace(**non_child_data)

        # Recursively wrap children
        self.children = [TagNode(_data=child) for child in raw_children]

    def __getattr__(self, item: str) -> Any:
        # Delegate attribute access to SimpleNamespace
        try:
            return getattr(self._ns, item)
        except AttributeError:
            raise AttributeError(
                f"{item!r} not found in tag fields {list(self._data.keys())}"
            )

    def __getitem__(self, key: str) -> Any:
        return self._data[key]

    def to_dict(self) -> Dict[str, Any]:
        """Convert back to raw dict form."""
        return {
            **{k: v for k, v in self._data.items() if k != "children"},
            "children": [child.to_dict() for child in self.children],
        }

    def walk(self):
        """Depth-first iteration over this tag and its descendants."""
        yield self
        for c in self.children:
            yield from c.walk()

    def find(self, name: str) -> "TagNode":
        """Find a tag anywhere in the tree by name."""
        for node in self.walk():
            if node.name.lower() == name.lower():
                return node
        return None

class TagHierarchy:
    """
    A helper around a list of TagNode roots.
    Provides:
    - fast lookup by name or alias
    - traversal helpers
    - normalization of names
    """

    def __init__(self):
        self.roots = [TagNode(data) for data in fetch_tags()]
        self._index = {node.name.lower(): node for node in self.walk()} 

    def find(self, name: str) -> TagNode | None:
        """Find a tag by name or alias."""
        return self._index.get(name.lower())

    def __getitem__(self, name: str) -> TagNode:
        found = self.find(name)
        if not found:
            raise KeyError(f"Tag {name!r} not found in hierarchy.")
        return found

    def walk(self):
        """Iterate all nodes in the entire hierarchy."""
        for root in self.roots:
            yield from root.walk()

    def flatten(self) -> List[TagNode]:
        """Return all nodes in a flat list."""
        return list(self.walk())


def build_tag_namespace(hierarchy: TagHierarchy) -> SimpleNamespace:
    """
    Converts TagHierarchy into a SimpleNamespace where:

    PIXEL_ART = "Pixel Art"
    FULL_ART = "Full-Art"
    LANDSCAPE_WIDE = "Landscape / Wide"

    Keys are Python-safe identifiers,
    Values remain human-readable names.
    """
    return dict_to_namespace({normalize_python_identifier(tag.name): tag.name for tag in hierarchy.walk()})

tag_hierarchy = TagHierarchy()
Tag = build_tag_namespace(tag_hierarchy)