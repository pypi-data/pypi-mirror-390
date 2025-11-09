from __future__ import annotations
from typing import (
    Any,
    TypeVar,
    cast,
)

from instaui.common.binding_track_mixin import BindingTrackerHelper, BindingTrackerMixin
from instaui.common.jsonable import Jsonable
from instaui.common.var_track_mixin import VarTrackerHelper, VarTrackerMixin
from instaui.common.const_data_mixin import ConstDataMixin
from instaui.runtime import try_new_scope_on_ui_state
from instaui.runtime.scope import Scope
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.path_var import PathVar

from .mixin_types.py_binding import CanInputMixin, CanOutputMixin
from .mixin_types.element_binding import ElementBindingMixin
from .mixin_types.str_format_binding import StrFormatBindingMixin


_T = TypeVar("_T")


class ConstData(
    Jsonable,
    PathVar,
    CanInputMixin,
    CanOutputMixin,
    StrFormatBindingMixin,
    BindingTrackerMixin,
    VarTrackerMixin,
    ElementBindingMixin,
    ConstDataMixin,
):
    def __init__(self, value: Any = None) -> None:
        self.value = value  # type: ignore

        self._define_scope = try_new_scope_on_ui_state()

        self.__var_tracker = VarTrackerHelper(
            var_id_gen_fn=lambda: self._define_scope.register_data(self)
        )
        self.__binding_tracker = BindingTrackerHelper(define_scope=self._define_scope)

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["id"] = self.__var_tracker.var_id

        return data

    def _to_event_output_type(self) -> OutputSetType:
        raise TypeError("ConstData cannot be used as an output")

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Data

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )

    def get_value(self) -> Any:
        return self.value


TConstData = ConstData


def const_data(value: _T) -> _T:
    return cast(_T, ConstData(value))
