from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Sequence
from instaui.common.binding_track_mixin import (
    mark_binding,
    try_mark_binding,
    is_binding_tracker,
)

from instaui.vars._types import InputBindingType, OutputSetType

if TYPE_CHECKING:
    from instaui.runtime.scope import Scope


class CanInputMixin(ABC):
    @abstractmethod
    def _to_event_input_type(self) -> InputBindingType:
        pass


class CanOutputMixin(ABC):
    @abstractmethod
    def _to_event_output_type(self) -> OutputSetType:
        pass


def inputs_to_config(inputs: Sequence[CanInputMixin]):
    return [
        {
            "value": mark_binding(input) if is_binding_tracker(input) else input,
            "type": input._to_event_input_type().value
            if isinstance(input, CanInputMixin)
            else InputBindingType.Data.value,
        }
        for input in inputs
    ]


def outputs_to_config(
    outputs: Sequence[CanOutputMixin], *, scope: Optional[Scope] = None
):
    return [
        {
            "ref": try_mark_binding(ref, scope=scope),
            "type": ref._to_event_output_type().value,
        }
        for ref in outputs
    ]


def _assert_outputs_be_can_output_mixin(outputs: Sequence):
    for output in outputs:
        if not isinstance(output, CanOutputMixin):
            raise TypeError("The outputs parameter must be a `ui.state`")
