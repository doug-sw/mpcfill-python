from mpcfill.filters import Tag, Language, CardType
from mpcfill.models import Card
from mpcfill.api import search_cards
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

queries = [
    {"query": "Bayou", "cardType": CardType.CARD},
    {"query": "Deflecting Swat", "cardType": CardType.CARD},
    {"query": "Treasure", "cardType": CardType.TOKEN}
]

cards = search_cards(
    queries=queries,
    search_settings=search_settings,
)
print(f'Found {len(cards)} cards.')

from pprint import pprint

for index, card in enumerate(cards):
    print(f'Downloading card {index+1}/{len(cards)}: {card.name}')
    name = f'{index}_{make_safe_path(card.name)}.{card.extension}'
    card.download_image('/home/doug/Downloads', filename=name)