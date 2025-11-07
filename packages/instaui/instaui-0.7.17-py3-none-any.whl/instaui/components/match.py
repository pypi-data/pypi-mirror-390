from __future__ import annotations

import typing
from instaui.common.binding_track_mixin import try_mark_binding, is_binding_tracker
from instaui.common.component_mixin import ComponentMixin
from instaui.common.var_track_mixin import mark_as_used
from instaui.vars.types import TMaybeRef
from instaui.components.logic_component import LogicContainer


class Match(LogicContainer):
    def __init__(self, cond: TMaybeRef[typing.Any]):
        """
        Creates a conditional logic container that renders different UI blocks
        based on the value of the given reactive reference. Each case is checked
        sequentially, and the first match will be displayed. A default case can be
        defined to handle unmatched values.

        Args:
            cond (TMaybeRef[typing.Any]): A reactive reference or plain value whose
                state determines which case block should be rendered.

        Example:
        .. code-block:: python
            a = ui.state("")

            html.input().vmodel(a)

            with ui.match(a) as mt:
                with mt.case("page1"):
                    html.paragraph("in page1 case")

                with mt.case("page2"):
                    html.paragraph("in page2 case")

                with mt.default():
                    html.paragraph("in default case")
        """

        super().__init__("match")
        mark_as_used(cond)

        self._cond = try_mark_binding(cond)
        self._const_cond = not is_binding_tracker(cond)
        self._cases: list[MatchCase] = []
        self._default_case: typing.Optional[DefaultCase] = None

        self._items: list[ComponentMixin] = []

    def __enter__(self):
        super().__enter__()
        return MatchWrapper(self)

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["cond"] = self._cond
        if self._const_cond:
            data["const"] = 1

        if self._cases:
            data["cases"] = self._cases

        if self._default_case:
            data["default"] = self._default_case

        return data

    def add_item(self, item: ComponentMixin):
        pass


class MatchWrapper:
    def __init__(self, host: Match) -> None:
        self.__host = host

    def case(self, value: typing.Any):
        assert not is_binding_tracker(value), "Cannot use binding in case value"
        case = MatchCase(value)
        self.__host._cases.append(case)
        return case

    def default(self):
        default_case = DefaultCase()
        self.__host._default_case = default_case
        return default_case


class MatchCase(LogicContainer):
    def __init__(self, value: typing.Any):
        super().__init__("match-case")
        self._value = value
        self._items: list[ComponentMixin] = []

    def _to_json_dict(self) -> dict:
        data = {}
        data["value"] = self._value
        if self._items:
            data["items"] = self._items
        return data

    def add_item(self, item: ComponentMixin):
        self._items.append(item)


class DefaultCase(LogicContainer):
    def __init__(self):
        super().__init__("default-case")
        self._items: list[ComponentMixin] = []

    def _to_json_dict(self) -> dict:
        data = {}
        if self._items:
            data["items"] = self._items
        return data

    def add_item(self, item: ComponentMixin):
        self._items.append(item)
