from __future__ import annotations
import threading
from typing import Callable, Optional
from . import _utils


UPLOAD_URL = "/instaui/upload_file"
_event_handlers: dict[str, _utils.HandlerInfo] = {}
dict_lock = threading.Lock()


def register_upload_file_handler(key: str, handler: Callable):
    upload_url = f"{UPLOAD_URL}?hkey={key}"

    if key in _event_handlers:
        return upload_url

    handler_info = _utils.HandlerInfo.from_handler(
        handler,
        0,
        skip_convert_param=True,
    )

    with dict_lock:
        _event_handlers[key] = handler_info

    return upload_url


def get_handler(key: str) -> Optional[_utils.HandlerInfo]:
    return _event_handlers.get(key)


create_handler_key = _utils.create_handler_key
