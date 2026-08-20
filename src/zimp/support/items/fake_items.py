from zimp.domain.items.inventory import Effect


class FakeItemsGateway:
    """Controllable fake for boundary and contract testing.

    Records what the controller asked for, and can be told to fail, so a
    boundary test never depends on real inventory rules.
    """

    def __init__(self, effect: Effect | None = None, held: list[str] | None = None) -> None:
        self.effect = effect if effect is not None else Effect()
        self.held = list(held) if held is not None else []
        self.calls: list[tuple[str, str]] = []
        self.battles = 0
        self.failure: Exception | None = None

    def add(self, item_id: str) -> None:
        self._record("add", item_id)
        self.held.append(item_id)

    def discard(self, item_id: str) -> None:
        self._record("discard", item_id)
        self.held.remove(item_id)

    def use(self, item_id: str) -> Effect:
        self._record("use", item_id)
        return self.effect

    def held_items(self) -> list[str]:
        return list(self.held)

    def attack_bonus(self) -> int:
        return 0

    def record_battle(self) -> None:
        self.battles += 1

    def _record(self, action: str, item_id: str) -> None:
        self.calls.append((action, item_id))
        if self.failure is not None:
            raise self.failure
