from __future__ import annotations
from typing import Generic, TypeVar, cast, TYPE_CHECKING

from instaui.common.binding_track_mixin import BindingTrackerHelper, BindingTrackerMixin
from instaui.common.jsonable import Jsonable
from instaui.common.var_track_mixin import (
    VarTrackerHelper,
    VarTrackerMixin,
)
from instaui.runtime import get_current_scope
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.py_binding import CanInputMixin, CanOutputMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.path_var import PathVar

if TYPE_CHECKING:
    from instaui.components.vfor import VFor
    from instaui.runtime.scope import Scope


_T = TypeVar("_T")


class VForItem(
    PathVar,
    CanInputMixin,
    ObservableMixin,
    CanOutputMixin,
    ElementBindingMixin,
    StrFormatBindingMixin,
    BindingTrackerMixin,
    VarTrackerMixin,
    Jsonable,
    Generic[_T],
):
    SCOPE_TYPE = "fv"

    def __init__(self, vfor: VFor):
        super().__init__()
        self._define_scope = get_current_scope()

        def var_id_gen_fn():
            var_id = self._define_scope.generate_vars_id()
            vfor._mark_binding_used(type="item", var_id=var_id)
            return var_id

        self.__var_tracker = VarTrackerHelper(var_id_gen_fn=var_id_gen_fn)
        self.__binding_tracker = BindingTrackerHelper(define_scope=self._define_scope)

    def __getattr__(self, name: str):
        return self[name]

    @property
    def value(self) -> _T:
        return cast(_T, self)

    def __to_binding_config(self):
        return {}

    def _to_json_dict(self):
        data: dict = {
            "id": self.__var_tracker.var_id,
        }

        return data

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.Ref

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )


class VForIndex(
    CanInputMixin,
    ElementBindingMixin,
    StrFormatBindingMixin,
    ObservableMixin,
    BindingTrackerMixin,
    VarTrackerMixin,
    Jsonable,
):
    SCOPE_TYPE = "fi"

    def __init__(self, vfor: VFor):
        super().__init__()

        self._define_scope = get_current_scope()

        def var_id_gen_fn():
            var_id = self._define_scope.generate_vars_id()
            vfor._mark_binding_used(type="index", var_id=var_id)
            return var_id

        self.__var_tracker = VarTrackerHelper(var_id_gen_fn=var_id_gen_fn)
        self.__binding_tracker = BindingTrackerHelper(define_scope=self._define_scope)

        self._mark_as_used()

    def __to_binding_config(self):
        return {}

    def _to_json_dict(self):
        return {
            "id": self.__var_tracker.var_id,
        }

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )


class VForItemKey(
    CanInputMixin,
    ElementBindingMixin,
    StrFormatBindingMixin,
    ObservableMixin,
    BindingTrackerMixin,
    VarTrackerMixin,
    Jsonable,
):
    SCOPE_TYPE = "fk"

    def __init__(self, vfor: VFor):
        super().__init__()
        self._define_scope = get_current_scope()

        def var_id_gen_fn():
            var_id = self._define_scope.generate_vars_id()
            vfor._mark_binding_used(type="key", var_id=var_id)
            return var_id

        self.__var_tracker = VarTrackerHelper(var_id_gen_fn=var_id_gen_fn)
        self.__binding_tracker = BindingTrackerHelper(define_scope=self._define_scope)
        self._mark_as_used()

    def __to_binding_config(self):
        return {}

    def _to_json_dict(self):
        return {
            "id": self.__var_tracker.var_id,
        }

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )


TVForItem = VForItem
TVForIndex = VForIndex
