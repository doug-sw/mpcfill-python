from enum import Enum


class CardType(str, Enum):
    """Type of printable entity returned by searches."""

    CARD = "CARD"
    TOKEN = "TOKEN"
