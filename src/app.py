
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from injector import inject, singleton
from src.driver import Driver
from src.webparser import WebParser
from src.di import global_injector
from typing import Literal, Optional
from src.settings import GameState


@singleton
class App:
    @inject
    def __init__(self, driver: Driver, parser: WebParser):
        self.driver = driver.driver
        self.parser = parser
        self.actions = ActionChains(driver.driver)

        self.game_state = self.parser.parse_game()

    # --------------状态----------------
    def get_state(self) -> GameState:
        return self.game_state

    # --------------动作----------------
    def refresh_waste(self) -> None:
        if self.game_state['stock']: el = self.game_state['stock'][0]['element']
        else: el = self.parser.el_turnOverWaste
        self.actions.click(el).perform()
        self.game_state = self.parser.parse_game()

    def move(self,
             _from: Literal['tableau', 'waste', 'foundation']='tableau',
             _to: Literal['tableau', 'foundation']='tableau',
             _frompile: Optional[int]=0,
             _fromdepth: Optional[int]=0,
             _topile: int=0) -> None:
        source_card = None; target_card = None
        if _from == 'tableau':
            if self.game_state['tableau'][_frompile]:
                source_card = self.game_state['tableau'][_frompile][_fromdepth]
                if source_card['is_back']: raise Exception(f'Backfaced card cannot be dragged! Card: {source_card}')
            else: raise Exception(f'Tableau pile{_frompile} is empty!')
        elif _from == 'waste':
            if self.game_state['waste']: source_card = self.game_state['waste'][0]
            else: raise Exception(f'Waste is empty! ')
        elif _from == 'foundation':
            if self.game_state['foundation'][_frompile]: source_card = self.game_state['foundation'][_frompile][0]
            else: raise Exception(f'Foundation pile{_frompile} is empty!')
        source = source_card['element']
        
        if _to == 'tableau':
            if self.game_state['tableau'][_topile]:
                target_card = self.game_state['tableau'][_topile][0]
                target = target_card['element']
                # color合法性判断
                if target_card['code']['color'] == source_card['code']['color']:
                    raise Exception(f"Color of source{source_card['code']} and target{target_card['code']} cannot be the same!")
            else:
                # rank合法性判断
                if source_card['code']['rank'] != 'K': raise Exception(f"Source should be K! Except: {source_card['code']}")
                target = self.parser.el_tableau[_topile]
        elif _to == 'foundation':
            if self.game_state['foundation'][_topile]:
                target_card = self.game_state['foundation'][_topile][0]
                target = target_card['element']
                # suit合法性判断
                if target_card['code']['suit'] != source_card['code']['suit']:
                    raise Exception(f"Suit of source{source_card['code']} and target{target_card['code']} should be the same!")
            else:
                # rank合法性判断
                if source_card['code']['rank'] != 'A': raise Exception(f"Source should be A! Except: {source_card['code']}")
                target = self.parser.el_foundation[_topile]

        self.actions.drag_and_drop(source=source, target=target).perform()
        self.game_state = self.parser.parse_game()

    def new_game(self) -> None:
        self.actions.click(self.parser.el_newgame).perform()
        try:
            WebDriverWait(self.driver, 2).until(EC.alert_is_present())
            self.driver.switch_to.alert.accept()
        except TimeoutException: pass
        self.game_state = self.parser.parse_game()

# debug
if __name__ == '__main__':
    app = global_injector.get(App)
    for i in range(10):
        app.refresh_waste()
        for card in app.get_state()['waste']:
            print(card['code']['rank'], card['pos'])
    
    app.new_game()
    