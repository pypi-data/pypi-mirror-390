from __future__ import annotations
from abc import abstractmethod
from typing import Any, Optional, Union, cast
from typing_extensions import Self
from dataclasses import dataclass, field
from instaui.common.binding_track_mixin import (
    is_binding_tracker,
    BindingTrackerMixin,
    mark_binding,
    try_mark_binding,
)
from instaui.common.var_track_mixin import VarTrackerMixin, mark_as_used
from instaui.runtime.scope import Scope
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.mixin_types.pathable import PathableMixin
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.py_binding import CanInputMixin, CanOutputMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin


@dataclass
class PathInfo:
    name: str
    args: Optional[list[Any]] = field(default=None)
    _is_binds: Optional[list[bool]] = field(default_factory=list, init=False)

    def __post_init__(self):
        self._is_binds = (
            None
            if self.args is None
            else [is_binding_tracker(arg) for arg in self.args]
        )

    def is_all_bind(self):
        return self._is_binds is not None and all(self._is_binds)

    def is_all_const(self):
        return self._is_binds is None or all(not bind for bind in self._is_binds)

    def mark_as_used(self):
        mark_as_used(self.args)

    def try_mark_binding(self, scope: Scope):
        if self.args is None:
            return [self.name]

        return [
            self.name,
            [try_mark_binding(arg, scope=scope) for arg in self.args],
            [int(bind) for bind in cast(list[bool], self._is_binds)],
        ]


class PathVar(PathableMixin):
    def __getitem__(self, item: Union[str, int]):
        return PathTrackerBindable(self)[item]

    def __deepcopy__(self, memo):
        memo[id(self)] = self
        return self

    def not_(self):
        return PathTrackerBindable(self).not_()

    def __add__(self, other: str):
        return PathTrackerBindable(self) + other

    def __radd__(self, other: str):
        return other + PathTrackerBindable(self)

    def __sub__(self, other: Union[int, float]):
        return PathTrackerBindable(self) - other

    def __rsub__(self, other: Union[int, float]):
        return other - PathTrackerBindable(self)

    def __mul__(self, other: Union[int, float]):
        return PathTrackerBindable(self) * other

    def __rmul__(self, other: Union[int, float]):
        return other * PathTrackerBindable(self)

    def __truediv__(self, other: Union[int, float]):
        return PathTrackerBindable(self) / other

    def __rtruediv__(self, other: Union[int, float]):
        return other / PathTrackerBindable(self)

    def __and__(self, other: Any):
        return other & PathTrackerBindable(self)

    def __or__(self, other: Any):
        return other | PathTrackerBindable(self)

    def __lt__(self, other):
        return PathTrackerBindable(self) < other

    def __le__(self, other):
        return PathTrackerBindable(self) <= other

    def __gt__(self, other):
        return PathTrackerBindable(self) > other

    def __ge__(self, other):
        return PathTrackerBindable(self) >= other

    def __ne__(self, other):
        return PathTrackerBindable(self) != other

    def len_(self):
        return PathTrackerBindable(self).len_()


class PathTracker(PathableMixin):
    def __init__(self, paths: Optional[list[PathInfo]] = None):
        self.paths = paths or []

    def __deepcopy__(self, memo):
        memo[id(self)] = self
        return self

    def __getitem__(self, key) -> Self:
        return self.__new_self__([*self.paths, PathInfo("bind", [key])])

    def __getattr__(self, key) -> Self:
        return self.__new_self__([*self.paths, PathInfo("bind", [key])])

    def not_(self) -> Self:
        return self.__new_self__([*self.paths, PathInfo("!")])

    def __add__(self, other: str) -> Self:
        return self.__new_self__([*self.paths, PathInfo("+", [other])])

    def __radd__(self, other: str) -> Self:
        return self.__new_self__([*self.paths, PathInfo("~+", [other])])

    def __sub__(self, other: Union[int, float]):
        return self.__new_self__([*self.paths, PathInfo("-", [other])])

    def __rsub__(self, other: Union[int, float]):
        return self.__new_self__([*self.paths, PathInfo("~-", [other])])

    def __mul__(self, other: Union[int, float]):
        return self.__new_self__([*self.paths, PathInfo("*", [other])])

    def __rmul__(self, other: Union[int, float]):
        return self.__new_self__([*self.paths, PathInfo("~*", [other])])

    def __truediv__(self, other: Union[int, float]):
        return self.__new_self__([*self.paths, PathInfo("/", [other])])

    def __rtruediv__(self, other: Union[int, float]):
        return self.__new_self__([*self.paths, PathInfo("~/", [other])])

    def __and__(self, other: Any):
        return self.__new_self__([*self.paths, PathInfo("&&", [other])])

    def __or__(self, other: Any):
        return self.__new_self__([*self.paths, PathInfo("||", [other])])

    def __lt__(self, other):
        return self.__new_self__([*self.paths, PathInfo("<", [other])])

    def __le__(self, other):
        return self.__new_self__([*self.paths, PathInfo("<=", [other])])

    def __gt__(self, other):
        return self.__new_self__([*self.paths, PathInfo(">", [other])])

    def __ge__(self, other):
        return self.__new_self__([*self.paths, PathInfo(">=", [other])])

    def __ne__(self, other):
        return self.__new_self__([*self.paths, PathInfo("!=", [other])])

    def len_(self):
        return self.__new_self__([*self.paths, PathInfo("len")])

    @abstractmethod
    def __new_self__(self, paths: list[PathInfo]) -> Self:
        pass


class PathTrackerBindable(
    PathTracker,
    CanInputMixin,
    ObservableMixin,
    CanOutputMixin,
    ElementBindingMixin,
    StrFormatBindingMixin,
    BindingTrackerMixin,
    VarTrackerMixin,
):
    def __init__(self, source: PathableMixin):
        super().__init__()
        self.__source = source

    def __deepcopy__(self, memo):
        memo[id(self)] = self
        return self

    def __new_self__(self, paths: list[Union[str, list[str]]]) -> PathTrackerBindable:
        obj = PathTrackerBindable(self.__source)
        obj.paths = paths
        return obj

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.Ref

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.Ref

    def _mark_as_used(self):
        cast(VarTrackerMixin, self.__source)._mark_as_used()

        for path in self.paths:
            path.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        assert is_binding_tracker(self.__source)
        data = mark_binding(self.__source, scope=scope)

        if self.paths:
            data["path"] = _try_mark_binding_path_infos(self.paths, scope=scope)

        return data


def _try_mark_binding_path_infos(path_infos: list[PathInfo], scope: Scope):
    all_paths = all(path.name == "bind" for path in path_infos)
    all_const_paths = all_paths and all(path.is_all_const() for path in path_infos)

    if all_const_paths:
        return [cast(list, path.args)[0] for path in path_infos]

    return [path.try_mark_binding(scope=scope) for path in path_infos]
