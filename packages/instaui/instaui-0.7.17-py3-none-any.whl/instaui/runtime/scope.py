from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Hashable, cast
from instaui.common.component_mixin import ComponentMixin, ContainerMixin
from instaui.common.jsonable import Jsonable
from instaui.runtime import get_app_slot, get_slot_stacks, pop_slot


if TYPE_CHECKING:
    from instaui.vars.ref_base import RefBase
    from instaui.vars.mixin_types.py_binding import CanInputMixin
    from instaui.vars.web_computed import WebComputed
    from instaui.vars.js_computed import JsComputed
    from instaui.vars.vue_computed import VueComputed
    from instaui.vars.data import ConstData
    from instaui.watch.web_watch import WebWatch
    from instaui.watch.js_watch import JsWatch
    from instaui.watch.vue_watch import VueWatch
    from instaui.vars.element_ref import ElementRef
    from instaui.components.vfor import VFor
    from instaui.js.fn import JsFn
    from instaui.vars.use_dark import UseDarkRef
    from instaui.vars.use_page_title import UsePageTitleRef
    from instaui.vars.use_language import UseLanguageRef


class Scope(ContainerMixin, ComponentMixin, Jsonable):
    def __init__(self, id: int, *, add_to_container=True) -> None:
        super().__init__()
        self.id = id
        self._vars_id_counter = 0
        self._element_ref_id_counter = 0
        self._refs: list[RefBase] = []
        self._element_refs: list[ElementRef] = []
        self._const_data: list[ConstData] = []
        self._js_computeds: list[JsComputed] = []
        self._vue_computeds: list[VueComputed] = []
        self._web_computeds: list[WebComputed] = []
        self._run_method_records: list = []
        self._web_watch_configs: list[WebWatch] = []
        self._js_watch_configs: list[JsWatch] = []
        self._vue_watch_configs: list[VueWatch] = []
        self._js_fns: list[JsFn] = []
        self._query = {}
        self.__has_registered_task = False
        self._items: list[ComponentMixin] = []
        self.__binds: dict[Hashable, dict] = {}
        self.__bind_index_map: dict[Hashable, int] = {}

        self._router_param_used_id: Optional[int] = None
        self._router_action_used_id: Optional[int] = None
        # vfor
        self._running_vfor: Optional[VFor] = None

        if add_to_container:
            get_app_slot().append_component_to_container(self)

    def mark_bind(self, key: Hashable, bind: dict):
        index = self.__bind_index_map.get(key)
        if index is None:
            self.__binds[key] = bind
            index = len(self.__binds) - 1
            self.__bind_index_map[key] = index

        return {"r": index}

    def __enter__(self):
        get_slot_stacks().append(self)
        get_app_slot()._scope_stack.append(self)
        return self

    def __exit__(self, *_) -> None:
        pop_slot()
        get_app_slot()._scope_stack.pop()

    def _mark_has_registered_task(self):
        self.__has_registered_task = True

    def add_item(self, item: ComponentMixin):
        self._items.append(item)

    @property
    def has_var(self):
        return self._vars_id_counter > 0

    @property
    def has_registered_task(self):
        return self.__has_registered_task

    def generate_vars_id(self) -> int:
        self._vars_id_counter += 1
        return self._vars_id_counter

    def _mark_vfor_exit(self):
        self._running_vfor = None

    def get_running_vfor(self) -> Optional[VFor]:
        return self._running_vfor

    def set_query(self, url: str, key: str, on: list[CanInputMixin]) -> None:
        self._query = {
            "url": url,
            "key": key,
            "on": [v for v in on],
        }

    def register_ref(self, ref: RefBase) -> int:
        self._refs.append(ref)
        return self.generate_vars_id()

    def register_web_computed(self, computed: WebComputed) -> int:
        self._web_computeds.append(computed)
        return self.generate_vars_id()

    def register_web_watch(self, watch: WebWatch) -> None:
        self._mark_has_registered_task()
        self._web_watch_configs.append(watch)

    def register_js_watch(self, watch: JsWatch) -> None:
        self._mark_has_registered_task()
        self._js_watch_configs.append(watch)

    def register_vue_watch(self, watch: VueWatch) -> None:
        self._mark_has_registered_task()
        self._vue_watch_configs.append(watch)

    def register_data(self, data: ConstData) -> int:
        self._const_data.append(data)
        return self.generate_vars_id()

    def register_element_ref(self, target: ElementRef) -> int:
        self._element_refs.append(target)
        return self.generate_vars_id()

    def register_js_computed(self, computed: JsComputed) -> int:
        self._js_computeds.append(computed)
        return self.generate_vars_id()

    def register_vue_computed(self, computed: VueComputed) -> int:
        self._vue_computeds.append(computed)
        return self.generate_vars_id()

    def register_router_param_used(self) -> int:
        if self._router_param_used_id is None:
            self._router_param_used_id = self.generate_vars_id()
        return self._router_param_used_id

    def register_router_action_used(self) -> int:
        if self._router_action_used_id is None:
            self._router_action_used_id = self.generate_vars_id()
        return self._router_action_used_id

    def register_js_fn(self, fn: JsFn) -> int:
        self._js_fns.append(fn)
        return self.generate_vars_id()

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data.update(
            {
                "type": "scope",
                "tag": "scope",
            }
        )

        if self._items:
            data["items"] = self._items

        if self._query:
            data["query"] = self._query
        if self._web_watch_configs:
            data["py_watch"] = self._web_watch_configs
        if self._js_watch_configs:
            data["js_watch"] = self._js_watch_configs
        if self._vue_watch_configs:
            data["vue_watch"] = self._vue_watch_configs
        if self._element_refs:
            data["eRefs"] = self._element_refs

        if self._web_computeds:
            data["web_computed"] = self._web_computeds

        if self._js_computeds:
            data["js_computed"] = self._js_computeds

        if self._vue_computeds:
            data["vue_computed"] = self._vue_computeds
        if self._const_data:
            data["data"] = self._const_data

        if self._js_fns:
            data["jsFn"] = self._js_fns

        if self._refs:
            data["refs"] = self._refs

        if self.__binds:
            data["binds"] = list(self.__binds.values())

        if self._router_param_used_id is not None:
            data["routerParam"] = self._router_param_used_id

        if self._router_action_used_id is not None:
            data["routerAct"] = self._router_action_used_id

        return data


class BaseScope(Scope):
    def __init__(self, id: int) -> None:
        super().__init__(id, add_to_container=False)
        self._use_dark: Optional[UseDarkRef] = None
        self._use_page_title: Optional[UsePageTitleRef] = None
        self._use_language: Optional[UseLanguageRef] = None

    def setup(
        self,
        *,
        use_dark: UseDarkRef,
        use_page_title: UsePageTitleRef,
        use_language: UseLanguageRef,
    ):
        self._use_dark = use_dark
        self._use_page_title = use_page_title
        self._use_language = use_language

    @property
    def use_dark_ref(self) -> bool:
        return cast(bool, self._use_dark)

    @property
    def use_page_title_ref(self) -> str:
        return cast(str, self._use_page_title)

    @property
    def use_language_ref(self) -> str:
        return cast(str, self._use_language)


class GlobalScope(Scope):
    def __init__(self, id: int) -> None:
        super().__init__(id)

    def register_ref(self, ref: RefBase) -> str:
        raise ValueError("Can not register ref in global scope")

    def register_web_computed(self, computed: WebComputed) -> int:
        raise ValueError("Can not register web_computeds in global scope")

    def register_js_computed(self, computed: JsComputed) -> int:
        raise ValueError("Can not register js_computeds in global scope")

    def register_vue_computed(self, computed: VueComputed) -> int:
        raise ValueError("Can not register vue_computeds in global scope")

    def register_web_watch(self, watch: WebWatch) -> None:
        raise ValueError("Can not register web_watchs in global scope")

    def register_js_watch(self, watch: JsWatch) -> None:
        raise ValueError("Can not register js_watchs in global scope")

    def register_vue_watch(self, watch: VueWatch) -> None:
        raise ValueError("Can not register vue_watchs in global scope")
