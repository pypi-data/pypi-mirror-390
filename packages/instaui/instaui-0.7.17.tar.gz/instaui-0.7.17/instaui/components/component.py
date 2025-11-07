from __future__ import annotations

from typing import Optional
from instaui.common.jsonable import Jsonable
from instaui.common.component_mixin import ComponentMixin
from instaui.runtime import get_app_slot, check_default_app_slot_or_error

from instaui.common.var_track_mixin import mark_as_used
from instaui.common.binding_track_mixin import mark_binding, is_binding_tracker
from instaui.vars.types import TMaybeRef


class Component(ComponentMixin, Jsonable):
    def __init__(self, tag: Optional[TMaybeRef[str]] = None):
        check_default_app_slot_or_error(
            "Not allowed to create element outside of ui.page"
        )
        mark_as_used(tag)

        self._tag = (
            "div"
            if tag is None or tag == ""
            else (mark_binding(tag) if is_binding_tracker(tag) else str(tag))
        )

        get_app_slot().append_component_to_container(self)

    def _to_json_dict(self) -> dict:
        data: dict = {
            "type": "cp",
            "tag": self._tag,
        }

        return data
