from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class ZeroOptions:
    icons_svg_content: Optional[str] = None
    cdn_resource_options: Optional[list[CdnResourceOption]] = None

    def get_import_maps_cdn_overrides(self) -> dict[str, str]:
        if not self.cdn_resource_options:
            return {}

        return dict(
            item
            for option in self.cdn_resource_options
            for item in (option.import_maps or {}).items()
        )

    def get_css_links_cdn_overrides(self) -> dict[Path, str]:
        if not self.cdn_resource_options:
            return {}

        return dict(
            item
            for option in self.cdn_resource_options
            for item in (option.css_links or {}).items()
        )


@dataclass
class CdnResourceOption:
    import_maps: Optional[dict[str, str]] = None
    css_links: Optional[dict[Path, str]] = None
