from typing import Optional, Final
from instaui.zero.options import CdnResourceOption

_M_VUE_CDN: Final = (
    "https://cdn.jsdelivr.net/npm/vue@3.5.21/dist/vue.esm-browser.prod.js"
)


def override(
    *, vue: Optional[str] = None, instaui: Optional[str] = None
) -> CdnResourceOption:
    """
    Configures overrides for CDN resource URLs, allowing custom external dependencies.

    Args:
        vue (Optional[str]): The custom CDN URL for the Vue library. If provided,
                             it replaces the default Vue runtime URL in the generated HTML.
        instaui (Optional[str]): The custom CDN URL for the InstaUI library. If provided,
                                 it replaces the default InstaUI library URL in the generated HTML.

    # Example:
    .. code-block:: python
        from instaui import ui, zero, cdn

        def page():
            ui.text("Hello")

        options = cdn.override(vue="https://cdn.example.com/vue.js")
        # options = cdn.override() # or use the default CDN URL
        html_str = zero(cdn_resource_overrides=options).to_html_str(page)
    """
    if not vue:
        return default_override()

    return CdnResourceOption(
        import_maps={k: v for k, v in {"vue": vue, "instaui": instaui}.items() if v},
    )


def default_override() -> CdnResourceOption:
    return override(vue=_M_VUE_CDN)
