from __future__ import annotations
from typing import Any, Optional, Literal, Union
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


class Text(Element):
    def __init__(
        self,
        text: Optional[TMaybeRef[Any]] = None,
        *,
        as_: Optional[TMaybeRef[Literal["span", "div", "label", "p", "pre"]]] = None,
        as_child: Optional[TMaybeRef[bool]] = None,
        size: Optional[TMaybeResponsive[TLevel_1_9]] = None,
        weight: Optional[TMaybeResponsive[Union[TWeightEnum, str]]] = None,
        align: Optional[TMaybeResponsive[Union[TAlignEnum, str]]] = None,
        trim: Optional[TMaybeRef[Union[TTrimEnum, str]]] = None,
        truncate: Optional[TMaybeRef[bool]] = None,
        text_wrap: Optional[TMaybeRef[Union[TTextWrapEnum, str]]] = None,
    ):
        """
        Creates a text element with customizable styling and typography options.

        Args:
            text (Optional[TMaybeRef[Any]]): The text content to display.
            as_ (Optional[TMaybeRef[Literal["span", "div", "label", "p", "pre"]]]):
                HTML element type to render as. Defaults to appropriate semantic element.
            as_child (Optional[TMaybeRef[bool]]): Whether to merge props with parent component.
            size (Optional[TMaybeResponsive[TLevel_1_9]]): Text size level from 1 to 9.
            weight (Optional[TMaybeResponsive[Union[TWeightEnum, str]]]): Font weight.
            align (Optional[TMaybeResponsive[Union[TAlignEnum, str]]]): Text alignment.
            trim (Optional[TMaybeRef[Union[TTrimEnum, str]]]): Whitespace trimming behavior.
            truncate (Optional[TMaybeRef[bool]]): Whether to truncate overflowing text.
            text_wrap (Optional[TMaybeRef[Union[TTextWrapEnum, str]]]): Text wrapping behavior.

        Example:
        .. code-block:: python
            # Basic text element
            ui.text("ui.text")

            # Text with specific HTML element and styling
            ui.text(
                "Styled text",
                as_="div",
                size=3,
                weight="bold",
                align="center"
            )
        """
        super().__init__("ui-text")

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
