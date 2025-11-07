from __future__ import annotations
from typing import Optional, Literal, Union
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef
from instaui.components._responsive_type._common import (
    TMaybeResponsive,
    TLevel_1_9,
)
from instaui.components._responsive_type._typography import (
    TWeightEnum,
    TTextWrapEnum,
    TTrimEnum,
    TAlignEnum,
)


class Heading(Element):
    def __init__(
        self,
        text: Optional[TMaybeRef[str]] = None,
        *,
        as_: Optional[TMaybeRef[Literal["h1", "h2", "h3", "h4", "h5", "h6"]]] = "h1",
        as_child: Optional[TMaybeRef[bool]] = None,
        size: Optional[TMaybeResponsive[TLevel_1_9]] = "6",
        weight: Optional[TMaybeResponsive[Union[TWeightEnum, str]]] = None,
        align: Optional[TMaybeResponsive[Union[TAlignEnum, str]]] = None,
        trim: Optional[TMaybeRef[Union[TTrimEnum, str]]] = None,
        truncate: Optional[TMaybeRef[bool]] = None,
        text_wrap: Optional[TMaybeRef[Union[TTextWrapEnum, str]]] = None,
    ):
        """
        Creates a heading element with customizable HTML tag level and typography styles.

        Args:
            text (Optional[TMaybeRef[str]]): The text content of the heading. Can be a static string or a reactive reference.
            as_ (Optional[TMaybeRef[Literal["h1", "h2", "h3", "h4", "h5", "h6"]]]): Specifies the HTML heading tag level.
                Defaults to "h1".
            as_child (Optional[TMaybeRef[bool]]): If True, renders the heading component without wrapping its own element,
                allowing it to inherit the parent context.
            size (Optional[TMaybeResponsive[TLevel_1_9]]): Controls the font size using a predefined size scale.
                Defaults to "6".
            weight (Optional[TMaybeResponsive[Union[TWeightEnum, str]]]): Sets the font weight style.
            align (Optional[TMaybeResponsive[Union[TAlignEnum, str]]]): Sets text alignment such as left,
                center, or right.
            trim (Optional[TMaybeRef[Union[TTrimEnum, str]]]): Adjusts whitespace trimming behavior.
            truncate (Optional[TMaybeRef[bool]]): If True, truncates long text with ellipsis when overflow occurs.
            text_wrap (Optional[TMaybeRef[Union[TTextWrapEnum, str]]]): Controls text wrapping behavior.

        Example:
        .. code-block:: python
            from instaui import ui

            # Render a default h1 heading
            ui.heading("ui.heading")
        """

        super().__init__("heading")

        self.props(
            {
                "innerText": text,
                "as": as_,
                "as_child": as_child,
                "size": size,
                "weight": weight,
                "text_align": align,
                "trim": trim,
                "truncate": truncate,
                "text_wrap": text_wrap,
            }
        )
