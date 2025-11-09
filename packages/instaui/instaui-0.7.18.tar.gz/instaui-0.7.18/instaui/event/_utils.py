from typing import Any, Sequence

from instaui.common.binding_track_mixin import try_mark_binding
from instaui.common.var_track_mixin import mark_as_used


def mark_binding(bindings: Sequence[Any]):
    for binding in bindings:
        try_mark_binding(binding)


def mark_used(bindings: Sequence[Any]):
    mark_as_used(bindings)
