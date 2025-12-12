from functools import lru_cache
from ..utils import dict_to_namespace
from ..services.catalog import fetch_languages
import re
from types import SimpleNamespace

def build_language_namespace() -> SimpleNamespace:
    """
    Convert the MPCFill languages list into a SimpleNamespace.

    Example output:
        LANG.SPANISH  -> "ES"
        LANG.JAPANESE -> "JA"
    """
    return dict_to_namespace({lang["name"].upper(): lang["code"] for lang in fetch_languages()})

Language = build_language_namespace()