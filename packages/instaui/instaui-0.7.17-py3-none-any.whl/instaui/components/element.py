from __future__ import annotations

import ast
from copy import copy
import inspect
from pathlib import Path
import re
from typing import (
    Any,
    Callable,
    Iterable,
    ClassVar,
    Literal,
    Optional,
    Set,
    Union,
    cast,
    overload,
    TYPE_CHECKING,
)
from typing_extensions import Self
from collections import defaultdict
from instaui.common.binding_track_mixin import (
    mark_binding,
    try_mark_binding,
    is_binding_tracker,
)
from instaui.event import event_modifier
from instaui.event.event_modifier import TEventModifier
from instaui.runtime import get_app_slot
from instaui.vars.element_ref import ElementRef
from instaui.vars.vfor_item import VForItem
from instaui.components.directive import Directive
from instaui.dependencies.component_dependency import (
    ComponentDependencyInfo,
)
from .slot import SlotManager, Slot
from instaui import consts
from instaui.components.component import Component


from instaui.common.var_track_mixin import mark_as_used
from instaui.event.event_mixin import EventMixin

if TYPE_CHECKING:
    from instaui.vars.types import TMaybeRef


TVarGetterStrategy = Union[Literal["as_needed", "all"], list]

# Refer to the NiceGUI project.
# https://github.com/zauberzeug/nicegui/blob/main/nicegui/element.py
PROPS_PATTERN = re.compile(
    r"""
# Match a key-value pair optionally followed by whitespace or end of string
([:\w\-]+)          # Capture group 1: Key
(?:                 # Optional non-capturing group for value
    =               # Match the equal sign
    (?:             # Non-capturing group for value options
        (           # Capture group 2: Value enclosed in double quotes
            "       # Match  double quote
            [^"\\]* # Match any character except quotes or backslashes zero or more times
            (?:\\.[^"\\]*)*  # Match any escaped character followed by any character except quotes or backslashes zero or more times
            "       # Match the closing quote
        )
        |
        (           # Capture group 3: Value enclosed in single quotes
            '       # Match a single quote
            [^'\\]* # Match any character except quotes or backslashes zero or more times
            (?:\\.[^'\\]*)*  # Match any escaped character followed by any character except quotes or backslashes zero or more times
            '       # Match the closing quote
        )
        |           # Or
        ([\w\-.%:\/]+)  # Capture group 4: Value without quotes
    )
)?                  # End of optional non-capturing group for value
(?:$|\s)            # Match end of string or whitespace
""",
    re.VERBOSE,
)


class Element(Component):
    dependency: ClassVar[Optional[ComponentDependencyInfo]] = None
    _default_props: ClassVar[dict[str, Any]] = {}
    _default_classes: ClassVar[list[str]] = []
    _default_style: ClassVar[dict[str, str]] = {}

    def __init__(self, tag: Optional[TMaybeRef[str]] = None):
        if self.dependency:
            tag = self.dependency.tag_name or ""

        super().__init__(tag)

        self._str_classes: list[str] = []
        self._dict_classes: dict[str, dict] = {}
        self._bind_str_classes: list[dict] = []
        self._str_classes.extend(self._default_classes)
        self._style: dict[str, str] = {}
        self._style.update(self._default_style)
        self._style_str_binds: list[dict] = []
        self._style_dict_binds: dict[str, dict] = {}
        self._props: dict[str, Any] = {}
        self._props.update(self._default_props)
        self._props_dict_binds: dict[str, dict] = {}
        self._proxy_props: list[dict] = []

        self._events: defaultdict[str, list[dict]] = defaultdict(list)
        self._directives: dict[Directive, None] = {}

        self._slot_manager = SlotManager()
        self.__element_ref: Optional[dict] = None

    def __init_subclass__(
        cls,
        *,
        esm: Union[str, Path, None] = None,
        externals: Optional[dict[str, Path]] = None,
        css: Union[list[Union[str, Path]], None] = None,
    ) -> None:
        super().__init_subclass__()

        if esm:
            esm = _make_dependency_path(esm, cls)

            if externals:
                externals = {
                    key: _make_dependency_path(value, cls)
                    for key, value in externals.items()
                }

            if css:
                css = set(_make_dependency_path(c, cls) for c in css)  # type: ignore

            tag_name = f"instaui-{esm.stem}"

            cls.dependency = ComponentDependencyInfo(
                tag_name=tag_name,
                esm=esm,
                externals=cast(dict[str, Path], externals or {}),
                css=cast(Set[Path], css or set()),
            )

        cls._default_props = copy(cls._default_props)
        cls._default_classes = copy(cls._default_classes)
        cls._default_style = copy(cls._default_style)

    def on_mounted(
        self,
        handler: EventMixin,
        *,
        extends: Optional[list] = None,
    ):
        return self.on(
            ":mounted",
            handler=handler,
            extends=extends,
        )

    def __enter__(self):
        self._slot_manager.default.__enter__()
        return self

    def __exit__(self, *_) -> None:
        self._slot_manager.default.__exit__(*_)

    def scoped_style(
        self,
        style: str,
        *,
        selector: Union[str, Callable[[str], str]] = "*",
        with_self=False,
    ):
        """
        Applies scoped CSS styles to child elements within the component.

        Args:
            style (str): The CSS style rules to be applied within the scope.
            selector (Union[str, Callable[[str], str]], optional): CSS selector or function
                that generates a selector to target specific child elements. Defaults to "*".
            with_self (bool, optional): If True, applies the styles to the component itself
                in addition to its children. Defaults to False.

        Example:
        .. code-block:: python
            # Apply red outline to all direct children
            ui.column().scoped_style("outline: 1px solid red;")

            # Apply styles only to elements with specific class
            ui.box().scoped_style("color: blue;", selector=".target-class")

            # Apply styles to component itself and children
            ui.column().scoped_style("outline: 1px solid red;", with_self=True)

            # Use lambda function for dynamic selector generation
            ui.box().scoped_style(
                "outline: 1px solid red;",
                selector=lambda t: f"{t}:has(.hover) .target"
            )
        """
        app = get_app_slot()
        ssid = app.gen_scoped_style_group_id()

        select_box = f"*[insta-scoped-style={ssid}]"
        real_selector = (
            f"{select_box} {selector}"
            if isinstance(selector, str)
            else selector(select_box)
        )

        if with_self:
            real_selector = f"{select_box},{real_selector}"

        real_selector = f":where({real_selector})"
        style_code = f"{real_selector} {{ {style} }}"

        self.props({"insta-scoped-style": ssid})
        app._html_resource.add_style_tag(
            style_code, group_id=consts.SCOPED_STYLE_GROUP_ID
        )
        return self

    def slot_props(self, name: str):
        return self._slot_manager.default.slot_props(name)

    @staticmethod
    def _update_classes(
        classes: list[str],
        add: str,
    ) -> list[str]:
        return list(dict.fromkeys(classes + add.split()))

    @staticmethod
    def _parse_style(text: Union[str, dict[str, str]]) -> dict[str, str]:
        if isinstance(text, dict):
            return text

        if not text:
            return {}

        result = {}
        for item in text.split(";"):
            item = item.strip()
            if item:
                key, value = item.split(":")
                key = key.strip()
                value = value.strip()
                result[key] = value

        return result

    @staticmethod
    def _parse_props(props: Union[str, dict[str, Any]]) -> dict[str, Any]:
        if isinstance(props, dict):
            return props

        if not props:
            return {}

        dictionary = {}
        for match in PROPS_PATTERN.finditer(props or ""):
            key = match.group(1)
            value = match.group(2) or match.group(3) or match.group(4)
            if value is None:
                dictionary[key] = True
            else:
                if (value.startswith("'") and value.endswith("'")) or (
                    value.startswith('"') and value.endswith('"')
                ):
                    value = ast.literal_eval(value)
                dictionary[key] = value
        return dictionary

    def key(self, key: Any):
        """Set the key prop of the component.

        Args:
            key (str): The key prop value.

        """
        self.props({"key": key})
        return self

    def vmodel(
        self,
        value: Any,
        modifiers: Union[consts.TModifier, list[consts.TModifier], None] = None,
        *,
        prop_name: str = "value",
        is_html_component=False,
    ):
        if prop_name == "value":
            prop_name = "modelValue"

        modifiers = modifiers or []
        if isinstance(modifiers, str):
            modifiers = [modifiers]

        self.directive(
            Directive(
                is_sys=is_html_component,
                name="vmodel",
                arg=prop_name,
                modifiers=modifiers,
                value=value,  # type: ignore
            )
        )

        return self

    def add_slot(self, name: str) -> Slot:
        """
        Creates and adds a new named slot to the current component, returning the slot object for further use.

        Args:
            name (str): The name of the slot to create and add. This name is used to reference the slot within the component.

        Example:
        .. code-block:: python
            cp = some_component()

            # Default slot
            with cp as default_slot:
                html.span(default_slot.slot_props("count"))

            # Add a named footer slot
            with cp.add_slot("footer") as footer_slot:
                html.span(footer_slot.slot_props("count"))
        """

        return self._slot_manager.get_slot(name)

    @overload
    def classes(self, add: str) -> Self: ...
    @overload
    def classes(self, add: dict[str, TMaybeRef[bool]]) -> Self: ...

    @overload
    def classes(self, add: TMaybeRef[str]) -> Self: ...

    def classes(
        self,
        add: Union[
            str,
            dict[str, TMaybeRef[bool]],
            TMaybeRef[str],
            VForItem,
        ],
    ) -> Self:
        """
        Adds one or more CSS classes to the element, supporting static strings,
        reactive string references, or conditional class bindings.

        Args:
            add (str | dict[str, TMaybeRef[bool]] | TMaybeRef[str] | VForItem):
                CSS class configuration to apply. It can be:
                - A static class name string.
                - A reactive reference to a dynamic class name string.
                - A dictionary mapping class names to reactive boolean values,
                which toggle classes on or off.
                - A loop item reference when used inside v-for style bindings.

        Example:
        .. code-block:: python
            from instaui import ui, html

            # Static class
            html.span("target").classes("test")

            # Dynamic class string
            ref = ui.state("c1")
            html.span("target").classes(ref)

            # Conditional class binding
            c1 = ui.state(True)
            c2 = ui.state(False)
            html.span("target").classes({"c1": c1, "c2": c2})
        """

        mark_as_used(add)

        if isinstance(add, str):
            self._str_classes = self._update_classes(self._str_classes, add)

        elif isinstance(add, dict):
            self._dict_classes.update(
                **{key: try_mark_binding(value) for key, value in add.items()}
            )

        elif is_binding_tracker(add):
            self._bind_str_classes.append(mark_binding(add))

        return self

    def style(self, add: Union[str, dict[str, Any], TMaybeRef[str]]) -> Self:
        """
        Applies inline CSS styles to the element. Supports static strings, dictionaries, or reactive references
        to dynamically update styles.

        Args:
            add (Union[str, dict[str, Any], TMaybeRef[str]]): The style(s) to apply. Can be:
                - A CSS string (e.g., "color: red;")
                - A dictionary mapping CSS properties to values (e.g., {"color": "red"})
                - A reactive reference to a string or dictionary for dynamic updates.

        Example:
        .. code-block:: python
            from instaui import ui, html

            # Apply static string style
            html.span("inline style").style("color: red;")

            # Apply dictionary style
            ref = ui.state("red")
            html.span("target").style({"color": ref})

            # Apply reactive string style
            style = ui.state("color: red;")
            html.span("target").style(style)
        """

        mark_as_used(add)

        if isinstance(add, str):
            self._style.update(self._parse_style(add))

        elif isinstance(add, dict):
            self._style.update(
                {
                    key: value
                    for key, value in add.items()
                    if not is_binding_tracker(value)
                }
            )
            self._style_dict_binds.update(
                {
                    key: mark_binding(value)
                    for key, value in add.items()
                    if is_binding_tracker(value)
                }
            )

        elif is_binding_tracker(add):
            self._style_str_binds.append(mark_binding(add))
            return self

        return self

    def props(self, add: Union[str, dict[str, Any], TMaybeRef]) -> Self:
        """
        Applies one or more HTML properties to the element. Supports constant values,
        string boolean attributes, reactive bindings, and dynamic evaluated props.

        Args:
            add (Union[str, dict[str, Any], TMaybeRef]):
                The property source to apply.
                - If a string, the property is treated as a boolean attribute (e.g., "disabled").
                - If a dict, key-value pairs are applied as element properties.
                - If a reactive reference (state), the property updates automatically
                when the referenced value changes.

        Example:
        .. code-block:: python
            from instaui import ui, html

            # Apply constant dictionary
            html.button("Submit").props({"disabled": True})

            # Apply boolean attribute using a string
            html.button("Click").props("disabled")

            # Bind reactive state to a property
            value = ui.state(True)
            html.checkbox(value)
            html.button("Submit").props({"disabled": value})

            # Apply dictionary state with multiple properties
            value = ui.state({"disabled": True})
            html.button("target").props(value)
        """

        mark_as_used(add)

        if isinstance(add, str):
            self._props.update(self._parse_props(add))

        elif is_binding_tracker(add):
            self._proxy_props.append(mark_binding(add))
            return self

        elif isinstance(add, dict):
            self._props.update(
                {
                    key: value
                    for key, value in add.items()
                    if (not is_binding_tracker(value)) and value is not None
                }
            )

            self._props_dict_binds.update(
                {
                    key: mark_binding(value)
                    for key, value in add.items()
                    if is_binding_tracker(value)
                }
            )

        return self

    @classmethod
    def default_classes(cls, add: str) -> type[Self]:
        cls._default_classes = cls._update_classes(cls._default_classes, add)
        return cls

    @classmethod
    def default_style(cls, add: Union[str, dict[str, str]]) -> type[Self]:
        new_style = cls._parse_style(add)
        cls._default_style.update(new_style)
        return cls

    @classmethod
    def default_props(cls, add: Union[str, dict[str, Any]]) -> type[Self]:
        new_props = cls._parse_props(add)
        cls._default_props.update(new_props)
        return cls

    def on(
        self,
        event_name: str,
        handler: EventMixin,
        *,
        extends: Optional[list] = None,
        modifier: Optional[list[TEventModifier]] = None,
    ):
        assert isinstance(handler, EventMixin), (
            "handler must be an instance of EventMixin"
        )

        event_name, real_modifier = event_modifier.parse_event_modifiers(
            event_name, modifier
        )

        self._events[event_name].append(
            handler._attach_to_element(extends=extends, modifier=real_modifier)
        )

        return self

    def directive(self, directive: Directive) -> Self:
        self._directives[directive] = None
        return self

    def display(self, value: TMaybeRef[bool]) -> Self:
        return self.directive(Directive(is_sys=False, name="vshow", value=value))

    def event_dataset(self, data: Any, name: str = "event-data") -> Self:
        from instaui.vars.js_computed import JsComputed

        value = JsComputed(inputs=[data], code="(data)=> JSON.stringify(data)")
        self.props({f"data-{name}": value})
        return self

    def element_ref(self, ref: ElementRef):
        """
        Associates an `ElementRef` with the component, allowing interaction with
        the underlying UI element from Python or through event callbacks.

        Args:
            ref (ElementRef): A reference object used to access or manipulate
                the rendered UI element programmatically.

        Example:
        .. code-block:: python
            from instaui import ui, html
            from custom import Counter

            cp = ui.element_ref()

            @ui.event(outputs=[cp])
            def on_click():
                return ui.run_element_method("reset")

            Counter().element_ref(cp)
            html.button("reset").on_click(on_click)
        """

        mark_as_used(ref)
        self.__element_ref = mark_binding(ref)
        return self

    def update_dependencies(
        self,
        *,
        css: Optional[Iterable[Path]] = None,
        externals: Optional[dict[str, Path]] = None,
        replace: bool = False,
    ):
        if not self.dependency:
            return

        app = get_app_slot()
        dep = self.dependency.copy()
        if replace:
            dep.css.clear()
            dep.externals.clear()

        if css:
            dep.css.update(css)

        if externals:
            dep.externals.update(externals)

        app.add_temp_component_dependency(dep)

    def use(self, *use_fns: Callable[[Self], None]) -> Self:
        """Use functions to the component object.

        Args:
            use_fns (Callable[[Self], None]): The list of use functions.

        Examples:
        .. code-block:: python
            def use_red_color(element: html.paragraph):
                element.style('color: red')

            html.paragraph('Hello').use(use_red_color)
        """

        for fn in use_fns:
            fn(self)
        return self

    @classmethod
    def use_init(cls, init_fn: Callable[[type[Self]], Self]) -> Self:
        """Use this method to initialize the component.

        Args:
            init_fn (Callable[[type[Self]], Self]): The initialization function.

        Examples:
        .. code-block:: python
            def fack_init(cls: type[html.table]) -> html.table:
                return cls(columns=['name', 'age'],rows = [{'name': 'Alice', 'age': 25}, {'name': 'Bob', 'age': 30}])

            ui.table.use_init(fack_init)
        """
        return init_fn(cls)

    def _to_json_dict(self):
        data = super()._to_json_dict()

        if self._style:
            data["style"] = self._style

        if self._style_dict_binds:
            data["dStyle"] = self._style_dict_binds

        if self._style_str_binds:
            data["sStyle"] = self._style_str_binds

        if self._str_classes or self._dict_classes or self._bind_str_classes:
            data["classes"] = _normalize_classes_data(
                self._str_classes, self._dict_classes, self._bind_str_classes
            )

        if self._props:
            data["props"] = self._props

        if self._props_dict_binds:
            data["bProps"] = self._props_dict_binds

        if self._proxy_props:
            data["proxyProps"] = self._proxy_props

        if self._events:
            data["events"] = _normalize_events(self._events)

        if self._slot_manager.has_slot():
            data["slots"] = self._slot_manager

        if self._directives:
            data["dir"] = list(self._directives.keys())

        if self.dependency:
            app_slot = get_app_slot()
            tag_name = self.dependency.tag_name
            app_slot.use_component_dependency(
                app_slot.get_temp_component_dependency(tag_name, self.dependency)
            )

        if self.__element_ref:
            data["eRef"] = self.__element_ref

        return data


def _normalize_events(
    events: defaultdict[str, list[dict]],
):
    return [
        (_normalize_event_name(name), event)
        for name, event_list in events.items()
        for event in event_list
    ]


def _normalize_event_name(event_name: str):
    """'click' -> 'onClick' , 'press-enter' -> 'onPressEnter' , 'pressEnter' -> 'onPressEnter'"""

    if event_name.startswith("on-"):
        event_name = event_name[3:]

    if event_name.startswith("on"):
        event_name = event_name[2:]

    parts = event_name.split("-")
    formatted_parts = [part[0].upper() + part[1:] for part in parts]

    return "".join(["on", *formatted_parts])


def _normalize_classes_data(
    str_classes: list[str],
    dict_classes: dict[str, dict],
    bind_str_classes: list[dict],
):
    _str_result = " ".join(str_classes)

    if dict_classes or bind_str_classes:
        result = {}

        if _str_result:
            result["str"] = _str_result

        if dict_classes:
            result["map"] = dict_classes

        if bind_str_classes:
            result["bind"] = bind_str_classes

        return result
    else:
        return _str_result


def _make_dependency_path(path: Union[str, Path], cls: type):
    if isinstance(path, str):
        path = Path(path)

    if not path.is_absolute():
        path = Path(inspect.getfile(cls)).parent / path

    return path
