import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Union, Literal, cast
from instaui.common.jsonable import Jsonable
from instaui.vars._types import OutputSetType
from instaui.vars.mixin_types.py_binding import CanOutputMixin
from instaui.vars.js_computed import js_computed

from . import _types


@dataclass
class DownloadModeConfig:
    """Configuration for download modes."""

    mode: str
    chunk_size: int = 10
    chunk_size_unit: _types.TSizeUnitStr = "mb"
    threshold_size: Optional[int] = None
    threshold_size_unit: Optional[_types.TSizeUnitStr] = None


class DownloadMode:
    """Download mode configuration factory."""

    @staticmethod
    def chunked(
        chunk_size: int = 10, chunk_size_unit: _types.TSizeUnitStr = "mb"
    ) -> DownloadModeConfig:
        """Configure chunked download mode.

        Args:
            chunk_size: Size of each chunk (default: 10)
            chunk_size_unit: Unit for chunk size (default: "mb")
        """
        return DownloadModeConfig(
            mode="chunked", chunk_size=chunk_size, chunk_size_unit=chunk_size_unit
        )

    @staticmethod
    def auto(
        threshold_size: int = 100,
        threshold_size_unit: Literal["kb", "mb", "gb"] = "mb",
        chunk_size: int = 10,
        chunk_size_unit: Literal["kb", "mb", "gb"] = "mb",
    ) -> DownloadModeConfig:
        """Configure auto download mode.

        Args:
            threshold_size: Threshold for using chunked download (default: 100)
            threshold_size_unit: Unit for threshold size (default: "mb")
            chunk_size: Size of each chunk when using chunked download (default: 10)
            chunk_size_unit: Unit for chunk size (default: "mb")
        """
        return DownloadModeConfig(
            mode="auto",
            chunk_size=chunk_size,
            chunk_size_unit=chunk_size_unit,
            threshold_size=threshold_size,
            threshold_size_unit=threshold_size_unit,
        )


class DownloadFileBindingOutput(Jsonable, CanOutputMixin):
    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.FileDownload


class DownloadFile:
    """
    Provides utilities for file download operations in web applications.

    This class contains static methods to prepare and trigger file downloads
    through both Python and JavaScript event handlers.

    Example:
    .. code-block:: python
        from pathlib import Path
        from instaui import ui, html, file_io

        @ui.page()
        def index():
            @ui.event(outputs=[file_io.download_file.output()])
            def download():
                return file_io.download_file.prepare_download(Path("/path/to/file.txt"))

            html.button("download").on_click(download)
    """

    @staticmethod
    def output() -> DownloadFileBindingOutput:
        """
        Creates an output binding for file download events.

        Returns:
            DownloadFileBindingOutput: An output target that can be used in
                event handlers to trigger file downloads.
        """
        return DownloadFileBindingOutput()

    @staticmethod
    def prepare_download(
        file_path: Union[str, Path],
        *,
        file_name: Optional[str] = None,
        download_mode: Union[_types.TDownloadModeStr, DownloadModeConfig] = "auto",
    ) -> _types.PrepareDownloadResult:
        """
        Prepares file metadata for download operations.

        Args:
            file_path (Union[str, Path]): Path to the file to be downloaded.
            file_name (Optional[str]): Custom filename for the download.
                If not provided, uses the original filename from the file path.
            download_mode: Download mode configuration. Can be:
                - "chunked": Large file chunked download (default settings)
                - "standard": Regular download
                - "auto": Auto-select (prefer chunked, fallback to standard)
                - DownloadMode.chunked(): Configured chunked download
                - DownloadMode.auto(): Configured auto download mode
                Defaults to "auto".

        Returns:
            dict: A dictionary containing:
                - filename: The download filename
                - filepath: The file path
                - download_mode: The selected download mode
                - config: Additional configuration when applicable

        Examples:
        .. code-block:: python
            # Simple usage with string mode
            prepare_download(..., download_mode="chunked")

            # Configured chunked download
            prepare_download(..., download_mode=DownloadMode.chunked(
                chunk_size=20,
                chunk_size_unit="mb"
            ))

            # Configured auto mode
            prepare_download(..., download_mode=DownloadMode.auto(
                threshold_size=200,
                threshold_size_unit="mb",
                chunk_size=20,
                chunk_size_unit="mb"
            ))
        """
        org_path = Path(file_path)
        file_path_str = (
            _relative_path(Path.cwd(), org_path)
            if isinstance(file_path, str)
            else str(org_path.absolute())
        )
        file_name = file_name or org_path.name

        if isinstance(download_mode, str):
            if download_mode == "standard":
                download_config = {"mode": download_mode, "config": None}
            elif download_mode == "chunked":
                download_config = {
                    "mode": download_mode,
                    "config": DownloadMode.chunked().__dict__,
                }
            elif download_mode == "auto":
                download_config = {
                    "mode": download_mode,
                    "config": DownloadMode.auto().__dict__,
                }
            else:
                download_config = {"mode": download_mode, "config": None}
        else:
            download_config = {
                "mode": download_mode.mode,
                "config": {
                    "chunk_size": download_mode.chunk_size,
                    "chunk_size_unit": download_mode.chunk_size_unit,
                    **(
                        {
                            "threshold_size": download_mode.threshold_size,
                            "threshold_size_unit": download_mode.threshold_size_unit,
                        }
                        if download_mode.threshold_size is not None
                        else {}
                    ),
                },
            }

        return cast(
            _types.PrepareDownloadResult,
            {
                "filename": file_name,
                "filepath": file_path_str,
                "filesize": os.path.getsize(file_path_str),  # bytes
                **download_config,
            },
        )

    @staticmethod
    def js_fn_input(file_path: Union[str, Path], *, file_name: Optional[str] = None):
        """
        Creates a JavaScript-compatible input for file download operations.

        Args:
            file_path (Union[str, Path]): Path to the file to be downloaded.
            file_name (Optional[str]): Custom filename for the download.
                If not provided, uses the original filename from the file path.

        Returns:
            A computed JavaScript function that returns file metadata when called.

        Example:
        .. code-block:: python
            from pathlib import Path
            from instaui import ui, html, file_io

            @ui.page()
            def index():
                download = ui.js_event(
                    inputs=[file_io.download_file.js_fn_input(Path("/path/to/file.txt"))],
                    outputs=[file_io.download_file.output()],
                    code='fn=> fn()',
                )

                html.button("download").on_click(download)
        """
        args = DownloadFile.prepare_download(file_path, file_name=file_name)
        return js_computed(inputs=[args], code=r"(args)=> ()=> args")


def _relative_path(base_dir: Path, file_path: Path):
    try:
        relative_path = file_path.relative_to(base_dir)
    except ValueError:
        relative_path = Path(os.path.relpath(file_path, base_dir))

    return str(relative_path)
