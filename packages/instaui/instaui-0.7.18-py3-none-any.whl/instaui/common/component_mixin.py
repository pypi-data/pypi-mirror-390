from abc import ABC, abstractmethod


class ComponentMixin(ABC):
    pass


class ContainerMixin(ABC):
    @abstractmethod
    def add_item(self, item: ComponentMixin):
        pass
