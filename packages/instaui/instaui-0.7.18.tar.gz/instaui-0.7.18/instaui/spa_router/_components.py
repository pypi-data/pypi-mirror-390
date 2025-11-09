from __future__ import annotations
import typing
from instaui import html
from instaui.components.element import Element
from instaui.vars.types import TMaybeRef


class RouterLink(Element):
    def __init__(self, text: TMaybeRef[str], *, to: str):
        """
        Represents a navigational link element in a SPA (Single Page Application) that allows users
        to navigate between different routes without a full page reload.

        Args:
            text (TMaybeRef[str]): The display text of the link. Can be a static string or a reactive reference.
            to (str): The target route path that the link navigates to when clicked.


        Example:
        .. code-block:: python
            from instaui import html, spa_router, ui

            @ui.page()
            def index():
                # Basic route registration
                def home():
                    html.paragraph("hello home")

                def user_page():
                    name = spa_router.get_params("name")
                    html.paragraph(ui.str_format("welcome: {name}", name=name))

                # Add routes with different configurations
                spa_router.add_route(home)
                spa_router.add_route(user_page, path="/user/:name")

                # ui
                with ui.row():
                    spa_router.link("home page", to="/")
                    spa_router.link("user page", to="/user/foo")
                    spa_router.link("user page", to="/user/bar")
        """

        super().__init__("router-link")

        self.props({"to": to})

        if text is not None:
            with self.add_slot("default"):
                html.span(text)

    @classmethod
    def by_name(
        cls,
        text: TMaybeRef[str],
        *,
        name: str,
        params: typing.Optional[dict[str, typing.Any]] = None,
    ) -> RouterLink:
        to: dict = {"name": name}
        if params:
            to["params"] = params

        return cls(text, to=to)  # type: ignore


class RouterView(Element):
    def __init__(self):
        """
        Container element that displays the current route component in SPA routing.

        The router view acts as a dynamic container that automatically renders the component
        associated with the current route. It updates when navigation occurs via links or
        programmatic routing, providing the main content area for single-page applications.

        Example:
        .. code-block:: python
            from instaui import html, spa_router, ui

            @ui.page()
            def index():
                # Basic route registration
                def home():
                    html.paragraph("hello home")

                def user_page():
                    name = spa_router.get_params("name")
                    html.paragraph(ui.str_format("welcome: {name}", name=name))

                # Add routes with different configurations
                spa_router.add_route(home)
                spa_router.add_route(user_page, path="/user/:name")

                # ui
                with ui.row():
                    spa_router.link("home page", to="/")
                    spa_router.link("user page", to="/user/foo")
                    spa_router.link("user page", to="/user/bar")
        """
        super().__init__("router-view")
