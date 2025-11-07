from __future__ import annotations
from typing import (
    Optional,
    Union,
)
from instaui.components.value_element import ValueElement
from instaui.components.element import Element
from instaui.event.event_mixin import EventMixin
from instaui.event.event_modifier import TEventModifier
from instaui.vars.types import TMaybeRef
from instaui.components.vfor import VFor
from instaui.components.mixins import CanDisabledMixin

_T_Select_Value = Union[list[str], str]


class Select(CanDisabledMixin, ValueElement[Union[list[str], str]]):
    def __init__(
        self,
        value: Union[_T_Select_Value, TMaybeRef[_T_Select_Value], None] = None,
        *,
        model_value: Union[str, TMaybeRef[str], None] = None,
    ):
        """
        A dropdown select component for HTML-based UIs.

        Args:
            value (Union[_T_Select_Value, TMaybeRef[_T_Select_Value], None]): The initial selected value(s).
            model_value (Union[str, TMaybeRef[str], None]): Reactive model binding for the selected value.
                                                          If provided, overrides the `value` prop.

        # Example:
        .. code-block:: python
            from instaui import html

            # Basic usage
            with html.select(value="foo"):
                html.option(text="foo", value="foo")
                html.option(text="bar", value="bar")

            # Using from_list for simple options
            html.select.from_list(["foo", "bar"], value="foo")

            # Using from_records for structured data
            html.select.from_records(
                [{"value": "1", "text": "One"}, {"value": "2", "text": "Two"}],
                value="1"
            )
        """

        super().__init__("select", value, is_html_component=True)

        if model_value is not None:
            self.props({"value": model_value})

    def on_change(
        self,
        handler: EventMixin,
        *,
        extends: Optional[list] = None,
        modifier: Optional[list[TEventModifier]] = None,
    ):
        """
        Registers an event handler for the 'change' event.

        Args:
            handler (EventMixin): The function or callable to execute when selection changes.

        """
        self.on("change", handler, extends=extends, modifier=modifier)
        return self

    @classmethod
    def from_list(
        cls,
        options: list,
        value: Union[_T_Select_Value, None] = None,
        *,
        model_value: Union[str, TMaybeRef[str], None] = None,
    ) -> Select:
        """
        Creates a Select from a simple list of string options.

        Args:
            options (list): List of strings used as both text and value for each option.
            value (Union[_T_Select_Value, None]): The initially selected value.
            model_value (Union[str, TMaybeRef[str], None]): Reactive model binding for the selected value.

        """

        with cls(value, model_value=model_value) as select:
            with VFor(options) as item:
                Select.Option(text=item, value=item)

        return select

    @classmethod
    def from_records(
        cls,
        options: list[dict],
        value: Union[_T_Select_Value, TMaybeRef[_T_Select_Value], None] = None,
        *,
        model_value: Union[str, TMaybeRef[str], None] = None,
    ) -> Select:
        """
        Creates a Select from a list of dictionaries with 'text' and 'value' keys.

        Args:
            options (list[dict]): List of dicts containing 'text' (display) and 'value' (data) fields.
            value (Union[_T_Select_Value, TMaybeRef[_T_Select_Value], None]): The initially selected value.
            model_value (Union[str, TMaybeRef[str], None]): Reactive model binding for the selected value.

        """
        with cls(value, model_value=model_value) as select:
            with VFor(options) as item:
                Select.Option(text=item["text"], value=item["value"])

        return select

    class Option(Element, CanDisabledMixin):
        def __init__(
            self,
            *,
            text: Optional[str] = None,
            value: Optional[str] = None,
            disabled: Optional[bool] = None,
        ):
            """
            Represents an individual option within a Select component.

            Args:
                text (Optional[str]): Display text for the option.
                value (Optional[str]): Value associated with the option (submitted with form).
                disabled (Optional[bool]): Whether the option is disabled for selection.
            """
            super().__init__("option")

            self.props({"value": value, "disabled": disabled, "text": text})
