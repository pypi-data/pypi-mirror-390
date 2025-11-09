from __future__ import annotations
from typing import Optional

from instaui.runtime._index import get_app_slot

from .ref_base import RefBase


class UseLanguageRef(RefBase):
    def __init__(
        self,
        deep_compare: bool = False,
        options: Optional[dict] = None,
    ) -> None:
        super().__init__(
            ref_type="useLanguage", deep_compare=deep_compare, args=options
        )


def use_language() -> str:
    """
    This function returns the current application's language setting, making it convenient to provide a unified language configuration for surrounding frameworks.
    """

    return get_app_slot().base_scope.use_language_ref
