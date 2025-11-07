from typing import ClassVar
from typing_extensions import Self
from contextvars import ContextVar


class PageState:
    """
    Returns the current PageState instance for this subclass, creating one if it does not yet exist.
    This ensures each page request has an isolated state container via a ContextVar.

    Args:
        cls (type): The subclass of PageState requesting its context-bound instance.

    Returns:
        Self: The existing or newly created PageState instance associated with the current context.

    Example:
    .. code-block:: python
        class MyState(PageState):
            def __init__(self):
                self.a1 = ui.state("foo")

        # Retrieve the state instance for the current page context
        my_state = MyState.get()
        value = my_state.a1
    """

    _ctx: ClassVar[ContextVar["PageState"]]

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls._ctx = ContextVar(f"{cls.__name__}_ctx")

    @classmethod
    def get(cls) -> Self:
        inst = cls._ctx.get(None)

        if inst is None:
            inst = cls()
            cls._ctx.set(inst)
        return inst  # type: ignore
