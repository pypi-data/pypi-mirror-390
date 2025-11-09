from __future__ import annotations
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from .li import Li
from instaui.components.vfor import VFor


class Ul(Element):
    def __init__(self):
        super().__init__("ul")

    @classmethod
    def from_list(cls, data: TMaybeRef[list]) -> Ul:
        with Ul() as ul:
            with VFor(data) as items:
                Li(items)

        return ul
