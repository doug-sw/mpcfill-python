import json
from pathlib import Path
from functools import lru_cache
from typing import List, Union, Dict
from ..filters.tags import Tag

DATA_PATH = Path(__file__).parents[1] / "data" / "tag_hierarchy.json"
_TAG_HIERARCHY = {}

@lru_cache(1)
def _load_hierarchy() -> dict:
    """Load the full tag hierarchy from JSON."""
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)

def collapse_tags_to_parents(tags: List[Union[Tag, str]]) -> List[str]:
    """
    Collapse child tags into parents if both are selected.
    Returns a list of tag names suitable for the MPCFill API.
    """
    tag_names = {t.value if isinstance(t, Tag) else t for t in tags}
    hierarchy = _load_hierarchy()

    def is_child(tag: str, parent: str, subdict: dict) -> bool:
        """Check recursively if tag is under parent in the hierarchy"""
        for key, children in subdict.items():
            if key == parent:
                if tag in children:
                    return True
                return any(is_child(tag, child, children) for child in children)
            if children:
                if is_child(tag, parent, children):
                    return True
        return False

    result = set(tag_names)
    for parent in tag_names:
        for child in tag_names:
            if parent != child and is_child(child, parent, hierarchy):
                result.discard(child)
    return list(result)

