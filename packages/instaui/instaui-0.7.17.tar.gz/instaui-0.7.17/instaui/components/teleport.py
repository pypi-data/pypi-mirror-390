from instaui.components.element import Element
from instaui.vars.types import TMaybeRef


def teleport(
    to: TMaybeRef[str],
    *,
    defer: bool = True,
    disabled: TMaybeRef[bool] = False,
):
    """
    Teleports UI elements to a target container, allowing dynamic repositioning
    within the page layout.

    Args:
        to (TMaybeRef[str]): The CSS selector or reactive reference specifying
                            the target container where the content should be moved.
        defer (bool, optional): Whether to defer the teleportation until the
                                next render cycle. Defaults to True.
        disabled (TMaybeRef[bool], optional): A flag or reactive reference to
                                            conditionally disable teleportation.
                                            Defaults to False.

    Example:
    .. code-block:: python
        from instaui import ui, html

        # Basic teleport to a target element
        with ui.column().classes("target-box"):
            ui.content("Container")

        with ui.teleport(".target-box"):
            ui.text("Teleported content")

        # Dynamic teleport with reactive target
        target = ui.state(".box1")
        with ui.teleport(to=target):
            ui.text("Dynamic content")

        # Disabled teleport
        disabled = ui.state(False)
        with ui.teleport(".target", disabled=disabled):
            ui.text("Conditionally teleported")
    """

    ele = Element(tag="teleport")
    ele.props({"to": to})

    if defer is not True:
        ele.props({"defer": False})

    if disabled is not False:
        ele.props({"disabled": disabled})

    return ele
