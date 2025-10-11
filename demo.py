

from injector import inject, singleton
from src.di import global_injector
from src.app import App


@singleton
class Solution:
    @inject
    def __init__(self, app: App):
        # 纸牌交互接口对象
        self.app = app
        app.new_game(mode='1card')

    def demo(self) -> None:
        # 获取当前状态
        state = self.app.get_state()

        # 遍历tableau的七个牌堆，如果有A那就塞到foundation
        for i, pile in enumerate(state['tableau']):
            if pile:
                if pile[0]['code']['rank'] == 'A':
                    #将tableau第i个pile的第0张牌拖到foundation的第0个pile上
                    self.app.move(_from='tableau', _to='foundation', _frompile=i, _fromdepth=0, _topile=0)
                    break
        
        state = self.app.get_state()
        # 遍历stock堆，如果waste有A那就塞到foundation
        while len(state['stock']) > 0:
            # 刷新waste，即从stock拿1张牌到waste上
            self.app.refresh_waste()
            state = self.app.get_state()
            if state['waste']:
                if state['waste'][0]['code']['rank'] == 'A':
                    self.app.move(_from='waste', _to='foundation', _topile=3)
                    break
    
    def new_game(self) -> None:
        # 开新一局
        self.app.new_game(mode='3card')

if __name__ == "__main__":
    solution = global_injector.get(Solution)
    solution.demo()
    solution.new_game()
    solution.demo()
    input()