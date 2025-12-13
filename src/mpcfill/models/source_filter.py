from .sources import SourceCollection


class SourceFilter:
    """Track enabled sources and their priority for searches.

    Allows enabling/disabling by ID or by name (case-insensitive),
    and supports reordering/prioritizing sources.
    """

    def __init__(self, sources: SourceCollection | None = None):
        """Initialize with a `SourceCollection`, building lookup maps."""
        if sources is None:
            sources = SourceCollection()
        self._id_map = {s.id: s for s in sources._sources}
        self._name_map = {s.name.lower(): s for s in sources._sources}
        self.enabled = {s.id: True for s in sources._sources}
        self._priority_order = [s.id for s in sources._sources]

    def disable(self, key: int | str):
        """Disable a source by numeric ID or name."""
        sid = self._resolve_key(key)
        if sid in self.enabled:
            self.enabled[sid] = False

    def enable(self, key: int | str):
        """Enable a source by numeric ID or name."""
        sid = self._resolve_key(key)
        if sid in self.enabled:
            self.enabled[sid] = True

    def disable_all(self):
        """Disable all sources."""
        for key in self.enabled:
            self.enabled[key] = False

    def enable_all(self):
        """Enable all sources."""
        for key in self.enabled:
            self.enabled[key] = True

    def _resolve_key(self, key: int | str) -> int:
        """Return numeric ID given a key (int or name)."""
        if isinstance(key, str):
            sid = self._name_map.get(key.lower())
            if sid is None:
                raise ValueError(f"No source with name '{key}'")
            return sid.id
        return key

    def set_priority(self, key: int | str, position: int):
        """Move a source to a specific position (0 = first, -1 = last)."""
        sid = self._resolve_key(key)
        if sid in self._priority_order:
            self._priority_order.remove(sid)
        if position < 0:
            position = len(self._priority_order) + 1 + position
        self._priority_order.insert(position, sid)

    def set_priority_lowest(self, key: int | str):
        """Move a source to the last position."""
        self.set_priority(key, -1)

    def set_priority_highest(self, key: int | str):
        """Move a source to the first position."""
        self.set_priority(key, 0)

    def move_to_index(self, key: int | str, index: int):
        """Move a source to a specific index in the priority list.

        Negative indices are supported (Python style).
        """
        sid = self._resolve_key(key)
        if sid in self._priority_order:
            self._priority_order.remove(sid)
        if index < 0:
            index = len(self._priority_order) + 1 + index
        self._priority_order.insert(index, sid)

    def to_api_format(self) -> list[list[int, bool]]:
        """Return [[id, enabled], ...] for MPCFill, preserving priority order."""
        return [[sid, self.enabled[sid]] for sid in self._priority_order]
