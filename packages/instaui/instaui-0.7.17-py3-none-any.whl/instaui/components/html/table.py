from __future__ import annotations
from typing import TYPE_CHECKING, Union
from instaui.components.element import Element
from instaui.components.content import Content
from instaui.components.vfor import VFor

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


class Table(Element):
    def __init__(
        self,
        columns: Union[list[str], TMaybeRef[list[str]], None] = None,
        rows: Union[list, TMaybeRef[list], None] = None,
    ):
        """Create a table element.

        Args:
            columns (Union[list[str], TMaybeRef[list[str]], None], optional): A list of column headers or a reactive reference to such a list. Defaults to None.
            rows (Union[list, TMaybeRef[list], None], optional): A list of row data, where each row is a list of cell values, or a reactive reference to such a list. Defaults to None.
        """
        super().__init__("table")

        with self:
            with Element("thead"), Element("tr"):
                with VFor(columns) as col:  # type: ignore
                    with Element("th"):
                        Content(col)

            with Element("tbody"):
                with VFor(rows) as row:  # type: ignore
                    with Element("tr"):
                        with VFor(row) as cell:  # type: ignore
                            with Element("td"):
                                Content(cell)
