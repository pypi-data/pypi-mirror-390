from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Callable, Optional
from typing_extensions import TypeIs
from instaui.runtime import get_current_scope

if TYPE_CHECKING:
    from instaui.runtime.scope import Scope


class BindingTrackerMixin(ABC):
    @abstractmethod
    def _mark_binding(self, scope: Scope) -> dict:
        pass


class BindingTrackerHelper:
    def __init__(
        self,
        *,
        define_scope: Scope,
        upstreams_callback: Optional[Callable[[Scope], None]] = None,
    ) -> None:
        self._define_scope = define_scope
        self._upstreams_callback = upstreams_callback
        self._upstreams_binding_marked = False

    def mark_binding(self, *, var_id: int, scope: Scope) -> dict:
        sid = self._define_scope.id
        data = {
            "id": var_id,
            "sid": sid,
        }

        if not self._upstreams_binding_marked:
            if self._upstreams_callback is not None:
                self._upstreams_callback(self._define_scope)

            self._upstreams_binding_marked = True

        return scope.mark_bind(key=(sid, var_id), bind=data)


def is_binding_tracker(obj: Any) -> TypeIs[BindingTrackerMixin]:
    return isinstance(obj, BindingTrackerMixin)


def try_mark_binding(target: Any, *, scope: Optional[Scope] = None):
    if not is_binding_tracker(target):
        return target
    return mark_binding(target, scope=scope)


def mark_binding(target: BindingTrackerMixin, *, scope: Optional[Scope] = None):
    scope = scope or get_current_scope()
    return target._mark_binding(scope)
