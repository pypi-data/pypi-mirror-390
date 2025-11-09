from typing import cast
from instaui.common.binding_track_mixin import is_binding_tracker
from instaui.common.var_track_mixin import mark_as_used
from instaui.vars.mixin_types.str_format_binding import StrFormatBindingMixin
from instaui.vars.vue_computed import VueComputed


def str_format(template: str, *args, **kwargs):
    """
    Formats a string template with positional and keyword arguments.

    Args:
        template (str): The string template containing {} placeholders for formatting.
        *args: Variable length positional arguments for positional formatting.
        **kwargs: Arbitrary keyword arguments for named formatting.

    Example:
    .. code-block:: python
        # Positional formatting
        ui.str_format("pos:a={},b={}", a, b)

        # Index-based positional formatting
        ui.str_format("num pos:a={0},b={1}", a, b)

        # Named formatting
        ui.str_format("name pos:b={b},a={a}", a=a, b=b)
    """
    bindings = {}
    tran_args = []

    mark_as_used(args)
    mark_as_used(kwargs)

    for idx, arg in enumerate(args):
        is_mixin = is_binding_tracker(arg)
        value = (
            cast(StrFormatBindingMixin, arg)._to_str_format_binding(idx)
            if is_mixin
            else arg
        )
        tran_args.append(value[-1] if is_mixin else value)
        if is_mixin:
            bindings[value[0]] = arg

    tran_kwargs = {}

    for idx, (k, v) in enumerate(kwargs.items()):
        is_mixin = is_binding_tracker(v)
        value = (
            cast(StrFormatBindingMixin, v)._to_str_format_binding(idx)
            if is_mixin
            else v
        )
        tran_kwargs[k] = value[-1] if is_mixin else value
        if is_mixin:
            bindings[value[0]] = v

    code = "()=>`" + template.format(*tran_args, **tran_kwargs) + "`"
    return cast(str, VueComputed(code, bindings=bindings))
