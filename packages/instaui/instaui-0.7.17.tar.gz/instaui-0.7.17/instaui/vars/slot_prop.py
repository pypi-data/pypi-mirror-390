from __future__ import annotations
from typing import TYPE_CHECKING
from instaui.common.jsonable import Jsonable
from instaui.runtime.scope import Scope
from instaui.vars._types import InputBindingType
from instaui.vars.path_var import PathVar
from instaui.common.var_track_mixin import VarTrackerMixin, VarTrackerHelper
from instaui.common.binding_track_mixin import BindingTrackerMixin, BindingTrackerHelper


from .mixin_types.py_binding import CanInputMixin
from .mixin_types.element_binding import ElementBindingMixin

if TYPE_CHECKING:
    from instaui.components.slot import Slot


class SlotProp(
    Jsonable,
    PathVar,
    ElementBindingMixin,
    CanInputMixin,
    BindingTrackerMixin,
    VarTrackerMixin,
):
    def __init__(self, name: str, *, slot: Slot) -> None:
        super().__init__()
        self._define_scope = slot._define_scope
        self._name = name

        def var_id_gen_fn():
            var_id = self._define_scope.generate_vars_id()
            slot._mark_binding_used(var_id=var_id)
            return var_id

        self.__var_tracker = VarTrackerHelper(var_id_gen_fn=var_id_gen_fn)
        self.__binding_tracker = BindingTrackerHelper(define_scope=self._define_scope)

    def _to_json_dict(self):
        data: dict = {
            "id": self.__var_tracker.var_id,
        }

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )
