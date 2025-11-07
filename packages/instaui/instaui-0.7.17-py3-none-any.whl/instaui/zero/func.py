from __future__ import annotations
import itertools
from pathlib import Path
from typing import Optional
from instaui.version import __version__ as _INSTA_VERSION
import instaui.consts as consts
from instaui.runtime import get_app_slot, get_default_app_slot
from instaui.template import render_zero_html
from instaui.template import zero_template
from instaui.html_tools import to_config_data
from instaui.runtime.dataclass import JsLink
from instaui.runtime.resource import HtmlResource, StyleTag
from .options import ZeroOptions


def to_html(
    file: Path,
    *,
    options: Optional[ZeroOptions] = None,
    use_empty_html_resource: bool = False,
):
    file = Path(file)

    raw = to_html_str(options, use_empty_html_resource)
    file.write_text(raw, "utf8")

    return file.resolve().absolute()


def get_template_model(options: ZeroOptions, use_empty_html_resource: bool = False):
    system_slot = get_app_slot()

    default_app_slot = get_default_app_slot()
    html_resource = system_slot._html_resource
    default_html_resource = (
        _empty_html_resource()
        if use_empty_html_resource
        else default_app_slot._html_resource
    )

    config_data = to_config_data()

    model = zero_template.ZeroTemplateModel(
        import_maps_cdn_overrides=options.get_import_maps_cdn_overrides(),
        css_links_cdn_overrides=options.get_css_links_cdn_overrides(),
        version=_INSTA_VERSION,
        icons_svg_code=options.icons_svg_content,
        vue_js_code=consts.VUE_ES_JS_PATH,
        instaui_js_code=consts.APP_ES_JS_PATH,
        css_links=[
            consts.APP_CSS_PATH,
        ],
        config_dict=config_data,
        favicon=html_resource.favicon
        or default_html_resource.favicon
        or consts.FAVICON_PATH,
        title=html_resource.title or default_html_resource.title or consts.PAGE_TITLE,
    )

    # register custom components
    for component in system_slot._component_dependencies:
        if not component.esm:
            continue

        model.vue_app_component.append(
            zero_template.ZeroVueAppComponent(
                name=component.tag_name,
                url=component.esm,
            )
        )

        if component.css:
            for css_link in component.css:
                model.add_css_link(css_link)

        if component.externals:
            for name, url in component.externals.items():
                if url.is_file():
                    model.add_extra_import_map(name, url)

    # register custom plugins
    for plugin in set(
        itertools.chain(
            system_slot._plugin_dependencies, default_app_slot._plugin_dependencies
        )
    ):
        if not plugin.esm:
            continue

        model.vue_app_use.append(plugin.name)

        model.add_extra_import_map(plugin.name, plugin.esm)

        for name, url in plugin.externals.items():
            model.add_extra_import_map(name, url)

        for css in plugin.css:
            model.add_css_link(css)

    # css file link to web static link
    for link in html_resource.get_valid_css_links(
        default_html_resource._css_links_manager
    ):
        if isinstance(link, Path):
            model.add_css_link(link)

    # js file link to web static link
    for info in html_resource.get_valid_js_links(
        default_html_resource._js_links_manager
    ):
        if isinstance(info.link, Path):
            model.js_links.append(JsLink(info.link))

    for js_code in itertools.chain(
        html_resource._script_tags, default_html_resource._script_tags
    ):
        model.script_tags.append(js_code)

    for sylte_tag in StyleTag.merge_by_group_id(
        itertools.chain(html_resource._style_tags, default_html_resource._style_tags)
    ):
        model.style_tags.append(sylte_tag)

    return model


def to_html_str(
    options: Optional[ZeroOptions] = None, use_empty_html_resource: bool = False
):
    model = get_template_model(options or ZeroOptions(), use_empty_html_resource)
    return render_zero_html(model)


def _empty_html_resource():
    return HtmlResource()
