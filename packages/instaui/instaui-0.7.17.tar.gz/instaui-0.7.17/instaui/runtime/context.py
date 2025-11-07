from __future__ import annotations
from typing import Any, Optional
from ._index import get_app_slot


class Context:
    _instance: Optional[Context] = None

    @classmethod
    def get_instance(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self):
        self._page_params: dict[str, Any] = {}

    @property
    def app_mode(self):
        return get_app_slot().mode

    @property
    def debug_mode(self):
        return get_app_slot().debug_mode

    @property
    def page_path(self):
        return get_app_slot().page_path

    @property
    def page_params(self):
        return get_app_slot().page_params

    @property
    def query_params(self):
        return get_app_slot().query_params


def get_context():
    """
    Retrieves the current UI context, providing access to page parameters, query parameters, and other request-specific data.

    Example:
    .. code-block:: python
        from instaui import ui, html

        # Access page parameters
        @ui.page('/{name})
        def index():
            name = ui.context().page_params.get("name")
            html.paragraph(f"Hello {name}!")


        # Access query parameters. http://localhost/?name=foo
        @ui.page('/)
        def index():
            name = ui.context().query_params.get("name")
            html.paragraph(f"Hello {name}!")
    """

    return Context.get_instance()
