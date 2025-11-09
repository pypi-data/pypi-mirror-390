from __future__ import annotations
from typing import Any, Optional, TYPE_CHECKING
from instaui.common.const_data_mixin import ConstDataMixin
from instaui.common.jsonable import Jsonable
from instaui.runtime import try_new_scope_on_ui_state
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.path_var import PathVar
from instaui.missing import MISSING
from instaui.common.var_track_mixin import VarTrackerMixin, VarTrackerHelper
from instaui.common.binding_track_mixin import (
    BindingTrackerMixin,
    BindingTrackerHelper,
    try_mark_binding,
)

from .mixin_types.py_binding import CanInputMixin, CanOutputMixin
from .mixin_types.observable import ObservableMixin
from .mixin_types.element_binding import ElementBindingMixin
from .mixin_types.str_format_binding import StrFormatBindingMixin

if TYPE_CHECKING:
    from instaui.runtime.scope import Scope


class RefBase(
    Jsonable,
    PathVar,
    ObservableMixin,
    CanInputMixin,
    CanOutputMixin,
    StrFormatBindingMixin,
    ElementBindingMixin,
    BindingTrackerMixin,
    VarTrackerMixin,
):
    def __init__(
        self,
        *,
        ref_type: Optional[str] = None,
        value: Optional[Any] = MISSING,
        deep_compare: bool = False,
        args: Optional[dict] = None,
    ) -> None:
        self._define_scope = try_new_scope_on_ui_state()

        self._deep_compare = deep_compare
        self._value = value
        self._is_const_data = False
        self._args = args
        self._ref_type = ref_type

        def upstreams_binding_callback(scope: Scope):
            if isinstance(self._value, ConstDataMixin):
                self._value = try_mark_binding(self._value, scope=scope)
                self._is_const_data = True

        self.__binding_tracker = BindingTrackerHelper(
            define_scope=self._define_scope,
            upstreams_callback=upstreams_binding_callback,
        )

        self.__var_tracker = VarTrackerHelper(
            var_id_gen_fn=lambda: self._define_scope.register_ref(self),
            upstreams_getter=lambda: [self._value]
            if isinstance(self._value, ConstDataMixin)
            else [],
        )

    def __deepcopy__(self, memo):
        memo[id(self)] = self
        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["id"] = self.__var_tracker.var_id

        if self._deep_compare is True:
            data["deepCompare"] = True

        if self._args:
            data["args"] = {k: v for k, v in self._args.items() if v is not None}

        if self._ref_type:
            data["type"] = self._ref_type

        if self._value is not MISSING:
            if self._is_const_data:
                data["constData"] = 1
            data["value"] = self._value

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.Ref

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )
