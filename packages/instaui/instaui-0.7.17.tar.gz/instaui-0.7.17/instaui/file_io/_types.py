from typing import Literal, TypedDict, Union

TDownloadModeStr = Literal["chunked", "standard", "auto"]
TSizeUnitStr = Literal["kb", "mb", "gb"]


class ChunkedDownloadModeConfig(TypedDict):
    chunk_size: int
    chunk_size_unit: TSizeUnitStr


class AutoDownloadModeConfig(TypedDict):
    chunk_size: int
    chunk_size_unit: TSizeUnitStr
    threshold_size: int
    threshold_size_unit: TSizeUnitStr


class PrepareDownloadResult(TypedDict):
    filename: str
    filepath: str
    filesize: int
    mode: TDownloadModeStr
    config: Union[ChunkedDownloadModeConfig, AutoDownloadModeConfig, None]
