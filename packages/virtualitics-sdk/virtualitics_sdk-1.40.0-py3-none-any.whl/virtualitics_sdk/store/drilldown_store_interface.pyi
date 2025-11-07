from _typeshed import Incomplete
from virtualitics_sdk import Element as Element, Row as Row
from virtualitics_sdk.page.card import Card as Card

class DrilldownStoreInterface:
    flow_id: Incomplete
    user_id: Incomplete
    step_name: Incomplete
    card: Incomplete
    def __init__(self, flow_id: str, user_id: str, step_name: str, card: Card) -> None: ...
    def add_element(self, *, elements: Row | list[Element] | Element, ratio: list[int | float] | None = None, index: int | None = None): ...
