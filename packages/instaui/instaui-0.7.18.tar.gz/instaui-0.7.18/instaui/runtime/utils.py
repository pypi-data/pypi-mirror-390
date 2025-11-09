from __future__ import annotations
from typing import TYPE_CHECKING


from instaui.runtime.scope import BaseScope
from instaui.vars.use_dark import UseDarkRef
from instaui.vars.use_page_title import UsePageTitleRef
from instaui.vars.use_language import UseLanguageRef

if TYPE_CHECKING:
    from instaui.runtime._app import App


def init_base_scope(app: App):
    bs = BaseScope(app.gen_scope_id())
    app.setup(bs)
    bs.setup(
        use_dark=UseDarkRef(),
        use_page_title=UsePageTitleRef(),
        use_language=UseLanguageRef(),
    )
