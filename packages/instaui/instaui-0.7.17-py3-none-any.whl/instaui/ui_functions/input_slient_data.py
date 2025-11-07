import typing
from instaui.common.binding_track_mixin import (
    BindingTrackerMixin,
    try_mark_binding,
    is_binding_tracker,
)
from instaui.common.var_track_mixin import VarTrackerMixin, mark_as_used
from instaui.runtime.scope import Scope
from instaui.vars._types import InputBindingType
from instaui.vars.mixin_types.py_binding import CanInputMixin


class InputSilentData(CanInputMixin, BindingTrackerMixin, VarTrackerMixin):
    def __init__(self, value: typing.Union[BindingTrackerMixin, typing.Any]) -> None:
        """
        Wraps a value to mark it as "silent" for reactive tracking,
        so that changes to this value do not trigger dependent watchers
        or computed functions.

        Args:
            value (Union[BindingTrackerMixin, Any]): The value to wrap.
                Can be any data type or a reactive binding,
                which will be excluded from triggering reactive updates.


        Example:
        .. code-block:: python
            from instaui import ui, html

            a = ui.state("a")
            b = ui.state("b")
            result = ui.state("result")

            # Use silent data for 'b' so changes to 'b' don't trigger recomputation
            @ui.watch(inputs=[a, ui.slient(b)], outputs=[result])
            def only_a_changed(a: str, b: str):
                return f"{a}+{b}"

            # Only changes to 'a' will update the result
            html.input(a).classes("a")
            html.input(b).classes("b")
            html.paragraph(result)
        """

        self.value = value

    def is_const_value(self) -> bool:
        return not is_binding_tracker(self.value)

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _mark_binding(self, scope: Scope) -> dict:
        return try_mark_binding(self.value, scope=scope)

    def _mark_as_used(self):
        mark_as_used(self.value)
