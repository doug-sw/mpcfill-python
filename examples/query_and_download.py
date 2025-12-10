from mpcfill.filters import Tag, Language, CardType
from mpcfill.api import search_cards, fetch_dfcs
from mpcfill.search_settings import SearchSettings
from mpcfill.utils import make_safe_path


search_settings = SearchSettings(
	minimum_dpi=600,
	includes_tags=[],
	excludes_tags=[Tag.NSFW, Tag.WHITE_BORDER],
	languages=[Language.ENGLISH],
	fuzzy_search=False,
	filter_cardbacks=False,
)

search_settings.disable_all_sources()
search_settings.enable_source('PsilosX')
search_settings.enable_source('CompC')

queries = [
    {"query": "Bayou", "cardType": CardType.CARD},
    {"query": "Treasure", "cardType": CardType.TOKEN},
    {"query": "Avatar Aang", "cardType": CardType.CARD},
]

cards = search_cards(
    queries=queries,
    search_settings=search_settings,
    fetch_backs=True,
)

print(f'Found {len(cards)} cards.')
for index, card in enumerate(cards):
    print(f'Downloading card {index+1}/{len(cards)}: {card.name}')
    name = f'{index}_{make_safe_path(card.name)}.{card.extension}'
    card.download_image('/home/doug/Downloads', filename=name)