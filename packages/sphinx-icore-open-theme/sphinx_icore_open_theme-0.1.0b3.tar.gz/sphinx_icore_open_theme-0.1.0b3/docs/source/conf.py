# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information


project = "manon-icore-open-sphinx-theme"
copyright = "Ministerie van Volksgezondheid, Welzijn en Sport"
author = "The iCore team"
release = "0.1.0"

master_doc = "index"
language = "en"

# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.

# https://www.sphinx-doc.org/en/master/usage/extensions/index.html
# https://myst-parser.readthedocs.io/en/latest/
# https://github.com/mgaitan/sphinxcontrib-mermaid
# https://github.com/mansenfranzen/autodoc_pydantic

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.extlinks",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
    "sphinx.ext.todo",
    "sphinx.ext.viewcode",
    "myst_parser",
    "sphinxcontrib.mermaid",
    "sphinxcontrib.autodoc_pydantic",
    # When developing locally, and using:
    #
    #   html_theme_path = ["../../src/sphinx_icore_open/theme"]
    #
    # Sphinx will use that local folder, and won't import the
    # sphinx_icore_open package, so the package setup() will not
    # run. For local testing we can add the package to the extensions as a
    # workaround.
    "sphinx_icore_open",
]

myst_enable_extensions = [
    "colon_fence",
    "tasklist",
]

source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

extlinks = {
    "git_tag": (
        "https://github.com/minvws/manon-icore-open-sphinx-theme/tree/%s",
        "%s",
    ),
    "bug": ("https://github.com/minvws/manon-icore-open-sphinx-theme/issues/%s", "#%s"),
    "feature": (
        "https://github.com/minvws/manon-icore-open-sphinx-theme/issues/%s",
        "#%s",
    ),
    "issue": (
        "https://github.com/minvws/manon-icore-open-sphinx-theme/issues/%s",
        "#%s",
    ),
}

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Theme and options for HTML output ---------------------------------------
html_theme_path = ["../../src/sphinx_icore_open/theme"]
html_theme = "sphinx_icore_open"


locale_dirs = ["locales/"]

html_show_sphinx = False
html_show_sourcelink = False

html_theme_options = {
    "description": "Manon Sphinx theme",
    "github_user": "minvws",
    "github_repo": "manon-icore-open-sphinx-theme",
    "tidelift_url": "https://github.com/minvws/manon-icore-open-sphinx-theme",
}
