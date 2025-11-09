from typing import Optional
from instaui import custom
from instaui.event.event_mixin import EventMixin
from instaui.event.event_modifier import TEventModifier


class LazyRender(custom.element):
    def __init__(
        self,
        *,
        height: Optional[str] = None,
        destroy_on_leave: Optional[bool] = None,
        margin: Optional[str] = None,
        root: Optional[str] = None,
        disable: Optional[bool] = None,
    ):
        """
        Represents a lazy rendering container that defers rendering of its content until it becomes visible in the viewport.

        Args:
            height (Optional[str]): The CSS height of the container when content is not yet rendered.
                                    Defaults to "200px" if not specified.
            destroy_on_leave (Optional[bool]): Whether to destroy the rendered content when it leaves the viewport.
                                            Defaults to True.
            margin (Optional[str]): The margin around the root intersection observer area, specified as a CSS string
                                    (e.g., "100px 0px"). Defaults to "0px".
            root (Optional[str]): A CSS selector string specifying the root element for the IntersectionObserver.
                                If not provided, the browser viewport is used as the root.
            disable (Optional[bool]): If True, disables lazy rendering behavior and renders content immediately.
                                    Defaults to False.

        Example:
        .. code-block:: python
            with ui.lazy_render():
                ui.text("This content will be rendered only when it becomes visible in the viewport.")
        """
        super().__init__("lazy-render")
        custom.configure_slot_without_slot_prop(self, slot_names=["default", "hidden"])

        self.props(
            {
                "height": height,
                "destroyOnLeave": destroy_on_leave,
                "margin": margin,
                "root": root,
                "disable": disable,
            }
        )

    def hidden_slot(self):
        """
        Provides access to the 'hidden' slot, which displays content while the main content is not yet rendered
        or has been destroyed due to leaving the viewport.

        Returns:
            The slot context manager for the 'hidden' slot.

        Example:
        .. code-block:: python
            with ui.lazy_render() as lr:
                ui.text("Main content")
            with lr.hidden_slot():
                ui.text("Placeholder shown before main content is rendered")
        """
        return self.add_slot("hidden")

    def on_visibility(
        self,
        handler: EventMixin,
        *,
        extends: Optional[list] = None,
        modifier: Optional[list[TEventModifier]] = None,
    ):
        """
        Registers an event handler that is triggered when the visibility state of the lazy-rendered content changes.

        Args:
            handler (EventMixin): The event handler function to call when visibility changes.
                                It receives a boolean indicating whether the content is now visible.
            extends (Optional[list]): Additional event data to extend the payload.
            modifier (Optional[list[TEventModifier]]): List of event modifiers (e.g., prevent_default, stop_propagation).

        Example:
        .. code-block:: python
            @ui.event(inputs=[ui.event_context.e()])
            def visibility_changed(visible: bool):
                print(f"Content is now {'visible' if visible else 'hidden'}")

            with ui.lazy_render().on_visibility(visibility_changed):
                ui.text("Content")
        """
        return self.on("visibility", handler, extends=extends, modifier=modifier)
