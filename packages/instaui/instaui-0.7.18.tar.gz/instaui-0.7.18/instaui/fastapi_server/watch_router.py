from fastapi import APIRouter
from instaui.handlers import watch_handler
from instaui.launch_collector import get_launch_collector

from . import _utils


def create_router(router: APIRouter):
    _async_handler(router)
    _sync_handler(router)


def _async_handler(router: APIRouter):
    @router.post(watch_handler.ASYNC_URL)
    async def _(data: dict):
        hkey = data.pop("key")
        handler_info = watch_handler.get_handler_info(hkey)
        if handler_info is None:
            return {"error": "watch handler not found"}

        _utils.update_app_page_info(data)

        result = await handler_info.fn(
            *handler_info.get_handler_args(_get_binds_from_data(data))
        )
        return _utils.response_web_data(handler_info.outputs_binding_count, result)


def _sync_handler(router: APIRouter):
    @router.post(watch_handler.SYNC_URL)
    def _(data: dict):
        hkey = data.pop("key")
        handler_info = watch_handler.get_handler_info(hkey)
        if handler_info is None:
            return {"error": "watch handler not found"}

        _utils.update_app_page_info(data)

        result = handler_info.fn(
            *handler_info.get_handler_args(_get_binds_from_data(data))
        )
        return _utils.response_web_data(handler_info.outputs_binding_count, result)

    if get_launch_collector().debug_mode:

        @router.get("/instaui/watch-infos", tags=["instaui-debug"])
        def watch_infos():
            return watch_handler.get_statistics_info()


def _get_binds_from_data(data: dict):
    return data.get("input", [])
