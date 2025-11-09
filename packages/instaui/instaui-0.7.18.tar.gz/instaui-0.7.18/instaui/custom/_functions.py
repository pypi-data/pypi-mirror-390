from typing import Any
from instaui.common.binding_track_mixin import mark_binding, is_binding_tracker
from instaui.common.var_track_mixin import mark_as_used, is_var_tracker


def convert_reference(binding: Any):
    """
    Allows reactive variable configurations to be passed into custom components, enabling them to obtain their Ref references.

    Args:
        binding (Any): The reactive binding or variable to be converted

    Examples:
    .. code-block:: python

        class CustomElement(custom.element, esm="./custom_element.js"):
            def __init__(self, ref):
                super().__init__()
                self.props({"ref_binding": custom.convert_reference(ref)})
    """

    assert is_var_tracker(binding), "binding should be a VarTrackerMixin"
    mark_as_used(binding)

    assert is_binding_tracker(binding), "binding should be a BindingTrackerMixin"
    config = mark_binding(binding)
    return config
