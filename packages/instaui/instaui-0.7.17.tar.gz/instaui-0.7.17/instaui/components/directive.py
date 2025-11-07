from __future__ import annotations

from typing import (
    Any,
    Optional,
)
from instaui.common.binding_track_mixin import try_mark_binding
from instaui.common.jsonable import Jsonable
from instaui.common.var_track_mixin import mark_as_used


class Directive(Jsonable):
    def __init__(
        self,
        *,
        is_sys: bool,
        name: str,
        arg: Optional[str] = None,
        modifiers: Optional[list[Any]] = None,
        value: Optional[Any] = None,
    ) -> None:
        super().__init__()
        mark_as_used(value)
        self.name = name
        self._arg = arg
        self._is_sys = is_sys
        self._modifiers = modifiers
        self._value = try_mark_binding(value)

    def __hash__(self) -> int:
        return hash(f"{self.name}:{self._arg}:{self._modifiers}")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Directive):
            return False
        return (
            self.name == other.name
            and self._arg == other._arg
            and self._modifiers == other._modifiers
        )

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._arg:
            data["arg"] = self._arg

        if self._value:
            data["value"] = self._value

        if self._modifiers:
            data["mf"] = list(dict.fromkeys(self._modifiers).keys())

        data["sys"] = int(self._is_sys)

        return data
