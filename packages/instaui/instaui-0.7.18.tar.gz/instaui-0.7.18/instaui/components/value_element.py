from __future__ import annotations
from typing import (
    Generic,
    Optional,
    Union,
    TypeVar,
)
from instaui.common.binding_track_mixin import try_mark_binding
from instaui.common.var_track_mixin import mark_as_used
from instaui.components.element import Element
from instaui import consts

from instaui.vars.types import TMaybeRef
from instaui.vars.web_computed import WebComputed
from instaui.ui_functions.ui_types import is_bindable


_T = TypeVar("_T")


class ValueElement(Element, Generic[_T]):
    def __init__(
        self,
        tag: Optional[str] = None,
        value: Union[_T, TMaybeRef[_T], None] = None,
        is_html_component: bool = False,
        value_name: str = "value",
    ):
        super().__init__(tag)
        self.__is_html_component = is_html_component

        if value is not None:
            if is_bindable(value):
                if isinstance(value, WebComputed):
                    self.props({value_name: value})
                else:
                    self.vmodel(value, prop_name=value_name)
            else:
                self.props({value_name: value})

    def vmodel(
        self,
        value,
        modifiers: Union[consts.TModifier, list[consts.TModifier], None] = None,
        *,
        prop_name: str = "value",
    ):
        mark_as_used(value)
        return super().vmodel(
            try_mark_binding(value),
            modifiers,
            prop_name=prop_name,
            is_html_component=self.__is_html_component,
        )
