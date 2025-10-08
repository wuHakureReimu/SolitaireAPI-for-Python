# SolitaireAPI-for-Python

---

This is a Python interaction interface for the visual online solitaire game (https://solitaire.online/zh). To use this interface, you can import it in any script under the project root directory with the following line:

```python
from src.app import App
```

The `App` class provides only 4 interfaces, as listed below:

## 1. Core Interfaces
### 1.1 get_state()
Retrieves the current GameState (the full state of the solitaire game).

### 1.2 refresh_waste()
Refreshes the waste pile. Specifically, it draws 3 cards from the top of the stock pile and places them onto the waste pile.

### 1.3 move(_from, _to, _frompile, _fromdepth, _topile)
Moves cards from a source pile to a target pile. The parameters are defined as follows:
- `_from`: Type of the **source** pile (e.g., "waste", "tableau").
- `_to`: Type of the **target** pile (e.g., "tableau", "foundation").
- `_frompile`: Index of the source pile (0-based).
- `_fromdepth`: Depth of the starting card in the source pile (0 refers to the top card).
- `_topile`: Index of the target pile (0-based).

**Examples**:
```python
# Moves the top card of the current waste pile to the 0th tableau pile
move(_from="waste", _to="tableau", _topile=0)

# Moves all cards starting from the 3rd card (0-based) in the 6th tableau pile to the 1st tableau pile
move(_from="tableau", _to="tableau", _frompile=6, _fromdepth=3, _topile=1)

# Moves the top card of the current waste pile to the 3rd (last) foundation pile
move(_from="waste", _to="foundation", _topile=3)
```

### 1.4 new_game()
Starts a new solitaire game.

## 2. Reference Files
- **Demo Usage**: See `demo.py` for a complete example that covers the usage of all App interfaces.
- **Data Format**: Check `src/settings.py` to view the structure of `GameState` and other related data. You don’t need to memorize the data protocol— the data annotations in `settings.py` enable IDEs to provide automatic field completion.

## 3. Environment Setup
Refer to requirements.txt for the required dependencies to configure your Python environment. You can typically install dependencies using the following command:
```bash
pip install -r requirements.txt
```

---