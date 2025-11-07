from typing import Any
from instaui.vars.mixin_types.pathable import PathableMixin
from instaui.vars.types import TMaybeRef


def not_(value: TMaybeRef[bool]) -> bool:
    """
    Inverts the boolean value of the given value.

    Args:
        value (TMaybeRef[bool]): The value to invert.

    Example:
    .. code-block:: python
        value = ui.state(True)
        ui.text(ui.not_(value))  # False
    """

    if isinstance(value, PathableMixin):
        return value.not_()
    return not value


def len_(value: Any) -> int:
    """
    Returns the length of the given string value.

    Args:
        value (TMaybeRef[str]): The string value to get the length of.

    Example:
    .. code-block:: python
        value = ui.state("hello")
        ui.text(ui.len_(value))  # 5
    """
    if isinstance(value, PathableMixin):
        return value.len_()

    return len(value)
