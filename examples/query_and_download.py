from mpcfill import (
    search_cards,
    SearchSettings,
    CardType,
    Language,
    Tag,
)
from mpcfill.utils import make_safe_path
from pprint import pprint


search_settings = SearchSettings(
	minimum_dpi=600,
	includes_tags=[],
	excludes_tags=[Tag.NSFW, Tag.WHITE_BORDER],
	languages=[Language.ENGLISH],
	fuzzy_search=False,
	filter_cardbacks=False,
)

search_settings.set_source_priority_highest('PsilosX')

queries = [
    {"query": "Dragon Egg", "cardType": CardType.CARD},
    {"query": "Dragon Egg", "cardType": CardType.TOKEN},
]

print(f'Searching for {len(queries)} cards...')
card_groups = search_cards(
    queries=queries,
    search_settings=search_settings,
    fetch_backs=True,
)
print(f'...found candidates for {len(card_groups)} cards.')

print(f'Grabbing highest priority image for each card.')
for index, candidates in enumerate(card_groups):
    card = candidates[0]  # or min(candidates, key=lambda candidate: candidate.priority)
    print(f'Downloading card {index+1}/{len(card_groups)}: {card.name}')
    name = f'{index}_{make_safe_path(card.name)}.{card.extension}'
    card.download_image('/home/doug/Downloads', filename=name)
