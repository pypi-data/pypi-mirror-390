from __future__ import annotations
from typing import (
    Callable,
    Generator,
    Literal,
    Optional,
    Tuple,
    Union,
    Sequence,
    Generic,
    TypeVar,
    cast,
)
from contextlib import contextmanager
from enum import Enum
from dataclasses import dataclass
from instaui.common.component_mixin import ComponentMixin
from instaui.runtime import get_current_scope, get_app_slot
from instaui.runtime.scope import Scope
from instaui.vars.vfor_item import VForItem, VForIndex, VForItemKey
from instaui.common.var_track_mixin import mark_as_used
from instaui.common.binding_track_mixin import (
    try_mark_binding,
    mark_binding,
    is_binding_tracker,
)
from instaui.components.logic_component import LogicContainer


@dataclass
class _VForRangeInfo:
    end: int
    start: int = 1
    step: int = 1

    def mark_as_used(self):
        mark_as_used(self.end)
        mark_as_used(self.start)
        mark_as_used(self.step)

    def to_data(self):
        data = {
            "end": try_mark_binding(self.end),
        }
        if self.start != 0:
            data["start"] = try_mark_binding(self.start)
        if self.step != 1:
            data["step"] = try_mark_binding(self.step)

        return data


_T = TypeVar("_T")


class VForArrayTypeEnum(Enum):
    CONST = "c"
    REF = "r"
    RANGE = "n"


class VFor(LogicContainer, Generic[_T]):
    def __init__(
        self,
        data: Union[Sequence[_T], _VForRangeInfo, dict[str, _T], _T],
        *,
        key: Union[Literal["item", "index"], str] = "index",
    ):
        """for loop component.

        Args:
            data (Union[Sequence[_T], ElementBindingMixin[list[_T]]]): data source.
            key (Union[Literal[&quot;item&quot;, &quot;index&quot;], str]]): key for each item. Defaults to 'index'.

        Examples:
        .. code-block:: python
            items = ui.state([1,2,3])

            with ui.vfor(items) as item:
                html.span(item)

            # object key
            items = ui.state([{"name": "Alice"}, {"name": "Bob"}])
            with ui.vfor(items, key="item.name") as item:
                html.span(item.name)

            # js computed key
            items = ui.state([{"name": "Alice"}, {"name": "Bob"}])
            with ui.vfor(items, key=": (item , index) => item.name + index") as item:
                html.span(item.name)

            # iter info
            items = ui.state({"a": 1, "b": 2, "c": 3})
            with ui.vfor(items).with_key() as [value, key]:

                html.span(key)
                html.span(value)

            # range
            with ui.vfor.range(10) as i:
                html.paragraph(i)
        """

        super().__init__("vfor")

        mark_as_used(data)
        if isinstance(data, _VForRangeInfo):
            data.mark_as_used()

        # Must be before new scope
        if is_binding_tracker(data):
            self._data = mark_binding(data)
            self._array_type = VForArrayTypeEnum.REF
        elif isinstance(data, _VForRangeInfo):
            self._data = data.to_data()
            self._array_type = VForArrayTypeEnum.RANGE
        else:
            self._data = data
            self._array_type = VForArrayTypeEnum.CONST

        self._key = key
        self._transition_group_setting = None
        self._items: list[ComponentMixin] = []
        self._exit_callbacks: list[Callable[[], None]] = []
        self._binding_used_info = {}
        self._scope = _new_scope_vfor(self)

    def _mark_binding_used(self, *, type: Literal["item", "index", "key"], var_id: int):
        self._binding_used_info[type] = var_id

    def __enter__(self) -> _T:
        return cast(_T, VForItem(self))

    @contextmanager
    def with_index(self) -> Generator[Tuple[_T, int], None, None]:
        with self:
            yield (
                VForItem(self),
                VForIndex(self),
            )  # type: ignore

    @contextmanager
    def with_key(self) -> Generator[Tuple[_T, str], None, None]:
        with self:
            yield (
                VForItem(self),
                VForItemKey(self),
            )  # type: ignore

    @contextmanager
    def with_key_index(self) -> Generator[Tuple[_T, str, int], None, None]:
        with self:
            yield (
                VForItem(self),
                VForItemKey(self),
                VForIndex(self),
            )  # type: ignore

    def __exit__(self, *_) -> None:
        for callback in self._exit_callbacks:
            callback()

        self._exit_callbacks.clear()
        get_current_scope()._mark_vfor_exit()

    def _set_range_type(self):
        self._array_type = VForArrayTypeEnum.RANGE

    def transition_group(self, name="fade", tag: Optional[str] = None):
        self._transition_group_setting = {"name": name, "tag": tag}
        return self

    def _on_exit(self, exit_callback: Callable[[], None]):
        self._exit_callbacks.append(exit_callback)

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data.update(
            {
                "type": "logic",
                "tag": "vfor",
            }
        )

        if self._scope:
            data["scope"] = self._scope

        if self._key is not None and self._key != "index":
            data["fkey"] = self._key

        if self._data:
            data["array"] = {"type": self._array_type.value, "value": self._data}

        if self._transition_group_setting is not None:
            data["tsGroup"] = {
                k: v for k, v in self._transition_group_setting.items() if v is not None
            }

        if self._binding_used_info:
            data["used"] = self._binding_used_info

        return data

    @classmethod
    def range(
        cls,
        end: int,
        *,
        start: int = 0,
        step: int = 1,
    ) -> VFor[int]:
        obj = cls(_VForRangeInfo(start=start, end=end, step=step))

        return obj  # type: ignore

    def add_item(self, item: ComponentMixin):
        self._items.append(item)


def _new_scope_vfor(vfor: VFor):
    app = get_app_slot()
    _new_scope = Scope(app.gen_scope_id(), add_to_container=False)

    _new_scope.__enter__()

    @vfor._on_exit
    def _():
        _new_scope.__exit__()

    return _new_scope
