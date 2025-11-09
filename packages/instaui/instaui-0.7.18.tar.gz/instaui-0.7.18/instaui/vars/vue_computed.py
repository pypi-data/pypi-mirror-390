from __future__ import annotations
from typing import TYPE_CHECKING, Mapping, Optional

from instaui.common.jsonable import Jsonable

from instaui.runtime import try_new_scope_on_ui_state
from instaui.runtime.scope import Scope
from instaui.vars._types import InputBindingType
from instaui.vars.path_var import PathVar
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.py_binding import CanInputMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.common.var_track_mixin import VarTrackerMixin, VarTrackerHelper
from instaui.common.binding_track_mixin import (
    BindingTrackerMixin,
    BindingTrackerHelper,
    mark_binding,
    is_binding_tracker,
)
from instaui.vars.types import TMaybeRef

if TYPE_CHECKING:
    from instaui.runtime.scope import Scope


class VueComputed(
    Jsonable,
    PathVar,
    CanInputMixin,
    ObservableMixin,
    StrFormatBindingMixin,
    VarTrackerMixin,
    BindingTrackerMixin,
    ElementBindingMixin,
):
    def __init__(
        self,
        fn_code: str,
        bindings: Optional[Mapping[str, TMaybeRef]] = None,
    ) -> None:
        self._define_scope = try_new_scope_on_ui_state()
        self.code = fn_code
        self._bindings = bindings
        self._bind_data = None
        self._bind_const: Optional[list[int]] = None

        def upstreams_binding_callback(scope: Scope):
            if not self._bindings:
                return

            binds = {}
            bind_consts = []

            for k, v in self._bindings.items():
                is_binding = is_binding_tracker(v)
                binds[k] = mark_binding(v, scope=scope) if is_binding else v

                bind_consts.append(int(not is_binding))

            self._bind_data = binds
            if sum(bind_consts) > 0:
                self._bind_const = bind_consts

        self.__binding_tracker = BindingTrackerHelper(
            define_scope=self._define_scope,
            upstreams_callback=upstreams_binding_callback,
        )

        self.__usage_tracker = VarTrackerHelper(
            var_id_gen_fn=lambda: self._define_scope.register_vue_computed(self),
            upstreams_getter=lambda: [bindings],
        )

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["id"] = self.__usage_tracker.var_id

        if self._bind_data:
            data["bind"] = self._bind_data

        if self._bind_const:
            data["const"] = self._bind_const

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _mark_as_used(self):
        self.__usage_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__usage_tracker.var_id, scope=scope
        )


TVueComputed = VueComputed
