from __future__ import annotations
from typing import Any, Literal, Optional, Protocol
from typing_extensions import TypedDict
from tempfile import SpooledTemporaryFile


class UploadFileProtocol(Protocol):
    @property
    def file(self) -> SpooledTemporaryFile:
        """
        Gets the underlying spooled temporary file object.

        Returns:
            SpooledTemporaryFile: The temporary file object containing uploaded data.
        """
        ...

    @property
    def filename(self) -> str:
        """
        Gets the original filename of the uploaded file.
        e.g. "example.txt"

        Returns:
            str: The name of the uploaded file as provided during upload.
        """
        ...

    async def read(self, size: int = -1) -> bytes:
        """
        Reads data from the uploaded file.

        Args:
            size (int): Number of bytes to read. Defaults to -1 (read until EOF).

        Returns:
            bytes: The bytes read from the file.
        """
        ...

    async def write(self, data: bytes):
        """
        Writes data to the uploaded file.

        Args:
            data (bytes): The bytes to write to the file.
        """
        ...

    async def close(self):
        """
        Closes the uploaded file and releases any associated resources.

        Should be called when file processing is complete to ensure proper cleanup.
        """
        ...

    async def seek(self, offset: int) -> int:
        """
        Moves the file pointer to the specified position.

        Args:
            offset (int): The byte offset to seek to.

        Returns:
            int: The new absolute file position.
        """
        ...


class UploadFileResult(TypedDict, total=False):
    error: Optional[str]
    url: Optional[str]
    status: Optional[Literal[200, 400, 500]]
    files: Optional[list[str]]
    extra: Optional[dict[str, Any]]
