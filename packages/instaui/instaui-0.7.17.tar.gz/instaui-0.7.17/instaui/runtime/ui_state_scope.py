import contextvars


_scope_var: contextvars.ContextVar[dict[type, object]] = contextvars.ContextVar(
    "_scope_var", default={}
)


def save_state(key, obj: object) -> None:
    _scope_var.get()[key] = obj


def load_state(key) -> object:
    return _scope_var.get()[key]
