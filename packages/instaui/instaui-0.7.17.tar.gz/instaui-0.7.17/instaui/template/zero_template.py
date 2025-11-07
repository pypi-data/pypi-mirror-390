from __future__ import annotations
import typing
from pathlib import Path
from urllib.parse import quote
import base64
from dataclasses import dataclass, field
from .env import env
from instaui.common.jsonable import dumps
from instaui.runtime.dataclass import JsLink
from . import _utils

if typing.TYPE_CHECKING:
    from instaui.runtime.resource import StyleTag


_TCodeOrPath = typing.Union[str, Path]
_JS_PREFIX = "data:text/javascript;charset=utf-8"
_CSS_PREFIX = "data:text/css;charset=utf-8"
_ICON_PREFIX = "data:image/x-icon;base64"

_html_template = env.get_template("zero.html")


@dataclass(frozen=True)
class ZeroVueAppComponent:
    name: str
    url: _TCodeOrPath


@dataclass
class ZeroTemplateModel:
    version: str
    vue_js_code: _TCodeOrPath
    instaui_js_code: _TCodeOrPath
    config_dict: dict[str, typing.Any] = field(default_factory=dict)
    extra_import_maps: dict[str, _TCodeOrPath] = field(default_factory=dict)
    css_links: list[_TCodeOrPath] = field(default_factory=list)
    style_tags: list[StyleTag] = field(default_factory=list)
    js_links: list[JsLink] = field(default_factory=list)
    script_tags: list[str] = field(default_factory=list)
    vue_app_use: list[str] = field(default_factory=list)
    vue_app_component: list[ZeroVueAppComponent] = field(default_factory=list)
    prefix: str = ""
    title: typing.Optional[str] = None
    favicon: typing.Optional[Path] = None
    icons_svg_code: typing.Optional[str] = None
    import_maps_cdn_overrides: dict[str, str] = field(default_factory=dict)
    css_links_cdn_overrides: dict[Path, str] = field(default_factory=dict)

    def add_extra_import_map(self, name: str, url: _TCodeOrPath):
        self.extra_import_maps[name] = self.import_maps_cdn_overrides.get(name, url)

    def add_css_link(self, link: _TCodeOrPath):
        self.css_links.append(
            link
            if isinstance(link, str)
            else self.css_links_cdn_overrides.get(link, link)
        )

    @property
    def import_maps_records(self):
        return {
            **self.extra_import_maps,
            "vue": self.import_maps_cdn_overrides.get("vue", self.vue_js_code),
            "instaui": self.import_maps_cdn_overrides.get(
                "instaui", self.instaui_js_code
            ),
        }

    @property
    def import_maps_string(self):
        return dumps(self.import_maps_records)

    def normalize_path_with_self(self):
        self.vue_js_code = _normalize_path_to_dataurl_or_cdn(
            self.vue_js_code, _JS_PREFIX
        )

        self.instaui_js_code = _normalize_path_to_dataurl_or_cdn(
            self.instaui_js_code, _JS_PREFIX
        )

        self.css_links = [
            _normalize_path_to_dataurl_or_cdn(link, _CSS_PREFIX)
            for link in self.css_links
            if isinstance(link, str) or (isinstance(link, Path) and link.is_file())
        ]

        self.js_links = [
            JsLink(
                link=_normalize_path_to_dataurl_or_cdn(link.link, _JS_PREFIX),
                attrs=link.attrs,
            )
            for link in self.js_links
        ]

        self.extra_import_maps = {
            k: _normalize_path_to_dataurl_or_cdn(v, _JS_PREFIX)
            for k, v in self.extra_import_maps.items()
        }

        self.vue_app_component = [
            ZeroVueAppComponent(
                name=component.name,
                url=_normalize_path_to_dataurl_or_cdn(component.url, _JS_PREFIX),
            )
            for component in self.vue_app_component
        ]

        self.favicon = _normalize_path_to_base64_url(self.favicon, _ICON_PREFIX)  # type: ignore


def _normalize_path_to_dataurl_or_cdn(path: typing.Union[str, Path], prefix: str):
    if isinstance(path, Path):
        path = path.read_text(encoding="utf-8")

    return path if _utils.is_url(path) else f"{prefix},{quote(path)}"


def _normalize_path_to_base64_url(path: typing.Optional[Path], prefix: str):
    if path is None:
        return None
    return f"{prefix},{base64.b64encode(path.read_bytes()).decode('utf-8')}"


def render_zero_html(model: ZeroTemplateModel) -> str:
    model.normalize_path_with_self()
    return _html_template.render(model=model)
