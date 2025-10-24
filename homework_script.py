

from src.di import global_injector
from src.app import App
from util.format import FormatCard, CardInfo

game = global_injector.get(App)
game.new_game(mode='1card')



if __name__ == "__main__":
    
    refresh_cnt = 0

    score_lst = []

    for _ in range(100):
        while True:
            state = game.get_state()
            cf = False
            
            # step0 判断获胜
            if sum([len(p) for p in state['foundation']]) == 52:
                print("WIN")
                break

            # step1 把能直接放到foundation的都放到foundation
            # 检查tableau
            for i, pile in enumerate(state['tableau']):
                if pile:
                    card = FormatCard(pile[0])
                    foundation_pile = state['foundation'][card.suit]
                    if foundation_pile:
                        top = FormatCard(foundation_pile[0])
                        if top.rank == card.rank - 1:
                            game.move("tableau", "foundation", i, 0, card.suit)
                            cf = True
                            refresh_cnt = 0
                            break
                    else:
                        if card.rank == 1:
                            game.move("tableau", "foundation", i, 0, card.suit)
                            cf = True
                            refresh_cnt = 0
                            break
            if cf: continue
            # 检查waste
            if not state['waste'] and state['stock']: game.refresh_waste(); continue
            elif state['waste']:
                card = FormatCard(state['waste'][0])
                foundation_pile = state['foundation'][card.suit]
                if foundation_pile:
                    top = FormatCard(foundation_pile[0])
                    if top.rank == card.rank - 1:
                        game.move("waste", "foundation", _topile=card.suit)
                        refresh_cnt = 0
                        continue
                else:
                    if card.rank == 1:
                        game.move("waste", "foundation", _topile=card.suit)
                        refresh_cnt = 0
                        continue
            
            # step2 把waste顶部的牌放到它能放的最左侧tableau牌堆
            if state['waste']:
                card = FormatCard(state['waste'][0])
                for i, pile in enumerate(state['tableau']):
                    if pile:
                        top = FormatCard(pile[0])
                        if top.color != card.color and top.rank == card.rank + 1:
                            game.move('waste', 'tableau', _topile=i)
                            cf = True
                            refresh_cnt = 0
                            break
                    else:
                        if card.rank == 13:
                            game.move('waste', 'tableau', _topile=i)
                            cf = True
                            refresh_cnt = 0
                            break
                if cf: continue

            # step3 把最左侧的tableau牌堆放到它能放的最左侧tableau牌堆
            for i, src_pile in enumerate(state['tableau']):
                if not src_pile: continue
                j = 0
                while j < len(src_pile) and not src_pile[j]['is_back']: j += 1
                card_idx_in_available = j - 1
                card = FormatCard(src_pile[card_idx_in_available])
                for l, dst_pile in enumerate(state['tableau']):
                    if l == i: continue
                    if dst_pile:
                        top = FormatCard(dst_pile[0])
                        if top.color != card.color and top.rank == card.rank + 1:
                            game.move('tableau', 'tableau', i, card_idx_in_available, l)
                            cf = True
                            refresh_cnt = 0
                            break
                    else:
                        if card.rank == 13 and j < len(src_pile):
                            game.move('tableau', 'tableau', i, card_idx_in_available, l)
                            cf = True
                            refresh_cnt = 0
                            break
                if cf: break
            if cf: continue

            # step4 从stock移动一张牌到waste
            if len(state['stock'])+len(state['waste']) > 0: game.refresh_waste()
            refresh_cnt += 1
            if refresh_cnt > len(state['stock']) + len(state['waste']) + 3:
                print("deadlock")
                break
        
        end_foundation = game.get_state()['foundation']
        score = 0
        for pile in end_foundation: score += 5 * len(pile)
        score_lst.append(score)
        print(f"Scores: {score_lst}")
        print(f"mean: {sum(score_lst)/len(score_lst)}")
        # input()
        game.new_game('1card')
    
