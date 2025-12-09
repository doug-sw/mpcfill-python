from typing import List, Union, Dict
from .tags import Tag, tag_hierarchy


def collapse_tags_to_parents(tags: List[Union[Tag, str]]) -> List[str]:
    """
    Collapse child tags into parents if both are selected.
    Returns a list of tag names suitable for the MPCFill API.

    - If the user selects BOTH a parent and any of its children,
      the child is removed.
    """

    if not tags:
        return []
    name_to_tag = {tag: tag_hierarchy.find(tag) for tag in tags}
    name_to_tag = {k:v for k, v in name_to_tag.items() if v is not None}

    selected_tags = set(tags)
    final_tags = set(tags)

    for parent_tag in selected_tags:
        for child_tag in selected_tags:
            if parent_tag == child_tag:
                continue
            if name_to_tag[parent_tag].find(child_tag) is not None:
                final_tags.discard(child_tag)
    return list(final_tags)
