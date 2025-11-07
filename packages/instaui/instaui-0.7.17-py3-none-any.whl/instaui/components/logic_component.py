from instaui.common.jsonable import Jsonable
from instaui.common.component_mixin import ContainerMixin, ComponentMixin
from instaui.runtime import (
    get_app_slot,
    get_slot_stacks,
    pop_slot,
)


class LogicComponent(ComponentMixin, Jsonable):
    def __init__(self, tag: str):
        self._tag = tag
        get_app_slot().append_component_to_container(self)

    def _to_json_dict(self) -> dict:
        data: dict = {
            "type": "logic",
            "tag": self._tag,
        }

        return data


class LogicContainer(ContainerMixin, LogicComponent):
    def __init__(self, tag: str):
        super().__init__(tag)

    def __enter__(self):
        get_slot_stacks().append(self)
        return self

    def __exit__(self, *_) -> None:
        pop_slot()
