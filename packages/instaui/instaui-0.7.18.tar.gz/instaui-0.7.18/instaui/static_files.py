from pathlib import Path
import shutil
from instaui import consts


class Export:
    """
    Exports the compiled static files to the specified destination directory.


    # Example:
    .. code-block:: python
        from pathlib import Path
        from instaui import static_files

        static_files.Export.vue_js(Path("output/vue.es.js"))
    """

    @staticmethod
    def vue_js(to: Path):
        """
        Copies the Vue.js ES module file to the specified destination path.

        Args:
            to (Path): The destination file path where the Vue.js ES module will be copied.
                    Must be a valid writable path including the target filename.
        """
        shutil.copy2(consts.VUE_ES_JS_PATH, to)

    @staticmethod
    def instaui_js(to: Path):
        """
        Copies the InstaUI JavaScript ES module file to the specified destination path.

        Args:
            to (Path): The destination file path where the InstaUI JavaScript file will be copied.
                    Must be a valid writable path including the target filename.
        """
        shutil.copy2(consts.APP_ES_JS_PATH, to)

    @staticmethod
    def instaui_css(to: Path):
        """
        Copies the InstaUI CSS stylesheet file to the specified destination path.

        Args:
            to (Path): The destination file path where the InstaUI CSS file will be copied.
                    Must be a valid writable path including the target filename.
        """
        shutil.copy2(consts.APP_CSS_PATH, to)
