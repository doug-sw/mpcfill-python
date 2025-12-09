from typing import Any, Dict, List, Optional
from mpcfill.models.source_filter import SourceFilter
from mpcfill.models.sources import SourceCollection
from mpcfill.filters.tags import Tag
from mpcfill.filters.tag_utils import collapse_tags_to_parents

MAXIMUM_DPI = 1500
MINIMUM_DPI = 0
MAXIMUM_SIZE = 30
MINIMUM_SIZE = 0


class SearchSettings:
    """
    Encapsulates MPCFill search settings:
    - search type settings (fuzzy search, filter cardbacks)
    - source settings (enabled/disabled, priority)
    - filter settings (DPI, size, languages, tags)
    """

    def __init__(
        self,
        sources: Optional[SourceCollection] = None,
        fuzzy_search: bool = False,
        filter_cardbacks: bool = False,
        minimum_dpi: int = 0,
        maximum_dpi: int = 1500,
        maximum_size: int = 30,
        languages: Optional[List[str]] = None,
        includes_tags: Optional[List[str]] = None,
        excludes_tags: Optional[List[str]] = None,
    ):
        self.fuzzy_search = fuzzy_search
        self.filter_cardbacks = filter_cardbacks
        self.source_filter = SourceFilter(sources)
        self.minimum_dpi = max(minimum_dpi, MINIMUM_DPI)
        self.maximum_dpi = min(maximum_dpi, MAXIMUM_DPI)
        self.maximum_size = min(maximum_size, MAXIMUM_SIZE)
        self.languages = languages if languages is not None else  []
        self.includes_tags = includes_tags if includes_tags is not None else []
        self.excludes_tags = excludes_tags if excludes_tags is not None else [Tag.NSFW]

    def add_include_tag(self, tag: str):
        self.includes_tags.append(tag)

    def remove_include_tag(self, tag: str):
        if tag in self.includes_tags:
            self.includes_tags.remove(tag)

    def add_exclude_tag(self, tag: str):
        if tag not in self.excludes_tags:
            self.excludes_tags.append(tag)

    def remove_exclude_tag(self, tag: str):
        if tag in self.excludes_tags:
            self.excludes_tags.remove(tag)

    def enable_source(self, key: int | str):
        self.source_filter.enable(key)

    def disable_source(self, key: int | str):
        self.source_filter.disable(key)

    def enable_all_sources(self):
        self.source_filter.enable_all()

    def disable_all_sources(self):
        self.source_filter.disable_all()

    def set_source_priority_highest(self, key: int | str):
        self.source_filter.set_priority_highest(key)

    def set_source_priority_lowest(self, key: int | str):
        self.source_filter.set_priority_lowest(key)

    def set_source_priority(self, key: int | str, index: int):
        self.source_filter.set_priority(key, index)

    def to_dict(self) -> Dict[str, Any]:
        """
        Build the searchSettings JSON payload for a search.
        """
        search_settings = {
            "searchSettings": {
                "searchTypeSettings": {
                    "fuzzySearch": self.fuzzy_search,
                    "filterCardbacks": self.filter_cardbacks,
                },
                "sourceSettings": {
                    "sources": self.source_filter.to_api_format()
                },
                "filterSettings": {
                    "minimumDPI": self.minimum_dpi,
                    "maximumDPI": self.maximum_dpi,
                    "maximumSize": self.maximum_size,
                    "languages": self.languages,
                    "includesTags": collapse_tags_to_parents(self.includes_tags),
                    "excludesTags": collapse_tags_to_parents(self.excludes_tags),
                },
            }
        }
        return search_settings
