
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

        self.mode = "3card"
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
                # if source_card['is_back']: raise Exception(f'Backfaced card cannot be dragged! Card: {source_card}')
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

        self.actions.move_to_element_with_offset(source, 0, -65)
        self.actions.click_and_hold()
        self.actions.move_to_element_with_offset(target, 0, -55)
        self.actions.release()
        self.actions.perform()
        self.game_state = self.parser.parse_game()

    def new_game(self, mode: Literal[None, "1card", "3card"]=None) -> None:
        # 获胜时先关闭获胜窗口
        if sum([len(p) for p in self.game_state['foundation']]) == 52:
            try:
                close_button = WebDriverWait(self.driver, 1).until(
                    EC.element_to_be_clickable(self.parser.el_closeWinLocater)
                )
                self.actions.click(close_button).perform()
            except TimeoutException: pass

        if mode is None or self.mode == mode:
            self.actions.click(self.parser.el_newgame).perform()
            try:
                WebDriverWait(self.driver, 1).until(EC.alert_is_present())
                self.driver.switch_to.alert.accept()
            except TimeoutException: pass
        elif mode == "1card":
            self.actions.click(self.parser.el_settings).perform()
            self.actions.click(self.parser.el_mode1card).perform()
            try:
                WebDriverWait(self.driver, 1).until(EC.alert_is_present())
                self.driver.switch_to.alert.accept()
            except TimeoutException: pass
            self.actions.click(self.parser.el_closeSettings).perform()
            self.mode = mode
        elif mode == "3card":
            self.actions.click(self.parser.el_settings).perform()
            self.actions.click(self.parser.el_mode3card).perform()
            try:
                WebDriverWait(self.driver, 1).until(EC.alert_is_present())
                self.driver.switch_to.alert.accept()
            except TimeoutException: pass
            self.actions.click(self.parser.el_closeSettings).perform()
            self.mode = mode
        self.game_state = self.parser.parse_game()

# debug
if __name__ == '__main__':
    app = global_injector.get(App)
    for i in range(10):
        app.refresh_waste()
        for card in app.get_state()['waste']:
            print(card['code']['rank'], card['pos'])
    
    app.new_game()
    