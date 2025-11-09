from typing import Any, Tuple, TypeVar, Union, cast
from instaui.common.const_data_mixin import ConstDataMixin
from instaui.runtime.scope import Scope
from instaui.vars.path_var import PathVar
from instaui.vars.ref import Ref
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.mixin_types.py_binding import CanInputMixin, CanOutputMixin
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.element_binding import ElementBindingMixin
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.common.var_track_mixin import VarTrackerMixin
from instaui.common.binding_track_mixin import BindingTrackerMixin

from instaui.common.jsonable import Jsonable
from instaui.vars.ref_base import RefBase


from pydantic import BaseModel, RootModel


_T = TypeVar("_T")


_ProxyModel = RootModel


class RefProxy(
    CanInputMixin,
    ObservableMixin,
    CanOutputMixin,
    StrFormatBindingMixin,
    ElementBindingMixin,
    VarTrackerMixin,
    BindingTrackerMixin,
    PathVar,
    Jsonable,
):
    def __init__(self, data, ref_base: RefBase) -> None:
        self._ref_ = ref_base
        self._prop_names_ = set(data.keys()) if isinstance(data, dict) else set()

    @property
    def __ref_(self):
        return super().__getattribute__("_ref_")

    def __deepcopy__(self, memo):
        return self.__ref_.__deepcopy__(memo)

    def __getattribute__(self, name):
        if name not in super().__getattribute__("_prop_names_"):
            return super().__getattribute__(name)

        return self.__ref_[name]

    def __getitem__(self, name):
        return self.__ref_[name]

    def not_(self):
        return self.__ref_.not_()

    def __add__(self, other: str):
        return self.__ref_ + other

    def __radd__(self, other: str):
        return other + self.__ref_

    def __sub__(self, other: Union[int, float]):
        return self.__ref_ - other

    def __rsub__(self, other: Union[int, float]):
        return other - self.__ref_

    def __mul__(self, other: Union[int, float]):
        return self.__ref_ * other

    def __rmul__(self, other: Union[int, float]):
        return other * self.__ref_

    def __truediv__(self, other: Union[int, float]):
        return self.__ref_ / other

    def __rtruediv__(self, other: Union[int, float]):
        return other / self.__ref_

    def __and__(self, other: Any):
        return self.__ref_ & other

    def __or__(self, other: Any):
        return self.__ref_ | other

    def __lt__(self, other):
        return self.__ref_ < other

    def __le__(self, other):
        return self.__ref_ <= other

    def __gt__(self, other):
        return self.__ref_ > other

    def __ge__(self, other):
        return self.__ref_ >= other

    def __ne__(self, other):
        return self.__ref_ != other

    def len_(self):
        return self.__ref_.len_()

    def _to_str_format_binding(self, order: int) -> Tuple[str, str]:
        return self.__ref_._to_str_format_binding(order)

    def _to_json_dict(self):
        return self.__ref_._to_json_dict()

    def _to_event_output_type(self) -> OutputSetType:
        return self.__ref_._to_event_output_type()

    def _to_event_input_type(self) -> InputBindingType:
        return self.__ref_._to_event_input_type()

    def _mark_as_used(self):
        self._ref_._mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self._ref_._mark_binding(scope)


class StateModel(BaseModel, Jsonable):
    pass

    def _to_json_dict(self):
        return self.model_dump()


def state(
    value: _T,
    deep_compare: bool = False,
) -> _T:
    """
    Creates a reactive state wrapper that enables automatic UI updates when its value or
    nested elements change. Supports primitives, lists, dictionaries, and provides
    reactive operations such as indexing, comparisons, and length evaluation.

    Args:
        value (_T): The initial value to be wrapped as a reactive state. Can be any
            Python type including primitives, lists, or dictionaries.
        deep_compare (bool): Whether state updates should compare nested values to
            determine change propagation. Defaults to False.

    Example:
    .. code-block:: python
        from instaui import ui, html

        # Value reactivity
        s = ui.state('hello')
        html.input(s)
        ui.text(s)


        # List reactivity
        items = ui.state([1, 2, 3])
        html.number(items[0])
        html.ul.from_list(items)


        # Dictionary mutation triggers UI updates
        data = ui.state({"name": "John"})
        html.input(data["name"])


        # State used with js_computed
        data = ui.state({"items": [1, 2, 3]})
        items = ui.js_computed(inputs=[data], code="(d)=> d.items")
        html.ul.from_list(items)


        # Boolean operations maintain reactivity
        value = ui.state([{"state": True}])
        html.checkbox(value[0]["state"])
        html.paragraph(ui.not_(value[0]["state"]))


        # String or list length as reactive value
        text = ui.state("Hello")
        html.paragraph(ui.str_format("len: {}", ui.len_(text)))


        # Comparison operators trigger updates
        a = ui.state(1)
        b = ui.state(2)
        html.paragraph(a < b)  # UI updates when a or b changes
    """

    if isinstance(value, RefProxy):
        return value

    new_value = (
        value.get_value()
        if isinstance(value, ConstDataMixin)
        else _ProxyModel(value).model_dump()
    )
    obj = RefProxy(new_value, Ref(value, deep_compare=deep_compare))
    return cast(_T, obj)
