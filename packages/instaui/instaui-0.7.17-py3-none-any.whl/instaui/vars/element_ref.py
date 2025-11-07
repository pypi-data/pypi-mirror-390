from __future__ import annotations
from typing import TYPE_CHECKING
from instaui.common.binding_track_mixin import BindingTrackerHelper, BindingTrackerMixin
from instaui.common.jsonable import Jsonable
from instaui.common.var_track_mixin import VarTrackerHelper, VarTrackerMixin
from instaui.runtime import try_new_scope_on_ui_state
from instaui.vars._types import InputBindingType, OutputSetType
from instaui.vars.mixin_types.observable import ObservableMixin
from instaui.vars.mixin_types.py_binding import CanOutputMixin, CanInputMixin
from instaui.vars.mixin_types.element_binding import ElementBindingMixin

if TYPE_CHECKING:
    from instaui.runtime.scope import Scope


class ElementRef(
    Jsonable,
    CanOutputMixin,
    CanInputMixin,
    ElementBindingMixin,
    BindingTrackerMixin,
    ObservableMixin,
    VarTrackerMixin,
):
    def __init__(self) -> None:
        """
        A reference holder for a frontend DOM element, enabling two-way interaction between
        Python and JavaScript. The referenced element can be used as input/output in JS
        events, and methods can be executed dynamically on the element at runtime.

        Args:
            None: The reference is created without initialization parameters. It will be
                bound to an element using ``element_ref(...)`` during UI construction.

        Example:
        .. code-block:: python
            # 1️ Use ElementRef inside ui.event as an output
            cp = ui.element_ref()

            @ui.event(outputs=[cp])
            def on_click():
                return ui.run_element_method("reset")

            Counter("my counter").element_ref(cp)
            html.button("reset").on_click(on_click)


            # 2️⃣ Use ElementRef as input to ui.js_event
            ele = ui.element_ref()
            click_event = ui.js_event(inputs=[ele], code="(ele)=> ele.increment()")

            CounterWithRefInput().element_ref(ele)
            html.button("click").on_click(click_event)


            # 3️⃣ Access DOM element inside JavaScript event using `ele.$el ?? ele`
            ele_dom = ui.element_ref()
            output = ui.state("")

            ui.text("custom").element_ref(ele_dom).on(
                "click",
                ui.js_event(
                    inputs=[ele_dom],
                    outputs=[output],
                    code="ele => (ele.$el ?? ele).tagName"
                ),
            )
            ui.text(output)
        """

        self._define_scope = try_new_scope_on_ui_state()

        self.__var_tracker = VarTrackerHelper(
            var_id_gen_fn=lambda: self._define_scope.register_element_ref(self)
        )
        self.__binding_tracker = BindingTrackerHelper(define_scope=self._define_scope)

    def __to_binding_config(
        self,
    ):
        raise NotImplementedError()

    def _to_json_dict(self):
        data = super()._to_json_dict()
        data["id"] = self.__var_tracker.var_id

        return data

    def _to_event_output_type(self) -> OutputSetType:
        return OutputSetType.ElementRefAction

    def _to_event_input_type(self) -> InputBindingType:
        return InputBindingType.ElementRef

    def _mark_as_used(self):
        self.__var_tracker.mark_as_used()

    def _mark_binding(self, scope: Scope) -> dict:
        return self.__binding_tracker.mark_binding(
            var_id=self.__var_tracker.var_id, scope=scope
        )


def run_element_method(method_name: str, *args, **kwargs):
    return {
        "method": method_name,
        "args": args,
    }
