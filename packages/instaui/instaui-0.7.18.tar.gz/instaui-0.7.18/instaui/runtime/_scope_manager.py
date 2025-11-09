from ._index import get_current_scope, get_app_slot
from .scope import Scope


def try_new_scope_on_ui_state() -> Scope:
    scope = get_current_scope()
    vfor = scope.get_running_vfor()

    if vfor is None:
        return scope

    app = get_app_slot()
    _new_scope = Scope(app.gen_scope_id())

    _new_scope.__enter__()

    @vfor._on_exit
    def _():
        _new_scope.__exit__()

    return _new_scope
