
from injector import singleton
from typing import TypedDict, Literal
from selenium.webdriver.remote.webelement import WebElement


@singleton
class Settings:
    url: str = "https://solitaire.online/zh"
    mode: Literal["1card", "3card"] = "3card"

@singleton
class Mapping:
    pass


class CardCode(TypedDict):
    rank: Literal['A','2','3','4','5','6','7','8','9','10','J','Q','K', 'Unknown'] = 'Unknown'
    suit: Literal['Hearts', 'Diamonds', 'Spades', 'Clubs', 'Unknown'] = 'Unknown'
    color: Literal['black', 'red', 'Unknown'] = 'Unknown'
    full_name: str = 'Unknown'

class CardPosition(TypedDict):
    left: float
    top: float
    z_index: int

class CardInfo(TypedDict):
    id: str
    code: CardCode
    is_back: bool
    pos: CardPosition
    element: WebElement

class GameState(TypedDict):
    tableau: list[list[CardInfo]]
    foundation: list[list[CardInfo]]
    stock: list[CardInfo]
    waste: list[CardInfo]