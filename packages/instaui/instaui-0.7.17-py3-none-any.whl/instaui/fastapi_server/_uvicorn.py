from __future__ import annotations
from types import FrameType
import typing
import uvicorn
import socket
import logging

logger = logging.getLogger(__name__)
ThandleExitCallbacks = list[typing.Callable[[], typing.Any]]


class UvicornServer(uvicorn.Server):
    _instance: UvicornServer

    def __init__(self, config: uvicorn.Config) -> None:
        super().__init__(config)
        self._handle_exit_callbacks: ThandleExitCallbacks = []

    @classmethod
    def get_instance(cls) -> UvicornServer:
        if not hasattr(cls, "_instance"):
            raise RuntimeError("UvicornServer singleton not created")
        return cls._instance

    @classmethod
    def create_singleton(
        cls, config: uvicorn.Config, handle_exit_callbacks: ThandleExitCallbacks
    ) -> None:
        cls._instance = cls(config=config)
        for callback in handle_exit_callbacks:
            cls._instance.on_handle_exit(callback)

    def run(self, sockets: typing.Optional[list[socket.socket]] = None) -> None:
        self._instance = self
        super().run()

    def on_handle_exit(self, callback: typing.Callable[[], typing.Any]):
        self._handle_exit_callbacks.append(callback)

    def handle_exit(self, sig: int, frame: FrameType | None) -> None:
        for callback in self._handle_exit_callbacks:
            try:
                callback()
            except Exception as e:
                logger.exception("Exception in handle_exit callback: %s", e)
        return super().handle_exit(sig, frame)
