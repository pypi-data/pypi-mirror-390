from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional
from instaui.runtime import get_app_slot


@dataclass(frozen=True)
class PluginDependencyInfo:
    name: str = field(hash=True)
    esm: Path = field(hash=False)
    externals: dict[str, Path] = field(default_factory=dict, compare=False, hash=False)
    css: list[Path] = field(default_factory=list, compare=False, hash=False)


def register_plugin(
    name: str,
    esm: Path,
    *,
    externals: Optional[dict[str, Path]] = None,
    css: Optional[list[Path]] = None,
):
    info = PluginDependencyInfo(f"plugin/{name}", esm, externals or {}, css or [])

    get_app_slot().use_plugin_dependency(info)
    return info
