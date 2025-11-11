# Installation

manon_theme requires **Sphinx 6.2 or newer**

> **note** You will need to explicitly enable the theme in your Sphinx config by
> adding this lines to your `conf.py`:

```
html_theme = "sphinx_icore_open"
```

## Extensions

Manon theme uses 2 extensions: `sphinx.ext.extlinks` and `myst_parser`

```
extensions = [
    "sphinx.ext.extlinks",
    "myst_parser",
]
```

-See `the Sphinx Markdown docs`
[markdown](https://www.sphinx-doc.org/en/master/usage/markdown.html) for details
on how this extension behaves. -See
`the Sphinx Markup to shorten external links`
[extlinks](https://www.sphinx-doc.org/en/master/usage/extensions/extlinks.html)
for details on how this extension behaves.

```
_static-path:
```

## Static path for images & custom stylesheet

If you're using any of the image-related options listed on :doc:`customization`
(`logo`) or a :ref:`custom stylesheet <custom-stylesheet>`, you'll also want to
tell Sphinx where to get these files from. If so, add a line like this (changing
the path if necessary; see `the Sphinx docs for 'html_static_path'`
[html_static_path](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_static_path)
to your `conf.py`:

```python
html_static_path = ['_static']
```
