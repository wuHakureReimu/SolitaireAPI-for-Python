

from selenium.webdriver.common.by import By
import re
from src.driver import Driver
from injector import inject, singleton
from src.di import global_injector
from src.settings import CardCode, CardInfo, GameState

@singleton
class WebParser:
    @inject
    def __init__(self, driver: Driver):
        self.driver = driver.driver
        self.cards = []
        
        # 静态元素
        self.el_turnOverWaste = self.driver.find_element(By.CSS_SELECTOR, ".turnOverWasteImage")
        self.el_tableau = self.driver.find_elements(By.CSS_SELECTOR, '.tableauPileBase')
        self.el_foundation = self.driver.find_elements(By.CSS_SELECTOR, '.foundationBase')
        self.el_newgame = self.driver.find_element(By.CSS_SELECTOR, '.top-menu__btn')
    
    # 解析cards数据
    @property
    def cards_info(self) -> list[CardInfo]:
        result = []
        for card in self.cards:
            id = card.get_attribute('id')
            style = card.get_attribute('style')
            classes = card.get_attribute('class').split()

            left = float(re.search(r'left:\s*(\d+\.?\d*)px', style).group(1))
            top = float(re.search(r'top:\s*(\d+\.?\d*)px', style).group(1))
            z_index = int(re.search(r'z-index:\s*(\d+)', style).group(1))

            for name in classes:
                if name != 'card' and name != 'cardback':
                    code = self._decode_card(name.replace('card', ''))

            result.append({
                'id': id,
                'code': code,
                'is_back': 'cardback' in classes,
                'pos':{
                    'left': left,
                    'top': top,
                    'z_index': z_index
                },
                'element': card       # 原始未解析元素
            })
        return result
   
    @property
    def game_state(self) -> GameState:
        state = {
            'tableau': [[] for _ in range(7)], 
            'foundation': [[] for _ in range(4)],
            'stock': [],
            'waste': []
        }
        for card in self.cards_info:
            left, top = card['pos']['left'], card['pos']['top']
            if 268 <= top <= 500:  # Tableau区域
                if 30 <= left <= 153:  # 第1列
                    state['tableau'][0].append(card)
                elif 159 <= left <= 282:  # 第2列
                    state['tableau'][1].append(card)
                elif 288 <= left <= 411:  # 第3列
                    state['tableau'][2].append(card)
                elif 417 <= left <= 540:  # 第4列
                    state['tableau'][3].append(card)
                elif 546 <= left <= 669:  # 第5列
                    state['tableau'][4].append(card)
                elif 675 <= left <= 798:  # 第6列
                    state['tableau'][5].append(card)
                elif 804 <= left <= 927:  # 第7列
                    state['tableau'][6].append(card)
            elif top == 30 and left > 400:  # Foundation区域
                if 417 <= left <= 540:  # Foundation 1
                    state['foundation'][0].append(card)
                elif 546 <= left <= 669:  # Foundation 2
                    state['foundation'][1].append(card)
                elif 675 <= left <= 798:  # Foundation 3
                    state['foundation'][2].append(card)
                elif 804 <= left <= 927:  # Foundation 4
                    state['foundation'][3].append(card)
            elif top == 30:  # Stock/Waste区域
                if left <= 31: state['stock'].append(card)
                else: state['waste'].append(card)
        # format
        for pile in state['tableau']:
            pile.sort(key=lambda x: x['pos']['z_index'], reverse=True)
        for foundation in state['foundation']:
            foundation.sort(key=lambda x: x['pos']['z_index'], reverse=True)
        state['stock'].sort(key=lambda x: x['pos']['z_index'], reverse=True)
        state['waste'].sort(key=lambda x: x['pos']['z_index'], reverse=True)

        return state

    def _decode_card(self, card_code: str) -> CardCode:
        special_cards = {
            'ac': ('A', 'Clubs'), 'ad': ('A', 'Diamonds'), 'ah': ('A', 'Hearts'), 'as': ('A', 'Spades'),
            'jc': ('J', 'Clubs'), 'jd': ('J', 'Diamonds'), 'jh': ('J', 'Hearts'), 'js': ('J', 'Spades'),
            'qc': ('Q', 'Clubs'), 'qd': ('Q', 'Diamonds'), 'qh': ('Q', 'Hearts'), 'qs': ('Q', 'Spades'),
            'kc': ('K', 'Clubs'), 'kd': ('K', 'Diamonds'), 'kh': ('K', 'Hearts'), 'ks': ('K', 'Spades'),
            'tc': ('10', 'Clubs'), 'td': ('10', 'Diamonds'), 'th': ('10', 'Hearts'), 'ts': ('10', 'Spades')
        }
        suit_color_map = {
            'Hearts': 'red',
            'Diamonds': 'red', 
            'Clubs': 'black',
            'Spades': 'black'
        }
        if card_code in special_cards:
            rank, suit = special_cards[card_code]
            color = suit_color_map.get(suit, 'Unknown')
            return {'rank': rank, 'suit': suit, 'color': color, 'full_name': f'{rank} of {suit}'}
        if len(card_code) == 2:
            rank_map = {'c': 'Clubs', 'd': 'Diamonds', 'h': 'Hearts', 's': 'Spades'}
            rank = card_code[0]
            suit_char = card_code[1]
            suit = rank_map.get(suit_char, 'Unknown')
            color = suit_color_map.get(suit, 'Unknown')
            return {'rank': rank, 'suit': suit, 'color': color, 'full_name': f'{rank} of {suit}'}
        
        return {'rank': 'Unknown', 'suit': 'Unknown', 'color': 'Unknown', 'full_name': 'Unknown'}
    
    # 最外层call
    def parse_game(self) -> GameState:
        # CSS选择器定位全部52张卡牌
        self.cards = self.driver.find_elements(By.CSS_SELECTOR, '#solitaireCanvas .card')
        return self.game_state
    
    # debug
    def print_game_state(self) -> None:
        game_state = self.game_state
        print("\nTableau piles:")
        for i, pile in enumerate(game_state['tableau']):
            print(f"  Pile {i}: {[card['code']['full_name'] for card in pile]}")
        
        print("\nFoundation piles:")
        for i, foundation in enumerate(game_state['foundation']):
            print(f"  Foundation {i}: {[card['code']['full_name'] for card in foundation]}")
        
        print(f"\nStock: {len(game_state['stock'])} cards")
        print(f"Waste: {[card['code']['full_name'] for card in game_state['waste']]}")

# debug
if __name__ == "__main__":
    parser = global_injector.get(WebParser)
    parser.parse_game()
    parser.print_game_state()

    input()
    del parser