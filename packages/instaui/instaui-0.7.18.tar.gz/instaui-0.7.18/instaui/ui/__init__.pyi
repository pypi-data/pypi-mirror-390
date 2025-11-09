# -- __all__
__all__ = [
    "__version__",
    "TMaybeRef",
    "not_",
    "len_",
    "MISSING",
    "TMissing",
    "TBindable",
    "is_bindable",
    "slient",
    "data",
    "TConstData",
    "vue_computed",
    "TVueComputed",
    "js_computed",
    "TJsComputed",
    "computed",
    "TComputed",
    "state",
    "StateModel",
    "local_storage",
    "session_storage",
    "use_dark",
    "PageState",
    "TVForItem",
    "TVForIndex",
    "element_ref",
    "run_element_method",
    "to_json",
    "to_config_data",
    "element",
    "vfor",
    "content",
    "add_style",
    "add_css_link",
    "remove_css_link",
    "add_js_code",
    "add_js_link",
    "add_vue_app_use",
    "use_tailwind",
    "use_page_title",
    "use_language",
    "unwrap_reactive",
    "directive",
    "vif",
    "page",
    "event",
    "js_event",
    "vue_event",
    "event_context",
    "TEventFn",
    "server",
    "context",
    "row",
    "grid",
    "container",
    "text",
    "link",
    "lazy_render",
    "heading",
    "watch",
    "vue_watch",
    "js_watch",
    "js_fn",
    "TWatchState",
    "match",
    "column",
    "experimental",
    "skip_output",
    "str_format",
    "pre_setup_action",
    "patch_set",
    "on_page_init_lifespan",
    "webview",
    "markdown",
    "timer",
    "teleport",
    "icon",
    "box",
    "flex",
    "image",
    "video",
]

# -- static imports
from instaui.version import __version__
from instaui.vars.types import TMaybeRef
from instaui.vars.functions import not_, len_
from instaui.missing import MISSING, TMissing

from instaui.vars.data import const_data as data, TConstData
from instaui.vars.js_computed import js_computed, TJsComputed
from instaui.vars.vue_computed import VueComputed as vue_computed, TVueComputed
from instaui.vars.web_computed import web_computed as computed, TComputed
from instaui.vars.state import state, StateModel
from instaui.vars.local_storage import local_storage
from instaui.vars.session_storage import session_storage
from instaui.vars.use_dark import use_dark
from instaui.vars.use_page_title import use_page_title
from instaui.vars.use_language import use_language
from instaui.vars.unwrap_reactive import unwrap_reactive
from instaui.page_state import PageState
from instaui.vars.vfor_item import TVForItem, TVForIndex
from instaui.vars.element_ref import ElementRef as element_ref, run_element_method
from instaui.html_tools import (
    to_json,
    add_css_link,
    remove_css_link,
    add_js_link,
    add_style,
    add_js_code,
    add_vue_app_use,
    to_config_data,
    use_tailwind,
)

from instaui.components.element import Element as element
from instaui.components.heading import Heading as heading
from instaui.components.directive import Directive as directive
from instaui.components.vfor import VFor as vfor
from instaui.components.vif import VIf as vif
from instaui.components.match import Match as match
from instaui.components.content import Content as content
from instaui.components.timer.timer import Timer as timer
from instaui.components.teleport import teleport
from instaui.components.icon import Icon as icon
from instaui.components.layout.box import Box as box
from instaui.components.layout.flex import (
    Flex as flex,
    FlexRow as row,
    FlexColumn as column,
)
from instaui.components.layout.grid import Grid as grid
from instaui.components.layout.container import Container as container
from instaui.components.text import Text as text
from instaui.components.link import Link as link
from instaui.components.lazy_render import LazyRender as lazy_render

from instaui.event.web_event import event, WebEvent as TEventFn
from instaui.event.js_event import js_event
from instaui.event.vue_event import vue_event
from instaui.vars.event_context import EventContext as event_context
from instaui.runtime.context import get_context as context

from instaui.watch.web_watch import watch
from instaui.watch.vue_watch import vue_watch
from instaui.watch.js_watch import js_watch
from instaui.handlers.watch_handler import WatchState as TWatchState
from instaui.skip import skip_output
from instaui.ui_functions.input_slient_data import InputSilentData as slient
import instaui.experimental as experimental

from instaui.ui_functions.server import create_server as server
from instaui.ui_functions.ui_page import page
from instaui.ui_functions.str_format import str_format
from instaui.ui_functions.ui_types import TBindable, is_bindable

from ._events import on_page_init_lifespan
from instaui.extra_libs._import_error import show_error  # noqa: E402, F401
from instaui.js.fn import JsFn as js_fn
from instaui.pre_setup import PreSetupAction as pre_setup_action
from instaui.patch_update import patch_set
from instaui.components.html.image import Image as image
from instaui.components.html.video import Video as video

# -- dynamic imports
from instaui.components.markdown.markdown import Markdown as markdown
from instaui.webview import WebviewWrapper as webview

# -- extra libs
