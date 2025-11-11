import os
from importlib.metadata import version
from sphinx.application import Sphinx
from sphinx_icore_open.translator import CustomHTMLTranslator


__version__ = version("sphinx-icore-open-theme")


def setup(app: Sphinx):
    root_path = os.path.abspath(os.path.dirname(__file__))
    theme_path = os.path.join(root_path, "theme/sphinx_icore_open")

    app.add_html_theme("sphinx_icore_open", theme_path)
    app.set_translator("html", CustomHTMLTranslator)

    return {"parallel_read_safe": True, "parallel_write_safe": True}
