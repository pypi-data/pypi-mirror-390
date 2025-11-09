from abc import ABC, abstractmethod
from typing import Any, Callable, Mapping, Optional, Iterable
from typing_extensions import TypeIs
from instaui.runtime import get_current_scope


class VarTrackerMixin(ABC):
    @abstractmethod
    def _mark_as_used(self):
        pass


class VarTrackerHelper:
    def __init__(
        self,
        *,
        var_id_gen_fn: Optional[Callable[[], int]] = None,
        upstreams_getter: Optional[Callable[[], Iterable]] = None,
    ):
        self._upstreams_getter = upstreams_getter
        self._var_id_gen_fn = var_id_gen_fn
        self._scope = get_current_scope()
        self._marked = False
        self._var_id: Optional[int] = None

    @property
    def var_id(self) -> int:
        return self._var_id  # type: ignore

    def mark_as_used(self):
        if self._marked:
            return

        if self._upstreams_getter is not None:
            for target in self._upstreams_getter():
                mark_as_used(target)

        self._marked = True

        if self._var_id_gen_fn is not None:
            self._var_id = self._var_id_gen_fn()


def is_var_tracker(obj: Any) -> TypeIs[VarTrackerMixin]:
    return isinstance(obj, VarTrackerMixin)


def mark_as_used(maybe_tracker: Any):
    if isinstance(maybe_tracker, (list, tuple)):
        for item in maybe_tracker:
            if is_var_tracker(item):
                item._mark_as_used()
    elif isinstance(maybe_tracker, Mapping):
        for value in maybe_tracker.values():
            if is_var_tracker(value):
                value._mark_as_used()
    elif is_var_tracker(maybe_tracker):
        maybe_tracker._mark_as_used()
    else:
        pass
