from __future__ import annotations

from typing import Optional
from instaui.common.component_mixin import ContainerMixin, ComponentMixin
from instaui.common.jsonable import Jsonable
from instaui.runtime import get_slot_stacks, pop_slot, get_app_slot, get_current_scope
from instaui.runtime.scope import Scope
from instaui.vars.slot_prop import SlotProp


_DEFAULT_SLOT_NAME = ":"


class SlotManager(Jsonable):
    def __init__(self, *, no_prop=False) -> None:
        super().__init__()
        self._slots: dict[str, Slot] = {}
        self.__no_prop = no_prop

    def get_slot(self, name: str, *, _no_prop: Optional[bool] = None) -> Slot:
        name = normalize_slot_name(name)

        if name not in self._slots:
            no_prop = _no_prop if _no_prop is not None else self.__no_prop
            self._slots[name] = Slot(name, has_children_box=not no_prop)

        return self._slots[name]

    @property
    def default(self):
        return self.get_slot(_DEFAULT_SLOT_NAME)

    def _to_json_dict(self):
        return {name: slot._to_json_dict() for name, slot in self._slots.items()}

    def has_slot(self) -> bool:
        return len(self._slots) > 0 and any(
            slot.has_items() for slot in self._slots.values()
        )


class Slot(ContainerMixin, Jsonable):
    def __init__(self, name: str, *, has_children_box=True) -> None:
        super().__init__()

        self._id: Optional[str] = None
        self._name = name
        self._children: list[ComponentMixin] = []
        self._slot_props_used_id: Optional[int] = None
        self.__has_children_box = has_children_box

        if self.__has_children_box:
            self._scope = _new_scope_slot()

        self.__define_scope = (
            self._scope if self.__has_children_box else get_current_scope()
        )

        self._used_prop: Optional[SlotProp] = None

    @property
    def _define_scope(self):
        return self.__define_scope

    def has_items(self):
        if self.__has_children_box:
            return len(self._scope._items) > 0

        return len(self._children) > 0

    def _mark_binding_used(self, var_id: int):
        self._slot_props_used_id = var_id

    def slot_props(self, name: str):
        if not self.__has_children_box:
            raise ValueError(
                "Not allowed to use slot props when slot has no children box"
            )

        self._use_slot_props = True

        if not self._used_prop:
            self._used_prop = SlotProp(name, slot=self)

        return self._used_prop[name]

    def __getitem__(self, item: str):
        return self.slot_props(item)

    def __enter__(self):
        if self.__has_children_box:
            self._scope.__enter__()
            return self

        get_slot_stacks().append(self)
        return self

    def __exit__(self, *_):
        if self.__has_children_box:
            self._scope.__exit__(*_)
            return

        pop_slot()

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self.__has_children_box:
            data["scope"] = self._scope

        if self._children:
            data["items"] = self._children

        if self._slot_props_used_id:
            data["usePropId"] = self._slot_props_used_id

        return data

    def add_item(self, item: ComponentMixin):
        self._children.append(item)


def _new_scope_slot():
    app = get_app_slot()
    _new_scope = Scope(app.gen_scope_id(), add_to_container=False)

    return _new_scope


def normalize_slot_name(name: str):
    return _DEFAULT_SLOT_NAME if name == "default" else name
