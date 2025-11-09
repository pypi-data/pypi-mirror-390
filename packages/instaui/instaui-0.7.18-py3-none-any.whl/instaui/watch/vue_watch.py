from __future__ import annotations
from typing import (
    Any,
    Optional,
    Sequence,
    Union,
)

from instaui.common.binding_track_mixin import try_mark_binding
from instaui.common.var_track_mixin import mark_as_used
from instaui.vars.mixin_types.observable import ObservableMixin

from . import _types
from . import _utils

from instaui.common.jsonable import Jsonable
from instaui.runtime import get_current_scope


class VueWatch(Jsonable):
    def __init__(
        self,
        sources: Union[Any, Sequence],
        callback: str,
        *,
        bindings: Optional[dict[str, Any]] = None,
        immediate: bool = False,
        deep: Union[bool, int] = False,
        once: bool = False,
        flush: Optional[_types.TFlush] = None,
    ) -> None:
        get_current_scope().register_vue_watch(self)
        mark_as_used(sources)

        self.code = callback

        if not isinstance(sources, Sequence):
            sources = [sources]

        onData = [int(not isinstance(varObj, ObservableMixin)) for varObj in sources]

        if sum(onData) > 0:
            self.onData = onData

        self.on = [try_mark_binding(varObj) for varObj in sources]

        if bindings:
            mark_as_used(bindings)

            bindData = [
                int(not isinstance(v, ObservableMixin)) for v in bindings.values()
            ]

            if sum(bindData) > 0:
                self.bindData = bindData

            self.bind = {k: try_mark_binding(v) for k, v in bindings.items()}

        if immediate is not False:
            self.immediate = immediate

        if deep is not False:
            _utils.assert_deep(deep)
            self.deep = deep

        if once is not False:
            self.once = once

        if flush is not None:
            self.flush = flush


def vue_watch(
    sources: Union[Any, Sequence],
    callback: str,
    *,
    bindings: Optional[dict[str, Any]] = None,
    immediate: bool = False,
    deep: Union[bool, int] = False,
    once: bool = False,
    flush: Optional[_types.TFlush] = None,
):
    """ """

    watch = VueWatch(
        sources,
        callback,
        bindings=bindings,
        immediate=immediate,
        deep=deep,
        once=once,
        flush=flush,
    )
    return watch
