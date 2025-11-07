from __future__ import annotations
from typing import TYPE_CHECKING
from instaui.common.jsonable import Jsonable
from instaui.vars._types import InputBindingType
from instaui.vars.mixin_types.py_binding import CanInputMixin
from instaui.runtime import get_current_scope
from instaui.common.var_track_mixin import VarTrackerMixin, VarTrackerHelper
from instaui.common.binding_track_mixin import BindingTrackerMixin, BindingTrackerHelper

if TYPE_CHECKING:
    from instaui.runtime.scope import Scope


class JsFn(
    Jsonable,
    CanInputMixin,
    BindingTrackerMixin,
    VarTrackerMixin,
):
    """
    Creates a JavaScript function object from a raw code string.
    Valid targets include: `js_computed`, `js_watch`, and similar JS-bound methods.

    Args:
        code (str): Valid JavaScript function definition string.

    Example:
    .. code-block:: python
        a = ui.state(1)
        add = ui.js_fn(code="(a,b)=> a+b ")
        result = ui.js_computed(inputs=[add, a], code="(add,a)=>  add(a,10) ")

        html.number(a)
        ui.text(result)
    """

    def __init__(self, code: str, *, execute_immediately=False, global_scope=False):
        self.code = code
        self._execute_immediately = execute_immediately
        self._define_scope = get_current_scope()

        self.__var_tracker = VarTrackerHelper(
            var_id_gen_fn=lambda: self._define_scope.register_js_fn(self)
        )
        self.__binding_tracker = BindingTrackerHelper(define_scope=self._define_scope)

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["id"] = self.__var_tracker.var_id

        if self._execute_immediately is True:
            data["immediately"] = 1

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.JsFn

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )
