from typing import Union
from pathlib import Path
import inspect
from instaui.launch_collector import get_launch_collector


def create_server(
    debug: bool = False,
    use_gzip: Union[int, bool] = True,
):
    """
    Create a new server instance.

    Note: When deploy to production, you need to set `debug=False`

    Args:
        debug (bool): Whether to run in debug mode. In debug mode, it has the development hot-reload feature. Defaults to False.
        use_gzip (Union[int, bool], optional):  Whether to use gzip compression. If an integer is provided, it will be used as the minimum response size for compression. If True, the default minimum size of 500 bytes will be used. If False, compression will not be used. Defaults to True.
    """
    from instaui.fastapi_server.server import Server

    caller_file_path = get_caller_file_path()
    get_launch_collector().setup(debug_mode=debug)

    return Server(use_gzip=use_gzip, caller_file_path=caller_file_path)


def get_caller_file_path() -> Path:
    frame = inspect.currentframe().f_back.f_back  # type: ignore
    assert frame is not None
    file_path = inspect.getfile(frame)
    return Path(file_path).resolve()
