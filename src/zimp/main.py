import tkinter as tk

from zimp.domain.state.game_state import GameState
from zimp.domain.movement.game_map import GameMap
from zimp.domain.events.events import Events
from zimp.domain.items.game_items import GameItems

from zimp.integration.game_controller import GameController
from zimp.ui.tk_app import TkGameView


def build_app() -> tk.Tk:
    """Composition root: replace dependencies here, not inside widgets."""
    root = tk.Tk()
    state = GameState()
    movement = GameMap()
    items = GameItems()
    events = Events()
    TkGameView(root, GameController(state, movement, items, events))
    return root


def main() -> None:
    build_app().mainloop()


if __name__ == "__main__":
    main()
