from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Optional, Set
from contextlib import contextmanager
from instaui.common.jsonable import Jsonable
from instaui.common.component_mixin import ContainerMixin, ComponentMixin
from .resource import HtmlResource
from instaui.consts import _T_App_Mode
from types import MappingProxyType

if TYPE_CHECKING:
    from instaui.runtime.scope import Scope, BaseScope
    from instaui.dependencies.component_dependency import ComponentDependencyInfo
    from instaui.dependencies.plugin_dependency import PluginDependencyInfo
    from instaui.spa_router._route_model import RouteCollector


class App(Jsonable):
    _default_app_slot: ClassVar[Optional[App]] = None
    _web_server_info: ClassVar[Optional[dict]] = None

    def __init__(
        self,
        *,
        mode: _T_App_Mode,
        debug_mode: bool = False,
        meta: Optional[dict] = None,
    ) -> None:
        super().__init__()
        self._scope_id_counter = 0
        self._scoped_style_id_counter = 0
        self._mode: _T_App_Mode = mode
        self.meta = meta
        self.__debug_mode = debug_mode

        self._slots_stacks: list[ContainerMixin] = []
        self._base_scope: Optional[BaseScope] = None

        self._scope_stack: list[Scope] = []
        self._html_resource = HtmlResource()
        self._component_dependencies: Set[ComponentDependencyInfo] = set()
        self._temp_component_dependencies: dict[str, ComponentDependencyInfo] = {}
        self._plugin_dependencies: Set[PluginDependencyInfo] = set()

        self._page_path: Optional[str] = None
        self._page_params: dict[str, Any] = {}
        self._query_params: dict[str, Any] = {}
        self._route_collector: Optional[RouteCollector] = None
        self._router_base_scope: Optional[Scope] = None
        self._used_icons: set[str] = set()
        self._used_icons_set: set[str] = set()

    def collect_icon(self, icon_name: str):
        self._used_icons.add(icon_name)

    def collect_icon_set(self, icon_set_name: str):
        self._used_icons_set.add(icon_set_name)

    @contextmanager
    def _mark_router_base_scope(self, scope: Scope):
        self._router_base_scope = scope
        yield
        self._router_base_scope = None

    @property
    def debug_mode(self) -> bool:
        return self.__debug_mode

    @property
    def router_base_scope(self):
        return self._router_base_scope

    def setup(self, base_scope: BaseScope):
        base_scope.__enter__()
        self._base_scope = base_scope

    @property
    def mode(self) -> _T_App_Mode:
        return self._mode

    @property
    def base_scope(self) -> BaseScope:
        return self._base_scope  # type: ignore

    def gen_scope_id(self) -> int:
        sid = self._scope_id_counter
        self._scope_id_counter += 1
        return sid

    @property
    def top_scope(self) -> Scope:
        return self._scope_stack[0]

    @property
    def page_path(self) -> str:
        assert self._page_path is not None, "Page path is not set"
        return self._page_path  # type: ignore

    @property
    def page_params(self):
        return MappingProxyType(self._page_params)

    @property
    def query_params(self):
        return MappingProxyType(self._query_params)

    def gen_scoped_style_group_id(self):
        gid = f"scoped-style-{self._scoped_style_id_counter}"
        self._scoped_style_id_counter += 1
        return gid

    def reset_html_resource(self):
        self._html_resource = HtmlResource()

    def add_temp_component_dependency(self, dependency: ComponentDependencyInfo):
        self._temp_component_dependencies[dependency.tag_name] = dependency

    def get_temp_component_dependency(
        self, tag_name: str, default: ComponentDependencyInfo
    ) -> ComponentDependencyInfo:
        return self._temp_component_dependencies.get(tag_name, default)

    def has_temp_component_dependency(self, tag_name: str):
        return tag_name in self._temp_component_dependencies

    def use_component_dependency(
        self, dependency: ComponentDependencyInfo, *, replace=False
    ) -> None:
        if replace:
            self._component_dependencies.discard(dependency)

        self._component_dependencies.add(dependency)

    def use_plugin_dependency(self, dependency: PluginDependencyInfo) -> None:
        self._plugin_dependencies.add(dependency)

    def register_router(self, collector: RouteCollector) -> None:
        self._route_collector = collector

    def append_component_to_container(self, component: ComponentMixin):
        self._slots_stacks[-1].add_item(component)

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._page_path:
            url_info = {"path": self.page_path}
            if self._page_params:
                url_info["params"] = self._page_params  # type: ignore

            data["url"] = url_info

        if self._route_collector is not None:
            data["router"] = self._route_collector

        if self._web_server_info is not None:
            data["webInfo"] = self._web_server_info

        data["scope"] = self._base_scope

        icons = {}
        if self._used_icons:
            icons["names"] = list(self._used_icons)

        if self._used_icons_set:
            icons["sets"] = list(self._used_icons_set)

        if icons:
            data["icons"] = icons

        return data


class DefaultApp(App):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(DefaultApp, cls).__new__(cls)
        return cls._instance

    def append_component_to_container(self, component: ComponentMixin):
        raise ValueError("Operations are not allowed outside of ui.page")

    @property
    def base_scope(self) -> Scope:
        raise ValueError("Operations are not allowed outside of ui.page")
