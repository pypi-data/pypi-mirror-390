from __future__ import annotations
from instaui.common.binding_track_mixin import try_mark_binding
from instaui.common.component_mixin import ComponentMixin
from instaui.common.var_track_mixin import mark_as_used
from instaui.vars.types import TMaybeRef
from instaui.components.logic_component import LogicContainer


class VIf(LogicContainer):
    def __init__(self, on: TMaybeRef[bool]):
        """
        A conditional container that renders its children only when the given condition is True.

        Args:
            on (TMaybeRef[bool]): A boolean or reactive reference that determines whether the container's
                                child elements should be displayed. If True, children are rendered;
                                if False, children are hidden.


        Example:
        .. code-block:: python
            from instaui import ui, html

            value = ui.state(False)

            html.button("toggle").on_click(
                ui.js_event(inputs=[value], outputs=[value], code="(v)=> !v")
            )

            with ui.vif(value):
                ui.text("show")
        """

        super().__init__("vif")
        mark_as_used(on)
        self._on = try_mark_binding(on)
        self._items: list[ComponentMixin] = []

    def _to_json_dict(self):
        data = super()._to_json_dict()

        data["on"] = self._on

        if self._items:
            data["items"] = self._items

        return data

    def add_item(self, item: ComponentMixin):
        self._items.append(item)
