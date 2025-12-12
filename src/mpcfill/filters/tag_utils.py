from typing import List, Union
from .tags import Tag, tag_hierarchy


def collapse_tags_to_parents(tags: List[Union[Tag, str]]) -> List[str]:
    """
    Collapse child tags into parents if both are selected.
    Returns tag names suitable for the MPCFill API.

    Rules:
    - If a parent and any of its descendants are both selected, keep only the parent.
    - Inputs can be `Tag` constants or raw strings; output is a list of tag names.
    - Unknown tag names are ignored.
    """

    if not tags:
        return []

    # Normalize input to raw tag names (strings)
    normalized = [t if isinstance(t, str) else str(t) for t in tags]

    # Map names to TagNode; drop unknowns
    nodes = {name: tag_hierarchy.find(name) for name in normalized}
    nodes = {name: node for name, node in nodes.items() if node is not None}

    if not nodes:
        return []

    final = set(nodes.keys())
    names = list(nodes.keys())

    # For each pair, if one is ancestor of the other, drop the descendant
    for i, parent_name in enumerate(names):
        parent_node = nodes[parent_name]
        for j, child_name in enumerate(names):
            if i == j:
                continue
            if parent_node.find(child_name) is not None:
                # parent contains child somewhere in its subtree
                if child_name in final and parent_name in final:
                    final.discard(child_name)

    return list(final)
