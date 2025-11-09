from abc import ABC, abstractmethod


class PathableMixin(ABC):
    @abstractmethod
    def not_(self) -> bool:
        pass

    @abstractmethod
    def len_(self) -> int:
        pass
