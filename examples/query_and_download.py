"""Query for cards and download best-matching images."""

from mpcfill import (
    CardType,
    Language,
    SearchSettings,
    search_cards,
)
from mpcfill.filters import Tags
from mpcfill.utils import make_safe_path

search_settings = SearchSettings(
    minimum_dpi=600,
    includes_tags=[],
    excludes_tags=[Tags.NSFW, Tags.WHITE_BORDER],
    languages=[Language.ENGLISH],
    fuzzy_search=False,
    filter_cardbacks=False,
)

search_settings.set_source_priority_highest("PsilosX")

queries = [
    {"query": "Dragon Egg", "cardType": CardType.CARD},
    {"query": "Dragon Egg", "cardType": CardType.TOKEN},
]

print(f"Searching {len(queries)} queries…")
card_groups = search_cards(
    queries=queries,
    search_settings=search_settings,
    fetch_backs=True,
)
print(f"Found candidates for {len(card_groups)} items.")

print("Downloading highest priority image for each result.")
for index, candidates in enumerate(card_groups):
    card = candidates[0]
    print(f"Downloading {index+1}/{len(card_groups)}: {card.name}")
    name = f"{index}_{make_safe_path(card.name)}.{card.extension}"
    card.download_image("downloads", filename=name)
