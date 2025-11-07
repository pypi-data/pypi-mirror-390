import typing
from instaui.event.event_modifier import TEventModifier
from instaui.vars.mixin_types.py_binding import CanInputMixin
from instaui.vars._types import InputBindingType
from instaui.common.var_track_mixin import mark_as_used
from instaui.common.binding_track_mixin import try_mark_binding
from .event_mixin import EventMixin


class VueEvent(EventMixin):
    """
    Create an event object that can be bound to a UI component's event listener.

    This function generates a callable event handler with optional contextual bindings.
    The event logic is defined via a code string, which can reference bound variables.

    Args:
        code (str): A string containing the executable logic for the event handler.
                    Typically contains a function body or expression that utilizes bound variables.
        bindings (typing.Optional[dict[str, typing.Any]], optional): A dictionary mapping variable names to values that should be available in the
            event handler's context. If None, no additional bindings are created.. Defaults to None.

    Example:
    .. code-block:: python
        a = ui.state(1)

        event = ui.vue_event(bindings={"a": a}, code=r'''()=> { a.value +=1}''')

        html.span(a)
        html.button("plus").on("click", event)
    """

    def __init__(
        self,
        *,
        code: str,
        bindings: typing.Optional[dict[str, typing.Any]] = None,
    ):
        self._code = code
        self._bindings = bindings

    def event_type(self):
        return "vue"

    def _attach_to_element(
        self,
        *,
        extends: typing.Optional[typing.Sequence],
        modifier: typing.Optional[typing.Sequence[TEventModifier]],
    ) -> dict:
        data = {}
        data["code"] = self._code
        data["type"] = self.event_type()

        mark_as_used(self._bindings)

        if self._bindings:
            data["inputs"] = {
                name: {
                    "value": try_mark_binding(v),
                    "type": v._to_event_input_type().value
                    if isinstance(v, CanInputMixin)
                    else InputBindingType.Data,
                }
                for name, v in self._bindings.items()
            }
        return data


vue_event = VueEvent
