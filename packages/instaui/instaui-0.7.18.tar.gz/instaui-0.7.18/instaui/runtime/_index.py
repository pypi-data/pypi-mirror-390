from typing import Optional
from typing_extensions import Unpack, TypedDict
from instaui.consts import _T_App_Mode
from contextvars import ContextVar, Token

from instaui.launch_collector import get_launch_collector
from ._app import App, DefaultApp


def _create_default():
    if App._default_app_slot is None:
        App._default_app_slot = DefaultApp(mode="web")
    return App._default_app_slot


_app_var: ContextVar[App] = ContextVar("_app_var", default=_create_default())


def use_default_app_slot():
    assert App._default_app_slot is not None, "Default app slot is not set"
    _app_var.set(App._default_app_slot)


def get_default_app_slot():
    return _create_default()


def get_app_slot() -> App:
    return _app_var.get()


def get_current_scope():
    current_scope = get_app_slot()._scope_stack[-1]
    if current_scope is None:
        raise ValueError("No current scope")
    return current_scope


def get_slot_stacks():
    return get_app_slot()._slots_stacks


def pop_slot():
    get_slot_stacks().pop()


def new_app_slot(mode: _T_App_Mode, *, app_meta: Optional[dict] = None):
    app = App(mode=mode, meta=app_meta, debug_mode=get_launch_collector().debug_mode)
    token = _app_var.set(app)
    return app, token


def reset_app_slot(token: Token[App]):
    _app_var.reset(token)


def in_default_app_slot():
    return isinstance(get_app_slot(), DefaultApp)


def check_default_app_slot_or_error(
    error_message="Operations are not allowed outside of ui.page",
):
    if isinstance(get_app_slot(), DefaultApp):
        raise ValueError(error_message)


class TWebServerInfo(TypedDict, total=False):
    watch_url: Optional[str]
    watch_async_url: Optional[str]
    event_url: Optional[str]
    event_async_url: Optional[str]
    download_url: Optional[str]


def update_web_server_info(**kwargs: Unpack[TWebServerInfo]):
    if App._web_server_info is None:
        App._web_server_info = {}

    data = {k: v for k, v in kwargs.items() if v is not None}

    App._web_server_info.update(data)
