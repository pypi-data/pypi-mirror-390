from __future__ import annotations
import typing
from instaui.common.jsonable import Jsonable
from instaui.runtime import get_app_slot
from instaui.vars.path_var import PathVar
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.common.var_track_mixin import VarTrackerMixin, VarTrackerHelper
from instaui.common.binding_track_mixin import BindingTrackerMixin, BindingTrackerHelper

if typing.TYPE_CHECKING:
    from instaui.runtime.scope import Scope


class RouteParamsVar(
    Jsonable,
    PathVar,
    ObservableMixin,
    StrFormatBindingMixin,
    ElementBindingMixin,
    BindingTrackerMixin,
    VarTrackerMixin,
):
    def __init__(
        self,
        prop: typing.Literal["params", "path", "fullPath"] = "params",
    ) -> None:
        super().__init__()
        self._prop = prop

        base_scope = get_app_slot().router_base_scope
        assert base_scope is not None, "Router base scope not found"
        self._define_scope = base_scope

        def var_id_gen_fn():
            var_id = self._define_scope.register_router_param_used()
            return var_id

        self.__var_tracker = VarTrackerHelper(var_id_gen_fn=var_id_gen_fn)
        self.__binding_tracker = BindingTrackerHelper(define_scope=self._define_scope)

    def _to_json_dict(self):
        raise NotImplementedError("RouteParamsVar is not json serializable")

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )
