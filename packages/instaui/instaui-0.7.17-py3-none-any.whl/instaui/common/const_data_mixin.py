from abc import ABC, abstractmethod
from typing import Any


class ConstDataMixin(ABC):
    @abstractmethod
    def get_value(self) -> Any:
        pass
