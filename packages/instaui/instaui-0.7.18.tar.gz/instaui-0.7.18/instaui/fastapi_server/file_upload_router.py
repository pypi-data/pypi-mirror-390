from typing import Optional
from fastapi import APIRouter, Request, UploadFile, Query, File
from starlette.datastructures import UploadFile as StarletteUploadFile
from instaui.handlers import upload_file_handler
from instaui.fastapi_server.systems import async_system


def create_router(router: APIRouter):
    _async_handler(router)


def _async_handler(router: APIRouter):
    @router.post(upload_file_handler.UPLOAD_URL)
    async def _(
        request: Request,
        hkey: str = Query(...),
        files: list[UploadFile] = File(None),
        file: UploadFile = File(None),
    ):
        handler = _get_handler(hkey)
        if handler is None:
            raise ValueError("event handler not found")

        real_file = await _convert_file(request, files, file)
        return await async_system.maybe_async(handler.fn, real_file)


def _get_handler(hkey: str):
    return upload_file_handler.get_handler(hkey)


async def _convert_file(
    request: Request,
    files: Optional[list[UploadFile]] = None,
    file: Optional[UploadFile] = None,
):
    if file:
        return file
    if files:
        return files

    form = await request.form()
    indexed_files = []
    for key, value in form.multi_items():
        if key.startswith("file["):
            if isinstance(value, StarletteUploadFile):
                indexed_files.append(value)

    return indexed_files
