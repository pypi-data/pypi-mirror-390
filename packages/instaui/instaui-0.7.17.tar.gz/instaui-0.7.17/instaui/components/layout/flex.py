from __future__ import annotations
from typing import Literal, Union
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.custom import configure_slot_without_slot_prop
from instaui.vars.types import TMaybeRef
from .base_props import TLayoutBaseProps
from instaui.components._responsive_type._common import TMaybeResponsive, TLevel_0_9


class TFlexBaseProps(TLayoutBaseProps, total=False):
    as_: TMaybeRef[Literal["div", "span"]]
    as_child: TMaybeRef[bool]
    display: TMaybeResponsive[Literal["none", "inline-flex", "flex"]]
    align: TMaybeResponsive[Literal["start", "center", "end", "stretch", "baseline"]]
    justify: TMaybeResponsive[Literal["start", "center", "end", "between"]]
    wrap: TMaybeResponsive[Literal["nowrap", "wrap", "wrap-reverse"]]
    gap: TMaybeResponsive[Union[str, TLevel_0_9]]
    gap_x: TMaybeResponsive[Union[str, TLevel_0_9]]
    gap_y: TMaybeResponsive[Union[str, TLevel_0_9]]


class TFlexProps(TFlexBaseProps, total=False):
    direction: TMaybeResponsive[
        Literal["row", "column", "row-reverse", "column-reverse"]
    ]


class Flex(Element):
    def __init__(
        self,
        **kwargs: Unpack[TFlexProps],
    ):
        """
        Creates a flex container with configurable layout and alignment.

        Args:
            **kwargs (Unpack[TFlexProps]): Flex container properties including:
                direction (TMaybeResponsive[Literal["row", "column", "row-reverse", "column-reverse"]]):
                    Flex direction for child elements.
                align (TMaybeResponsive[Literal["start", "center", "end", "stretch", "baseline"]]):
                    Cross-axis alignment of flex items.
                justify (TMaybeResponsive[Literal["start", "center", "end", "between"]]):
                    Main-axis alignment of flex items.
                wrap (TMaybeResponsive[Literal["nowrap", "wrap", "wrap-reverse"]]):
                    Flex wrapping behavior.
                gap (TMaybeResponsive[Union[str, TLevel_0_9]]): Gap between flex items.
                gap_x (TMaybeResponsive[Union[str, TLevel_0_9]]): Horizontal gap between items.
                gap_y (TMaybeResponsive[Union[str, TLevel_0_9]]): Vertical gap between items.
                display (TMaybeResponsive[Literal["none", "inline-flex", "flex"]]): Display type.
                as_ (TMaybeRef[Literal["div", "span"]]): HTML element type.
                as_child (TMaybeRef[bool]): Whether to merge with parent component.

        Example:
        .. code-block:: python
            # Basic flex container
            with ui.flex():
                ui.text("Item 1")
                ui.text("Item 2")

            # Row flex container
            with ui.row():
                ui.text("Horizontal items")

            # Column flex container
            with ui.column():
                ui.text("Vertical items")

            # Flex with gap and alignment
            with ui.flex(gap="2", align="center", justify="between"):
                ui.text("Left")
                ui.text("Center")
                ui.text("Right")
        """
        super().__init__("flex")
        configure_slot_without_slot_prop(self)

        self.props(kwargs)


class FlexRow(Flex):
    def __init__(
        self,
        **kwargs: Unpack[TFlexBaseProps],
    ):
        """
        Creates a horizontal flex container with row direction.

        Args:
            **kwargs (Unpack[TFlexBaseProps]): Flex container properties including:
                align (TMaybeResponsive[Literal["start", "center", "end", "stretch", "baseline"]]):
                    Vertical alignment of flex items.
                justify (TMaybeResponsive[Literal["start", "center", "end", "between"]]):
                    Horizontal alignment of flex items.
                wrap (TMaybeResponsive[Literal["nowrap", "wrap", "wrap-reverse"]]):
                    Flex wrapping behavior.
                gap (TMaybeResponsive[Union[str, TLevel_0_9]]): Gap between flex items.
                gap_x (TMaybeResponsive[Union[str, TLevel_0_9]]): Horizontal gap between items.
                gap_y (TMaybeResponsive[Union[str, TLevel_0_9]]): Vertical gap between items.
                display (TMaybeResponsive[Literal["none", "inline-flex", "flex"]]): Display type.
                as_ (TMaybeRef[Literal["div", "span"]]): HTML element type.
                as_child (TMaybeRef[bool]): Whether to merge with parent component.

        Example:
        .. code-block:: python
            # Basic horizontal flex container
            with ui.row():
                ui.text("Item 1")
                ui.text("Item 2")

            # Row with gap and alignment
            with ui.row(gap="2", align="center", justify="between"):
                ui.text("Left")
                ui.text("Center")
                ui.text("Right")
        """
        super().__init__(direction="row", **kwargs)


class FlexColumn(Flex):
    def __init__(
        self,
        **kwargs: Unpack[TFlexBaseProps],
    ):
        """
        Creates a vertical flex container with column direction.

        Args:
            **kwargs (Unpack[TFlexBaseProps]): Flex container properties including:
                align (TMaybeResponsive[Literal["start", "center", "end", "stretch", "baseline"]]):
                    Horizontal alignment of flex items.
                justify (TMaybeResponsive[Literal["start", "center", "end", "between"]]):
                    Vertical alignment of flex items.
                wrap (TMaybeResponsive[Literal["nowrap", "wrap", "wrap-reverse"]]):
                    Flex wrapping behavior.
                gap (TMaybeResponsive[Union[str, TLevel_0_9]]): Gap between flex items.
                gap_x (TMaybeResponsive[Union[str, TLevel_0_9]]): Horizontal gap between items.
                gap_y (TMaybeResponsive[Union[str, TLevel_0_9]]): Vertical gap between items.
                display (TMaybeResponsive[Literal["none", "inline-flex", "flex"]]): Display type.
                as_ (TMaybeRef[Literal["div", "span"]]): HTML element type.
                as_child (TMaybeRef[bool]): Whether to merge with parent component.

        Example:
        .. code-block:: python
            # Basic vertical flex container
            with ui.column():
                ui.text("Item 1")
                ui.text("Item 2")

            # Column with gap and alignment
            with ui.column(gap="2", align="center", justify="between"):
                ui.text("Top")
                ui.text("Middle")
                ui.text("Bottom")
        """
        super().__init__(direction="column", **kwargs)
