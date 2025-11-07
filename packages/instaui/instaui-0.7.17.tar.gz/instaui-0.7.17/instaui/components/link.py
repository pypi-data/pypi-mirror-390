from __future__ import annotations
from typing import Literal, Optional
from instaui.components.element import Element


class Link(Element):
    def __init__(
        self,
        href: Optional[str] = None,
        *,
        text: Optional[str] = None,
        target: Optional[
            Literal["_blank", "_self", "_parent", "_top", "_unfencedTop"]
        ] = None,
        type: Optional[str] = None,
    ):
        """
        A wrapper component for HTML anchor links with predefined styles and common attributes.

        This component simplifies the creation of styled links and supports both static and
        reactive properties for dynamic behavior.

        Args:
            href (Optional[str]): The URL the link points to. Corresponds to the 'href' attribute.
            text (Optional[str]): The display text of the link. If not set, child elements are used.
            target (Optional[Literal]): Specifies where to open the linked document
                                       (e.g., '_blank' for new tab).
            type (Optional[str]): Hints at the linked resource's MIME type (e.g., 'text/html').

        # Example:
        .. code-block:: python
            from instaui import ui

            # Basic link
            ui.link("https://example.com", text="Visit Example")

            # Link with custom target
            ui.link("https://example.com", text="Open in new tab", target="_blank")

            # Link with child content
            with ui.link("https://example.com"):
                ui.text("Styled link content")

        """
        super().__init__("ui-link")

        self.props(
            {
                "href": href,
                "text": text,
                "target": target,
                "type": type,
            }
        )
