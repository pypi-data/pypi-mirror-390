from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Optional, Union
from contextvars import copy_context
from instaui.runtime import new_app_slot, reset_app_slot
from instaui.systems import file_path_system
from instaui.runtime.utils import init_base_scope
from .func import to_html, to_html_str, get_template_model
from instaui.template.zero_template import ZeroTemplateModel
from instaui.launch_collector import get_launch_collector
from .options import ZeroOptions, CdnResourceOption


class ZeroCaller:
    def __init__(
        self,
        *,
        icons_svg_path: Optional[
            Union[str, Path, Callable[[], Union[str, Path]]]
        ] = None,
        cdn_resource_overrides: Optional[
            Union[list[CdnResourceOption], CdnResourceOption]
        ] = None,
    ):
        """
        Initializes a configuration object for generating static HTML files with customizable assets.

        Args:
            icons_svg_path (Optional[Union[str, Path, Callable[[], Union[str, Path]]]]):
                Specifies the path to the SVG icon file used across the page.
                Can be a string or Path object representing a file path (relative or absolute),
                or a callable that returns such a path or the SVG content directly.
            cdn_resource_overrides (Optional[Union[list[CdnResourceOption], CdnResourceOption]]):
                Configuration(s) for overriding default CDN URLs of external resources.
                Can be a single CdnResourceOption or a list of them, created via cdn.override().

        # Example:
        .. code-block:: python
            from instaui import ui, zero, cdn

            # Custom SVG icons and CDN override
            config = zero(
                icons_svg_path="assets/icons/custom.svg",
                cdn_resource_overrides= cdn.override(vue='https://cdn.example.com/vue.js'),
            )
            config.to_html(lambda: ui.text("Hello"), file="index.html")
        """
        icons_svg_content = None

        if icons_svg_path is not None:
            if callable(icons_svg_path):
                icons_svg_path = icons_svg_path()
                icons_svg_content = (
                    icons_svg_path
                    if isinstance(icons_svg_path, str)
                    else icons_svg_path.read_text(encoding="utf-8")
                )
            else:
                icons_svg_path = file_path_system.get_caller_path(icons_svg_path)
                icons_svg_content = icons_svg_path.read_text(encoding="utf-8")

        self._options = ZeroOptions(
            icons_svg_content=icons_svg_content,
            cdn_resource_options=cdn_resource_overrides
            if isinstance(cdn_resource_overrides, list)
            else [cdn_resource_overrides]
            if cdn_resource_overrides is not None
            else None,
        )

    def to_html(self, render_fn: Callable[..., Any], *, file: Union[str, Path]):
        """
        Generates a static HTML file by rendering the provided function.

        Args:
            render_fn (Callable[..., Any]): A callable that defines the content to be rendered into HTML.
                                        This function typically contains UI component calls.
            file (Union[str, Path]): The output path where the generated HTML file will be saved.
                                    Can be a string or a Path object.

        # Example:
        .. code-block:: python
            from instaui import ui, zero

            def page():
                ui.text("Hello, World!")

            zero().to_html(page, file="output.html")
        """
        file = file_path_system.get_caller_path(file)

        with _run():
            copy_context().run(render_fn)
            return to_html(file, options=self._options)

    def to_html_str(self, render_fn: Callable[..., Any]):
        """
        Generates a static HTML file content string by rendering the provided function.

        Args:
            render_fn (Callable[..., Any]): A function that defines the UI content by calling UI components.
                                            It is executed to capture the view structure for static rendering.

        # Example:
        .. code-block:: python
            from instaui import ui, zero

            def page():
                ui.text("Hello, World!")

            html_str = zero().to_html_str(page)
        """
        with _run():
            copy_context().run(render_fn)
            return to_html_str(self._options)

    def to_debug_report(self, render_fn: Callable[..., Any], *, file: Union[str, Path]):
        """
        Generates a debug report for the static HTML output, including file size and resource usage analysis.

        Args:
            render_fn (Callable[..., Any]): A function that defines the UI content by calling UI components.
                                            It is used to generate the HTML for analysis.
            file (Union[str, Path]): The output file path where the debug report will be saved.

        # Example:
        .. code-block:: python
            from instaui import ui, zero

            def page():
                ui.text("Hello, World!")

            zero().to_debug_report(page, file="debug_report.html")
        """
        file = file_path_system.get_caller_path(file)

        # Custom component dependencies must be recorded only during actual execution
        with _run():
            copy_context().run(render_fn)
            result_html_str = to_html_str(self._options)

            model = get_template_model(self._options)

        with _run():
            copy_context().run(lambda: _create_debug_report(model, result_html_str))

            to_html(
                file.resolve().absolute(),
                options=ZeroOptions(),
            )


@contextmanager
def _run():
    app, app_token = new_app_slot("zero")
    init_base_scope(app)

    _events = [iter(event()) for event in get_launch_collector().page_init_lifespans]
    for event in _events:
        next(event)

    yield

    for event in _events:
        try:
            next(event)
        except StopIteration:
            pass

    assert app_token is not None
    reset_app_slot(app_token)


def _create_debug_report(model: ZeroTemplateModel, result_html_str: str):
    from instaui import ui, html

    no_exists_path_class = "ex-no-exists-path"

    def _path_exists_class(path: Union[str, Path]):
        if isinstance(path, str):
            return ""
        return "" if path.exists() else no_exists_path_class

    def _try_get_file_size_mb(path: Union[str, Path]):
        if isinstance(path, str):
            return None

        return f"{round(path.stat().st_size / 1024 / 1024, 2)} MB"

    ui.use_tailwind()

    ui.add_style(rf".{no_exists_path_class} {{background-color: red;color: white;}}")

    html_size = len(result_html_str.encode("utf-8")) / 1024 / 1024

    box_style = "border-2 border-gray-200 p-4 place-center gap-x-4"

    with ui.column().classes("gap-2"):
        # base info
        with ui.grid(columns="auto 1fr").classes(box_style):
            html.span("file size:")
            html.span(f"{html_size:.2f} MB")

        # import maps
        ui.heading("import maps")

        with ui.grid(columns="auto auto auto").classes(box_style):
            ui.text("name")
            ui.text("path or url")
            ui.text("size")

            ui.box(height="1px", width="100%", grid_column="1/-1").style(
                "border-top: 1px solid black;"
            )

            for name, url in model.import_maps_records.items():
                ui.text(name)
                ui.text(str(url) if isinstance(url, Path) else url)
                ui.text(_try_get_file_size_mb(url))

        # css links
        ui.heading("css links")

        with ui.grid(columns="1fr auto").classes(box_style):
            ui.text("path or url")
            ui.text("size")

            for link in model.css_links:
                html.span(str(link)).classes(_path_exists_class(link))
                ui.text(_try_get_file_size_mb(link))

        # js links
        ui.heading("js links")
        with ui.column().classes(box_style):
            for info in model.js_links:
                if isinstance(info.link, Path) and info.link.is_file():
                    html.span(str(info.link)).classes(_path_exists_class(info.link))

        # custom components
        ui.heading("custom components")
        with ui.grid(columns="auto 1fr").classes(box_style):
            html.span("name")
            html.span("js file path")

            for info in model.vue_app_component:
                html.span(info.name)

                if isinstance(info.url, Path) and info.url.is_file():
                    html.span(str(info.url)).classes(_path_exists_class(info.url))
                else:
                    html.span("not file")
