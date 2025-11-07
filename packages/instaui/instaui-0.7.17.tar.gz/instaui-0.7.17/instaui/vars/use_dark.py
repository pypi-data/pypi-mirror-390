from __future__ import annotations
from typing import Optional

from instaui.runtime._index import get_app_slot

from .ref_base import RefBase


class UseDarkRef(RefBase):
    def __init__(
        self,
        deep_compare: bool = False,
        options: Optional[dict] = None,
    ) -> None:
        super().__init__(ref_type="useDark", deep_compare=deep_compare, args=options)


def use_dark() -> bool:
    """
    On start up, it reads the value from localStorage/sessionStorage (the key is configurable) to see if there is a user configured color scheme, if not, it will use users' system preferences.


    Example:
    .. code-block:: python
        from instaui import ui,html

        @ui.page('/')
        def index():
            dark = ui.use_dark()
            html.checkbox(dark)
    """

    return get_app_slot().base_scope.use_dark_ref
