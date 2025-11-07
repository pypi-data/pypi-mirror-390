from __future__ import annotations
from typing import Optional, Literal
from typing_extensions import Unpack
from instaui.components.element import Element
from instaui.custom import configure_slot_without_slot_prop
from instaui.vars.types import TMaybeRef
from .base_props import TLayoutBaseProps
from instaui.components._responsive_type._common import TMaybeResponsive


class Container(Element):
    def __init__(
        self,
        *,
        as_child: Optional[TMaybeRef[bool]] = None,
        size: Optional[TMaybeResponsive[Literal["1", "2", "3", "4"]]] = "4",
        display: Optional[TMaybeResponsive[Literal["none", "initial"]]] = None,
        align: Optional[TMaybeResponsive[Literal["left", "center", "right"]]] = None,
        **kwargs: Unpack[TLayoutBaseProps],
    ):
        """
        Creates a responsive container with constrained maximum width and alignment.

        Args:
            as_child (Optional[TMaybeRef[bool]]): Whether to merge props with parent component.
            size (Optional[TMaybeResponsive[Literal["1", "2", "3", "4"]]]): Container size
                that determines the maximum width. Defaults to "4" (largest size).
            display (Optional[TMaybeResponsive[Literal["none", "initial"]]]): CSS display property.
            align (Optional[TMaybeResponsive[Literal["left", "center", "right"]]]): Horizontal
                alignment of the container content.
            **kwargs (Unpack[TLayoutBaseProps]): Additional layout properties like padding, margin, etc.

        Example:
        .. code-block:: python
            # Default container (size 4)
            with ui.container():
                ui.text("Default container content")

            # Smaller container (size 2)
            with ui.container(size="2"):
                ui.text("Small container content")

            # Centered container
            with ui.container(align="center"):
                ui.text("Centered content")
        """
        super().__init__("container")
        configure_slot_without_slot_prop(self)

        self.props(
            {
                "as_child": as_child,
                "ctn_size": size,
                "display": display,
                "align": align,
                **kwargs,
            }
        )
