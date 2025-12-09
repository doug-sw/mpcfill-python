from __future__ import annotations
import base64
from types import SimpleNamespace
from typing import Any, Dict, Optional
from pathlib import Path
from mpcfill.utils import dict_to_namespace, namespace_to_dict
import shutil

_PATH_CACHE: Dict[str, Path] = {}


class Card:
    """
    Represents a card from MPCFill.

    Attributes from the raw MPCFill JSON/dict are accessible as attributes
    via automatic delegation to an internal SimpleNamespace (_data).

    Example:
        card = Card(data)
        print(card.name)
        print(card.cardType)
    """

    def __init__(self, data: Dict[str, Any]):
        """
        Construct a Card from a raw MPCFill JSON/dict.

        Args:
            data (Dict[str, Any]): Raw card data from MPCFill API.
        """
        self._data = dict_to_namespace(data)

    def __getattr__(self, item: str) -> Any:
        """
        Delegate attribute access to the internal _data SimpleNamespace.

        Args:
            item (str): Attribute name.

        Returns:
            Any: Value of the attribute if it exists.

        Raises:
            AttributeError: If the attribute does not exist in _data.
        """
        if hasattr(self._data, item):
            return getattr(self._data, item)
        raise AttributeError(f"'Card' object has no attribute '{item}'")

    def __repr__(self) -> str:
        """
        Represent the Card with name, type, and identifier.

        Returns:
            str: Human-readable representation of the Card.
        """
        name = getattr(self._data, "name", None)
        identifier = getattr(self._data, "identifier", None)
        card_type = getattr(self._data, "cardType", None)
        return f"<Card name={name!r} type={card_type!r} id={identifier!r}>"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the internal _data SimpleNamespace back to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the card.
        """
        return namespace_to_dict(self._data)

    def download_image(
        self,
        dest_folder: str | Path,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Download the card image to a specified folder.

        If the card has been downloaded previously in this session, the method
        will attempt to create a hardlink from the cached path to the destination
        path. If hardlinking fails (e.g., on different filesystems), it will
        fallback to copying the file.

        The cache is in-memory only and stores the path of the previously
        downloaded file. There is no persistent cache on disk outside the
        destination folder.

        Args:
            dest_folder (str | Path): Destination folder to save the card image.
            filename (Optional[str]): Optional filename. Defaults to
                "<card_id>.<extension>" if not provided.

        Returns:
            Path: Path to the downloaded image file.

        Raises:
            ValueError: If the card has no download link.
        """
        from mpcfill.api.http import client
        if not hasattr(self, "downloadLink") or not self.downloadLink:
            raise ValueError(f"Card {self.identifier} has no download link")

        dest_folder = Path(dest_folder)
        dest_folder.mkdir(parents=True, exist_ok=True)

        ext = getattr(self, "extension")
        file_name = filename or f"{self.identifier}.{ext}"
        dest_path = dest_folder / file_name

        # If we have a cached path and it exists, create a hardlink
        cached_path = _PATH_CACHE.get(self.identifier)
        if cached_path and cached_path.exists():
            if not dest_path.exists():
                try:
                    dest_path.link_to(cached_path)
                except OSError:
                    shutil.copy2(cached_path, dest_path)
            return dest_path

        # Otherwise, download the image from MPCFill
        content = client.raw_get(self.downloadLink)
        dest_path.write_bytes(content)

        # Store the downloaded path in the in-memory cache
        _PATH_CACHE[self.identifier] = dest_path

        return dest_path
