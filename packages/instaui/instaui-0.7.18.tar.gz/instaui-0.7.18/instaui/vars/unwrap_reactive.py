from typing import Union
import copy
from instaui.common.binding_track_mixin import BindingTrackerMixin
from instaui.vars.js_computed import JsComputed


def unwrap_reactive(data: Union[dict, list], ignore_type_error: bool = False):
    """
    Convert nested reactive data into a plain structure while maintaining reactive updates.

    Args:
        data (Union[dict, list]): The data to be converted. Must be a Python dict or list.
        ignore_type_error (bool): If True, return the data directly when it is not a dict or list.

    Example:
    .. code-block:: python
        age = ui.state(18)
        data = [{"name": "John", "age": age}]

        unwrapped_data = unwrap_reactive(data)

        html.number(age)
        ui.text(unwrapped_data)

    """
    if not isinstance(data, (dict, list)):
        if ignore_type_error:
            return data
        assert False, "data should be a dict or a list"

    refs: list[BindingTrackerMixin] = []
    paths: list[list[Union[int, str]]] = []

    def walk(container, key, value, path: list[Union[int, str]]):
        if isinstance(value, BindingTrackerMixin):
            refs.append(value)
            paths.append(path.copy())
            container[key] = None
            return

        if isinstance(value, dict):
            for k, v in list(value.items()):
                walk(value, k, v, path + [str(k)])

        elif isinstance(value, list):
            for i, v in enumerate(list(value)):
                walk(value, i, v, path + [i])

    copy_data = copy.deepcopy(data)

    if isinstance(copy_data, dict):
        for k, v in list(copy_data.items()):
            walk(copy_data, k, v, [str(k)])
    elif isinstance(copy_data, list):
        for i, v in enumerate(list(copy_data)):
            walk(copy_data, i, v, [i])

    if not refs:
        return data

    return JsComputed(
        inputs=[copy_data, paths, *refs],
        _tool_name="unwrap_reactive",
        code="",
    )
