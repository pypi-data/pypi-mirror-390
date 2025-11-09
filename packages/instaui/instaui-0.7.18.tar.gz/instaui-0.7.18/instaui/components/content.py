from __future__ import annotations
from typing import Any
from instaui.common.binding_track_mixin import is_binding_tracker, try_mark_binding
from instaui.common.var_track_mixin import mark_as_used
from instaui.vars.types import TMaybeRef
from instaui.components.logic_component import LogicComponent


class Content(LogicComponent):
    def __init__(self, content: TMaybeRef[Any]):
        """Content to be displayed on the page, typically used for pure text content within slots.

        Args:
            content (TMaybeRef[Any]): The textual content to display.

        Examples:
        .. code-block:: python
            with html.div():
                ui.content("Hello, world!")
        """
        super().__init__("content")
        mark_as_used(content)
        self._content = try_mark_binding(content)
        self._is_binding = is_binding_tracker(content)

    def _to_json_dict(self) -> dict:
        data = super()._to_json_dict()

        if self._is_binding:
            data["r"] = 1

        if self._content:
            data["value"] = self._content

        return data
