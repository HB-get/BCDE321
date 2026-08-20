import tkinter as tk
from tkinter import ttk

from zimp.integration.game_controller import GameController



class TkGameView:
    """Minimal accessible shell. Visual sophistication is not assessed."""

    def __init__(self, root: tk.Tk, controller: GameController) -> None:
        self._root = root
        self._controller = controller

        root.title("Zombie in My Pocket")
        root.minsize(600, 700)

        frame = ttk.Frame(root, padding=16)
        frame.grid(row=0, column=0, sticky="nsew")
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        row = 0

        # ------------------------------------------------------------------
        # Actions
        # ------------------------------------------------------------------

        controls = (
            ("Move north", "move_up"),
            ("Move south", "move_down"),
            ("Move east", "move_right"),
            ("Move west", "move_left"),
            ("Rotate active tile", "rotate_active_tile"),
            ("Place active tile", "place_active_tile"),
            ("Zombie door up", "zombie_door_up"),
            ("Zombie door down", "zombie_door_down"),
            ("Zombie door left", "zombie_door_left"),
            ("Zombie door right", "zombie_door_right"),
            ("Attack", "attack"),
            ("Attack with chainsaw", "attack_with_chainsaw"),
            ("Attack with candle fuel", "attack_with_candle_fuel"),
            ("Flee up", "flee_up"),
            ("Flee down", "flee_down"),
            ("Flee left", "flee_left"),
            ("Flee right", "flee_right"),
            ("Flee up with oil", "flee_up_with_oil"),
            ("Flee down with oil", "flee_down_with_oil"),
            ("Flee left with oil", "flee_left_with_oil"),
            ("Flee right with oil", "flee_right_with_oil"),
            ("End turn", "end_turn"),
            ("Cower and end turn", "cower_and_end_turn"),
            ("Search for item", "search_for_item"),
            ("Don't search for item", "dont_search_for_item"),
            ("Take found item", "take_found_item"),
            ("Don't take found item", "dont_take_found_item"),
            ("Discard item 1", "discard_item_1"),
            ("Discard item 2", "discard_item_2"),
            ("Drink soda", "use_soda"),
            ("Refuel chainsaw", "use_gasoline"),
        )

        self._action_buttons: list[ttk.Button] = []

        for index, (label, method_name) in enumerate(controls):
            button_row = index // 2
            button_column = index % 2

            button = ttk.Button(
                frame,
                text=label,
                command=lambda method=method_name: self._call_controller(method),
            )
            button.grid(
                row=button_row,
                column=button_column,
                sticky="ew",
                padx=4,
                pady=2,
            )
            self._action_buttons.append(button)

        action_rows = (len(controls) + 1) // 2

        # ------------------------------------------------------------------
        # Status
        # ------------------------------------------------------------------

        status_row = action_rows

        ttk.Label(
            frame,
            text="Status",
        ).grid(
            row=status_row,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(16, 0),
        )

        self.status = tk.StringVar(value="Choose an action.")

        ttk.Label(
            frame,
            textvariable=self.status,
            wraplength=560,
        ).grid(
            row=status_row + 1,
            column=0,
            columnspan=2,
            sticky="w",
            pady=(2, 8),
        )

        # ------------------------------------------------------------------
        # State / Exit
        # ------------------------------------------------------------------

        button_row = status_row + 2

        ttk.Button(
            frame,
            text="Reset",
            command=lambda: self._call_controller("reset"),
        ).grid(
            row=button_row,
            column=0,
            sticky="ew",
            padx=4,
            pady=2,
        )

        ttk.Button(
            frame,
            text="Exit",
            command=root.destroy,
        ).grid(
            row=button_row,
            column=1,
            sticky="ew",
            padx=4,
            pady=2,
        )

        self._action_buttons[0].focus_set()

    def _call_controller(self, method_name: str) -> None:
        """Call a controller method and display its result."""
        method = getattr(self._controller, method_name)
        win_loss = self._controller.check_win_loss()
        if win_loss is None:
            self.status.set(method() + f"\n{self._controller.get_status()}")
        else:
            self.status.set(win_loss)