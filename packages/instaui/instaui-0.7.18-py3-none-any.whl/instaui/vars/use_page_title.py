from __future__ import annotations
from typing import Optional

from instaui.common.binding_track_mixin import is_binding_tracker
from instaui.runtime._index import get_app_slot

from .ref_base import RefBase


class UsePageTitleRef(RefBase):
    def __init__(
        self,
        deep_compare: bool = False,
        options: Optional[dict] = None,
    ) -> None:
        super().__init__(
            ref_type="usePageTitle", deep_compare=deep_compare, args=options
        )


def use_page_title(title: Optional[str] = None) -> str:
    """Set the title of the HTML document.

    Args:
        title (str): The title of the HTML document.
    """
    if not is_binding_tracker(title) and title is not None:
        get_app_slot()._html_resource.title = title

    return get_app_slot().base_scope.use_page_title_ref
