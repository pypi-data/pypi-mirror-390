from __future__ import annotations
from typing import Optional, TYPE_CHECKING
from instaui.runtime import get_app_slot
from instaui.vars._types import OutputSetType
from instaui.vars.mixin_types.py_binding import CanOutputMixin
from pydantic import BaseModel
from instaui.common.var_track_mixin import VarTrackerMixin, VarTrackerHelper
from instaui.common.binding_track_mixin import BindingTrackerMixin, BindingTrackerHelper

if TYPE_CHECKING:
    from instaui.runtime.scope import Scope


class RouterActionVar(BindingTrackerMixin, VarTrackerMixin, CanOutputMixin):
    def __init__(self):
        base_scope = get_app_slot().base_scope
        assert base_scope is not None, "Router base scope not found"
        self._define_scope = base_scope

        def var_id_gen_fn():
            var_id = self._define_scope.register_router_action_used()
            return var_id

        self.__var_tracker = VarTrackerHelper(var_id_gen_fn=var_id_gen_fn)
        self.__binding_tracker = BindingTrackerHelper(define_scope=self._define_scope)

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.RouterAction

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )


class RouterMethod(BaseModel):
    fn: str
    args: Optional[list]
