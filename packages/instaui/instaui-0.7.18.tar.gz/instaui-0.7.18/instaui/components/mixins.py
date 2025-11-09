from __future__ import annotations
from typing import Any, Protocol, Union, cast
from typing_extensions import Self
from instaui.vars.types import TMaybeRef


class PropsProtocol(Protocol):
    def props(self, add: Union[str, dict[str, Any], TMaybeRef]) -> Self: ...


class CanDisabledMixin:
    def disabled(self, disabled: TMaybeRef[bool] = True) -> Self:
        return cast(PropsProtocol, self).props({"disabled": disabled})  # type: ignore
