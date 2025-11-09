from typing import Union

from instaui.common.binding_track_mixin import BindingTrackerMixin


from ._types import _T_Value


TMaybeRef = Union[
    BindingTrackerMixin,
    _T_Value,
]
