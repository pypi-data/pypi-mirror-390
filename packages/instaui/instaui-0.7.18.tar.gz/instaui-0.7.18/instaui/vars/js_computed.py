from __future__ import annotations
import typing
from instaui.common.jsonable import Jsonable
from instaui.runtime import try_new_scope_on_ui_state
from instaui.vars._types import InputBindingType
from instaui.vars.path_var import PathVar
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.py_binding import CanInputMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.common_type import TObservableInput
from instaui._helper import observable_helper
from instaui.common.var_track_mixin import VarTrackerMixin, VarTrackerHelper
from instaui.common.binding_track_mixin import (
    BindingTrackerMixin,
    BindingTrackerHelper,
    try_mark_binding,
)

if typing.TYPE_CHECKING:
    from instaui.runtime.scope import Scope


_R_TYPE = typing.TypeVar("_R_TYPE")


class JsComputed(
    Jsonable,
    PathVar,
    ObservableMixin,
    CanInputMixin,
    StrFormatBindingMixin,
    VarTrackerMixin,
    BindingTrackerMixin,
    ElementBindingMixin,
):
    def __init__(
        self,
        *,
        inputs: typing.Optional[typing.Sequence[TObservableInput]] = None,
        code: str,
        async_init_value: typing.Optional[typing.Any] = None,
        deep_compare_on_input: bool = False,
        _tool_name: typing.Optional[str] = None,
    ) -> None:
        self.code = code
        self._tool_name = _tool_name
        self._org_inputs = inputs or []

        self._define_scope = try_new_scope_on_ui_state()

        self._inputs, self._is_slient_inputs, self._is_data = (
            observable_helper.analyze_observable_inputs(list(inputs or []))
        )

        self._async_init_value = async_init_value
        self._deep_compare_on_input = deep_compare_on_input

        def upstreams_binding_callback(scope: Scope):
            self._inputs = [
                try_mark_binding(input, scope=scope) for input in self._inputs
            ]

        self.__binding_tracker = BindingTrackerHelper(
            define_scope=self._define_scope,
            upstreams_callback=upstreams_binding_callback,
        )

        self.__var_tracker = VarTrackerHelper(
            var_id_gen_fn=lambda: self._define_scope.register_js_computed(self),
            upstreams_getter=lambda: [inputs],
        )

    def _to_json_dict(self):
        data = super()._to_json_dict()

        data["id"] = self.__var_tracker.var_id

        if self._inputs:
            data["inputs"] = self._inputs

        if sum(self._is_slient_inputs) > 0:
            data["slient"] = self._is_slient_inputs

        if sum(self._is_data) > 0:
            data["data"] = self._is_data

        if self._async_init_value is not None:
            data["asyncInit"] = self._async_init_value

        if self._deep_compare_on_input is not False:
            data["deepEqOnInput"] = 1
        if self._tool_name is not None:
            data["tool"] = self._tool_name

        return data

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )


TJsComputed = JsComputed


@typing.overload
def js_computed(
    *,
    inputs: typing.Optional[typing.Sequence[TObservableInput]] = None,
    code: str,
    async_init_value: typing.Optional[typing.Any] = None,
    deep_compare_on_input: bool = False,
) -> typing.Any: ...


@typing.overload
def js_computed(
    *,
    inputs: typing.Optional[typing.Sequence[TObservableInput]] = None,
    code: str,
    async_init_value: typing.Optional[typing.Any] = None,
    deep_compare_on_input: bool = False,
    r_type: typing.Optional[typing.Type[_R_TYPE]] = None,
) -> _R_TYPE: ...


def js_computed(
    *,
    inputs: typing.Optional[typing.Sequence[TObservableInput]] = None,
    code: str,
    async_init_value: typing.Optional[typing.Any] = None,
    deep_compare_on_input: bool = False,
    r_type: typing.Optional[typing.Type[_R_TYPE]] = None,
) -> typing.Union[JsComputed, _R_TYPE]:
    """
    A client-side computed property that evaluates JavaScript code to derive reactive values.

    Args:
        inputs (typing.Optional[typing.Sequence[TObservableInput]], optional): Reactive data sources to monitor.
                                                  Changes to these values trigger re-computation.
        code (str): JavaScript code to execute for computing the value.
        async_init_value (typing.Optional[typing.Any], optional): Initial value to use before first successful async evaluation.

    # Example:
    .. code-block:: python
        a = ui.state(0)

        plus_one = ui.js_computed(inputs=[a], code="a=> a+1")

        html.number(a)
        ui.text(plus_one)
    """

    jc = JsComputed(
        inputs=inputs,
        code=code,
        async_init_value=async_init_value,
        deep_compare_on_input=deep_compare_on_input,
    )

    if r_type is None:
        return jc

    return typing.cast(_R_TYPE, jc)
