from __future__ import annotations
import inspect
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generic,
    Optional,
    Sequence,
    TypeVar,
    cast,
)
from typing_extensions import ParamSpec
from collections.abc import Hashable

from instaui.common.jsonable import Jsonable
from instaui.runtime import get_app_slot, try_new_scope_on_ui_state
from instaui.handlers import watch_handler
from instaui.runtime.scope import Scope
from instaui.vars._types import InputBindingType
from instaui.vars.path_var import PathVar
from instaui.vars.mixin_types.py_binding import (
    CanInputMixin,
    CanOutputMixin,
    outputs_to_config,
)
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.common_type import TObservableInput
from instaui.common.var_track_mixin import VarTrackerMixin, VarTrackerHelper
from instaui.common.binding_track_mixin import (
    BindingTrackerMixin,
    BindingTrackerHelper,
    try_mark_binding,
)
from instaui._helper import observable_helper
from instaui import pre_setup as _pre_setup

if TYPE_CHECKING:
    from instaui.runtime.scope import Scope


_SYNC_TYPE = "sync"
_ASYNC_TYPE = "async"

P = ParamSpec("P")
R = TypeVar("R")


class WebComputed(
    Jsonable,
    PathVar,
    CanInputMixin,
    ObservableMixin,
    StrFormatBindingMixin,
    VarTrackerMixin,
    BindingTrackerMixin,
    ElementBindingMixin,
    Generic[P, R],
):
    def __init__(
        self,
        func: Callable[P, R],
        inputs: Optional[Sequence[TObservableInput]] = None,
        extend_outputs: Optional[Sequence[CanOutputMixin]] = None,
        init_value: Optional[R] = None,
        evaluating: Optional[CanOutputMixin] = None,
        deep_compare_on_input: bool = False,
        pre_setup: Optional[list] = None,
        debug_info: Optional[dict] = None,
        extra_key: Optional[Sequence[Hashable]] = None,
    ) -> None:
        self._define_scope = try_new_scope_on_ui_state()
        self._org_inputs = inputs or []

        self._inputs, self._is_slient_inputs, self._is_data = (
            observable_helper.analyze_observable_inputs(list(inputs or []))
        )
        self._outputs = extend_outputs or []
        self._fn = func
        self._init_value = init_value
        self._deep_compare_on_input = deep_compare_on_input
        self._pre_setup = _pre_setup.convert_list2list(pre_setup)
        if evaluating is not None:
            self._pre_setup.append([evaluating, True, False])

        if debug_info is not None:
            self.debug = debug_info

        def upstreams_binding_callback(scope: Scope):
            self._inputs = [
                try_mark_binding(input, scope=scope) for input in self._inputs
            ]
            self._outputs = outputs_to_config(self._outputs, scope=scope)
            self._pre_setup = _pre_setup.convert_config(self._pre_setup)

        self.__binding_tracker = BindingTrackerHelper(
            define_scope=self._define_scope,
            upstreams_callback=upstreams_binding_callback,
        )

        self.__var_tracker = VarTrackerHelper(
            var_id_gen_fn=lambda: self._define_scope.register_web_computed(self),
            upstreams_getter=lambda: [
                inputs,
                self._outputs,
                _pre_setup.extract_bindings(self._pre_setup),
            ],
        )

        self._extra_key = extra_key

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        return self._fn(*args, **kwargs)

    def _to_json_dict(self):
        data = super()._to_json_dict()

        app = get_app_slot()

        hkey = watch_handler.create_handler_key(
            page_path=app.page_path, handler=self._fn, extra_key=self._extra_key
        )

        watch_handler.register_handler(
            hkey,
            self._fn,
            len(self._outputs) + 1,
        )

        data["id"] = self.__var_tracker.var_id

        if self._inputs:
            data["inputs"] = self._inputs

        if self._outputs:
            data["outputs"] = self._outputs

        if sum(self._is_slient_inputs) > 0:
            data["slient"] = self._is_slient_inputs

        if sum(self._is_data) > 0:
            data["data"] = self._is_data

        data["fType"] = (
            _ASYNC_TYPE if inspect.iscoroutinefunction(self._fn) else _SYNC_TYPE
        )
        data["key"] = hkey
        if self._init_value is not None:
            data["init"] = self._init_value

        if self._deep_compare_on_input is not False:
            data["deepEqOnInput"] = 1
        if self._pre_setup:
            data["preSetup"] = self._pre_setup

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )


def web_computed(
    *,
    inputs: Optional[Sequence] = None,
    extend_outputs: Optional[Sequence] = None,
    init_value: Optional[Any] = None,
    evaluating: Optional[Any] = None,
    deep_compare_on_input: bool = False,
    pre_setup: Optional[list] = None,
    extra_key: Optional[Sequence[Hashable]] = None,
    debug_info: Optional[dict] = None,
):
    """
    Creates a computed property decorator for reactive programming with dependency tracking.

    This decorator factory wraps functions to create reactive computed properties that:
    - Automatically re-evaluate when dependencies (inputs) change
    - Cache results for performance optimization
    - Support both synchronous and asynchronous computation patterns

    Args:
        inputs (Optional[Sequence], optional): Collection of reactive sources that trigger recomputation
                                   when changed. These can be state objects or other computed properties.
        extend_outputs (Optional[Sequence], optional):  Additional outputs to notify when this computed value updates.
        init_value (Optional[Any], optional): Initial value to return before first successful evaluation.
        evaluating (Optional[Any], optional): Temporary value returned during asynchronous computation.
        pre_setup (typing.Optional[list], optional): A list of pre-setup actions to be executed before the event executes.

    # Example:
    .. code-block:: python
        from instaui import ui,html

        a = ui.state(0)

        @ui.computed(inputs=[a])
        def plus_one(a):
            return a + 1

        html.number(a)
        ui.text(plus_one)
    """

    if get_app_slot().mode == "zero":
        raise Exception(
            "Cannot use computed decorator in zero mode. You should use `ui.js_computed` instead."
        )

    def wrapper(func: Callable[P, R]):
        return cast(
            R,
            WebComputed(
                func,
                inputs=inputs,
                extend_outputs=extend_outputs,
                init_value=init_value,
                evaluating=evaluating,
                deep_compare_on_input=deep_compare_on_input,
                pre_setup=pre_setup,
                debug_info=debug_info,
                extra_key=extra_key,
            ),
        )

    return wrapper


TComputed = WebComputed
