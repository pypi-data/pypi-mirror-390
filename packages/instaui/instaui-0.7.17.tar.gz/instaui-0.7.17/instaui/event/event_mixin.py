from abc import ABC, abstractmethod
import typing

from instaui.event.event_modifier import TEventModifier


class EventMixin(ABC):
    @abstractmethod
    def event_type(self) -> typing.Literal["web", "js"]:
        pass

    @abstractmethod
    def _attach_to_element(
        self,
        *,
        extends: typing.Optional[typing.Sequence],
        modifier: typing.Optional[typing.Sequence[TEventModifier]],
    ) -> dict:
        pass
