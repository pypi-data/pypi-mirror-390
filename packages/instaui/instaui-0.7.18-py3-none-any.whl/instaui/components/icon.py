from __future__ import annotations
from typing import Optional, Union
from instaui.components.element import Element
from instaui.runtime._index import get_app_slot


class Icon(Element):
    def __init__(
        self,
        icon: Optional[str] = None,
        *,
        size: Optional[Union[int, str]] = None,
        color: Optional[str] = None,
        raw_svg: Optional[str] = None,
    ):
        """
        Creates an icon component by referencing an SVG symbol from a local file.

        By default, the icon is loaded from a predefined directory structure:
        ```
        - assets/
          - icons/
            - set1.svg  # Contains SVG symbols with IDs matching `icon` names
        - main.py      # Entry point of the application
        ```

        Args:
            icon (Optional[str]): The name of the icon to display. This must match the `id`
                        of an SVG `<symbol>` in the target SVG file.
            size (Optional[Union[int, str]]): The size of the icon in pixels or CSS units.
                                              Defaults to None (natural size).
            color (Optional[str]): The color of the icon. Defaults to None (inherits text color).
            raw_svg (Optional[str]): The raw SVG code to use instead of loading from a file.

        Example:
        .. code-block:: python
            # Renders the SVG symbol with ID "icon-1" from `assets/icons/set1.svg`
            ui.icon("set1:icon-1")

            # Renders with custom size and color
            ui.icon("set1:icon-2", size=24, color="#f00")
        """
        super().__init__("icon")

        if isinstance(icon, str):
            get_app_slot().collect_icon(icon)

        self.props(
            {
                "icon": icon,
                "size": size,
                "color": color,
                "rawSvg": raw_svg,
            }
        )

    @staticmethod
    def register_icon_set(name: str):
        """
        Register the icon SVG file. Useful when you need to dynamically use a large number of icons.

        Args:
            name (str): The name of the icon set.

        Example:
        .. code-block:: python
            ui.icon.register_icon_set("set1")  # Registers `assets/icons/set1.svg`
        """
        get_app_slot().collect_icon_set(name)
