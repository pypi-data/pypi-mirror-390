import typing
from instaui.event.event_modifier import TEventModifier
from instaui.vars.mixin_types.py_binding import (
    CanInputMixin,
    inputs_to_config,
    outputs_to_config,
)
from .event_mixin import EventMixin
from . import _utils


class JsEvent(EventMixin):
    def __init__(
        self,
        code: str,
        inputs: typing.Optional[typing.Sequence] = None,
        outputs: typing.Optional[typing.Sequence] = None,
        modifier: typing.Optional[typing.Sequence[TEventModifier]] = None,
    ):
        self._is_const_data = [
            int(not isinstance(input, CanInputMixin)) for input in inputs or []
        ]

        self._inputs = inputs or []
        self._outputs = outputs or []
        self._code = code
        self._modifier = modifier or []

    def _attach_to_element(
        self,
        *,
        extends: typing.Optional[typing.Sequence],
        modifier: typing.Optional[typing.Sequence[TEventModifier]],
    ) -> dict:
        real_inputs = [*self._inputs, *(extends or [])]
        real_modifier = [*self._modifier, *(modifier or [])]
        _utils.mark_as_used(real_inputs)
        _utils.mark_as_used(self._outputs)

        data = {}
        data["type"] = self.event_type()
        data["code"] = self._code

        if real_inputs:
            data["inputs"] = inputs_to_config(real_inputs)

        if self._outputs:
            data["sets"] = outputs_to_config(self._outputs)

        if sum(self._is_const_data) > 0:
            data["data"] = self._is_const_data

        if real_modifier:
            data["modifier"] = real_modifier

        return data

    def event_type(self):
        return "js"


def js_event(
    *,
    inputs: typing.Optional[typing.Sequence] = None,
    outputs: typing.Optional[typing.Sequence] = None,
    code: str,
):
    """
    Creates a client-side event handler decorator for binding JavaScript logic to UI component events.

    Args:
        inputs (typing.Optional[typing.Sequence], optional):Reactive sources (state variables, computed values)
                                   that should be passed to the event handler. These values
                                   will be available in the JavaScript context through the `args` array.
        outputs (typing.Optional[typing.Sequence], optional): Targets (state variables, UI elements) that should
                                    update when this handler executes. Used for coordinating
                                    interface updates after the event is processed.
        code (str): JavaScript code to execute when the event is triggered.

    # Example:
    .. code-block:: python
        from instaui import ui, html

        a = ui.state(0)

        plus_one = ui.js_event(inputs=[a], outputs=[a], code="a =>a + 1")

        html.button("click me").on_click(plus_one)
        html.paragraph(a)

    """
    return JsEvent(inputs=inputs, outputs=outputs, code=code)
