from __future__ import annotations
from typing import TYPE_CHECKING, Optional
from instaui.components.slot import Slot, SlotManager, normalize_slot_name


if TYPE_CHECKING:
    from instaui.components.element import Element


class _NoPropSlotManager(SlotManager):
    def __init__(
        self, *, no_prop=False, no_prop_by_names: Optional[list[str]] = None
    ) -> None:
        super().__init__(no_prop=no_prop)
        self._no_prop_by_names = set(
            normalize_slot_name(name) for name in no_prop_by_names or []
        )

    def get_slot(self, name: str) -> Slot:
        name = normalize_slot_name(name)
        no_prop = name in self._no_prop_by_names
        return super().get_slot(name, _no_prop=no_prop)


def configure_slot_without_slot_prop(
    element: Element, *, slot_names: Optional[list[str]] = None
):
    element._slot_manager = (
        SlotManager(no_prop=True)
        if slot_names is None
        else _NoPropSlotManager(no_prop_by_names=slot_names)
    )
