from __future__ import annotations
import typing

from instaui.runtime import get_app_slot
from instaui.common.jsonable import Jsonable
from instaui.runtime.scope import Scope

from . import _types


class RouteItem(Jsonable):
    def __init__(
        self,
        *,
        component_fn: typing.Optional[typing.Callable] = None,
        vue_route_item: VueRouteItem,
        meta: typing.Optional[dict] = None,
        children: typing.Optional[list[RouteItem]] = None,
    ) -> None:
        self._meta = meta
        self._vue_item = None
        self._scope: typing.Optional[Scope] = None
        self._children = children

        if component_fn is None and (not vue_route_item.path):
            raise ValueError("Either component_fn or vue_route_item.path must be set")

        if component_fn is None:
            self._vue_item = vue_route_item
            return

        if vue_route_item.path is None:
            vue_route_item.path = (
                f"/{'' if component_fn.__name__ == 'index' else component_fn.__name__}"
            )

        app = get_app_slot()

        with Scope(app.gen_scope_id(), add_to_container=False) as scope:
            with app._mark_router_base_scope(scope):
                component_fn()

        self._scope = scope
        self._vue_item = vue_route_item

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._meta:
            data["meta"] = self._meta

        if self._vue_item:
            data["vueItem"] = self._vue_item

        if self._scope:
            data["scope"] = self._scope

        if self._children:
            data["children"] = self._children

        return data

    @classmethod
    def create(
        cls,
        *,
        component_fn: typing.Optional[typing.Callable] = None,
        path: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        params: typing.Optional[dict[str, str]] = None,
        children: typing.Optional[list[RouteItem]] = None,
        meta: typing.Optional[dict] = None,
    ):
        """Create a new RouteItem

        Examples:
        .. code-block:: python
            routes = [
                spa_router.RouteItem.create(path='/',component_fn=home),
                spa_router.RouteItem.create(path='/user',component_fn=user_home),
            ]

            spa_router.config_router(routes=routes)

        Args:
            component_fn (typing.Callable): function that returns a component to be rendered.
            path (typing.Optional[str], optional): route path. Defaults to None.
            name (typing.Optional[str], optional): route name. Defaults to None.
            params (typing.Optional[dict[str, str]], optional): route params. Defaults to None.
            children (typing.Optional[list[RouteItem]], optional): child routes. Defaults to None.

        """

        return cls(
            component_fn=component_fn,
            meta=meta,
            children=children,
            vue_route_item=VueRouteItem(
                path=path,
                name=name,
                params=params,
            ),
        )


class VueRouteItem(Jsonable):
    def __init__(
        self,
        *,
        path: typing.Optional[str] = None,
        name: typing.Optional[str] = None,
        params: typing.Optional[dict[str, str]] = None,
    ) -> None:
        self.path = path
        self._name = name
        self._params = params

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self.path is not None:
            data["path"] = self.path

        if self._name is not None:
            data["name"] = self._name

        if self._params is not None:
            data["params"] = self._params

        return data


class RouteCollector(Jsonable):
    def __init__(
        self,
        mode: _types.TRouterHistoryMode = "hash",
        keep_alive: bool = False,
        routes: typing.Optional[list[RouteItem]] = None,
    ) -> None:
        self._mode = mode
        self._keep_alive = keep_alive
        self._routes = routes or []

    def add_route(self, item: RouteItem):
        self._routes.append(item)
        return self

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._mode != "hash":
            data["mode"] = self._mode

        if self._keep_alive is not False:
            data["kAlive"] = self._keep_alive

        if self._routes:
            data["routes"] = self._routes

        return data
