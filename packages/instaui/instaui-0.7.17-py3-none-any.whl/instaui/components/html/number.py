from __future__ import annotations
from typing import Union
from instaui.components.element import Element
from instaui.components.value_element import ValueElement
from ._mixins import InputEventMixin


_T_value = Union[int, float, None]


class Number(InputEventMixin, ValueElement[_T_value]):
    def __init__(
        self,
        value: _T_value = None,
        *,
        model_value: _T_value = None,
        min: _T_value = None,
        max: _T_value = None,
    ):
        super().__init__("input", value, is_html_component=True)
        self.props({"type": "number"})

        if min is not None:
            self.props({"min": min})
        if max is not None:
            self.props({"max": max})
        if model_value is not None:
            self.props({"value": model_value})

    def _input_event_mixin_element(self) -> Element:
        return self
