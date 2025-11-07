from ._index import (
    get_app_slot,
    reset_app_slot,
    new_app_slot,
    use_default_app_slot,
    get_slot_stacks,
    pop_slot,
    get_current_scope,
    check_default_app_slot_or_error,
    in_default_app_slot,
    update_web_server_info,
    get_default_app_slot,
)
from ._inner_helper import check_web_only_mode_or_error
from .resource import HtmlResource
from ._scope_manager import try_new_scope_on_ui_state


__all__ = [
    "get_slot_stacks",
    "get_current_scope",
    "get_app_slot",
    "reset_app_slot",
    "new_app_slot",
    "use_default_app_slot",
    "pop_slot",
    "check_web_only_mode_or_error",
    "check_default_app_slot_or_error",
    "in_default_app_slot",
    "update_web_server_info",
    "get_default_app_slot",
    "try_new_scope_on_ui_state",
    "HtmlResource",
]
