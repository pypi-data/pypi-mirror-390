from __future__ import annotations
from typing import Union
from instaui.common.binding_track_mixin import BindingTrackerMixin
from instaui.components.element import Element
from instaui.components.value_element import ValueElement
from instaui import consts
from instaui.vars.types import TMaybeRef
from ._mixins import InputEventMixin

_T_value = Union[int, float]


class Range(InputEventMixin, ValueElement[_T_value]):
    def __init__(
        self,
        value: Union[_T_value, TMaybeRef[_T_value], None] = None,
        *,
        min: Union[_T_value, TMaybeRef[_T_value], None] = None,
        max: Union[_T_value, TMaybeRef[_T_value], None] = None,
        step: Union[_T_value, TMaybeRef[_T_value], None] = None,
    ):
        super().__init__("input", value, is_html_component=True)
        self.props({"type": "range"})

        if min is not None:
            self.props({"min": min})
        if max is not None:
            self.props({"max": max})
        if step is not None:
            self.props({"step": step})

    def vmodel(
        self,
        value: BindingTrackerMixin,
        modifiers: Union[consts.TModifier, list[consts.TModifier], None] = None,
        *,
        prop_name: str = "value",
    ):
        modifiers = modifiers or []
        if isinstance(modifiers, str):
            modifiers = [modifiers]

        modifiers_with_number = list(set([*modifiers, "number"]))

        return super().vmodel(value, modifiers_with_number, prop_name=prop_name)  # type: ignore

    def _input_event_mixin_element(self) -> Element:
        return self
