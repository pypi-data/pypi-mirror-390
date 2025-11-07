import typing
from . import _types
from instaui.runtime import get_app_slot
from . import _install
from ._router_param_var import RouteParamsVar
from ._router_action import RouterActionVar, RouterMethod
from ._route_model import RouteItem

_ASSERT_MSG = "Router is not initialized."


def add_route(
    page_fn: typing.Callable,
    *,
    name: typing.Optional[str] = None,
    path: typing.Optional[str] = None,
    children: typing.Optional[list[RouteItem]] = None,
    lazy_loading: bool = False,
):
    """
    Registers a page function as a route in the SPA router, optionally with nested child routes and lazy loading.

    Args:
        page_fn (Callable): The function that renders the page content when the route is activated.
        name (Optional[str]): A unique name for the route, used for programmatic navigation and linking.
        path (Optional[str]): The URL path that triggers this route. Can include dynamic segments like '/page/:id'.
        children (Optional[list[RouteItem]]): A list of nested RouteItem objects representing child routes under this route.
        lazy_loading (bool): Whether to enable lazy loading for this route, deferring its component initialization until first access.

    Example:
    .. code-block:: python
        from instaui import html, spa_router, ui

        @ui.page()
        def index():
            # Basic route registration
            def home():
                html.paragraph("hello home")

            def user_page():
                name = spa_router.get_params("name")
                html.paragraph(ui.str_format("welcome: {name}", name=name))

            # Add routes with different configurations
            spa_router.add_route(home)
            spa_router.add_route(user_page, path="/user/:name")

            # ui
            with ui.row():
                spa_router.link("home page", to="/")
                spa_router.link("user page", to="/user/foo")
                spa_router.link("user page", to="/user/bar")
    """

    _install.try_register_router_collector()
    route_collector = get_app_slot()._route_collector
    assert route_collector is not None, _ASSERT_MSG
    route_collector.add_route(
        RouteItem.create(
            path=path,
            component_fn=page_fn,
            name=name,
            children=children,
        )
    )


def config_router(
    routes: typing.Optional[list[RouteItem]] = None,
    *,
    history: _types.TRouterHistoryMode = "hash",
    keep_alive: bool = False,
):
    """Configure the router.

    Examples:
    .. code-block:: python
        routes = [
            spa_router.RouteItem.create(path='/',component_fn=home),
            spa_router.RouteItem.create(path='/user',component_fn=user_home),
        ]

        spa_router.config_router(routes=routes)

    Args:
        routes (typing.Optional[list[RouteItem]], optional): list of routes to be added to the router. Defaults to None.
        history (_types.TRouterHistoryMode, optional): router history mode. Can be "web", "memory" or "hash". Defaults to "hash".
        keep_alive (bool, optional): whether to keep the components alive when navigating to a new route.Defaults to False.
    """

    _install.try_register_router_collector()

    route_collector = get_app_slot()._route_collector
    assert route_collector is not None, _ASSERT_MSG

    route_collector._mode = history
    route_collector._keep_alive = keep_alive
    route_collector._routes = routes or []


def get_params(param_name: str) -> typing.Any:
    return RouteParamsVar("params")[param_name]


def get_path():
    return RouteParamsVar("path")


def get_full_path():
    return RouteParamsVar("fullPath")


def push(
    *,
    path: typing.Optional[str] = None,
    name: typing.Optional[str] = None,
    params: typing.Optional[dict[str, typing.Any]] = None,
    query: typing.Optional[dict[str, typing.Any]] = None,
    hash: typing.Optional[str] = None,
):
    method_params: dict = {}

    if path is not None:
        method_params["path"] = path
    if name is not None:
        method_params["name"] = name

    if params is not None:
        method_params["params"] = params
    if query is not None:
        method_params["query"] = query
    if hash is not None:
        method_params["hash"] = hash

    return RouterMethod(
        fn="push",
        args=[method_params],
    )


def go(n: int):
    return RouterMethod(
        fn="go",
        args=[n],
    )


def forward():
    return go(1)


def back():
    return go(-1)


def output():
    return RouterActionVar()
