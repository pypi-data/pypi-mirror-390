import inspect
from fastapi import Response, APIRouter
from instaui.handlers import event_handler
from instaui.launch_collector import get_launch_collector

from . import _utils


def create_router(router: APIRouter):
    _async_handler(router)
    _sync_handler(router)


def _async_handler(router: APIRouter):
    @router.post(event_handler.ASYNC_URL)
    async def _(data: dict, response: Response):
        handler = _get_handler(data)
        if handler is None:
            return {"error": "event handler not found"}

        assert inspect.iscoroutinefunction(handler.fn), (
            "handler must be a coroutine function"
        )

        _utils.update_app_page_info(data)

        result = await handler.fn(*handler.get_handler_args(_get_binds_from_data(data)))
        return _utils.response_web_data(handler.outputs_binding_count, result, response)


def _sync_handler(router: APIRouter):
    @router.post(event_handler.SYNC_URL)
    def _(data: dict, response: Response):
        handler = _get_handler(data)
        if handler is None:
            return {"error": "event handler not found"}

        _utils.update_app_page_info(data)

        result = handler.fn(*handler.get_handler_args(_get_binds_from_data(data)))

        return _utils.response_web_data(handler.outputs_binding_count, result, response)

    if get_launch_collector().debug_mode:

        @router.get("/instaui/event-infos", tags=["instaui-debug"])
        def event_infos():
            return event_handler.get_statistics_info()


def _get_handler(data: dict):
    return event_handler.get_handler(data["hKey"])


def _get_binds_from_data(data: dict):
    return [bind for bind in data.get("bind", [])]
