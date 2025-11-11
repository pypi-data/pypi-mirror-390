# Customization

The Manon Sphinx theme behavior & style can be customized in multiple ways:

- Various template-level or nontrivial-style settings can be configured via your
  `conf.py` in `html_theme_options`; see :ref:`theme-options`.
- You can provide your own CSS stylesheet overrides via a
  :ref:`custom stylesheet <custom-stylesheet>`. This is suitable for changes
  that only need minor CSS modifications.

```
_custom-stylesheet:
```

## Custom stylesheet

If you need to modify the Manon Sphinx theme's default CSS styles in a way not
covered by the theme options from the next section, you may provide a custom CSS
stylesheet as follows:

- Create a file named `custom.css` anywhere you prefer (typically `_static/`,
  but this is solely convention) containing your desired overrides to the CSS
  found in the Manon Sphinx theme's `static/css/manon_theme.css`.
- Set the core Sphinx option `html_static_path`
  [html_static_path](https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_static_path)
  to either that file's path, or the directory it lives within.

```
_theme-options:
```

## Theme options

The Manon Sphinx theme's primary configuration route is the `html_theme_options`
variable, set in `conf.py` alongside the rest, e.g.:

```python
html_theme_options = {
    "description": "Manon Sphinx theme",
    "github_user": "minvws",
    "github_repo": "manon-icore-open-sphinx-theme",
    "tidelift_url": "https://github.com/minvws/manon-icore-open-sphinx-theme",
}
```

### Basics

Settings related to text display, logo, etc.

-`description`: Text blurb about your project, to appear under the
logo. -`logo`: Relative path (from `$PROJECT/_static/`) to a logo image, which
will appear in the upper left corner above the name of the project.

### Service links and badges

Third-party services (GitHub) and related badges or banners.

-`github_repo`: Used by `github_button` and `github_banner` (see above); does
nothing if both of those are set to `false`. -`github_user`: Used by
`github_button` and `github_banner` (see above); does nothing if both of those
are set to `false`. -`tidelift_url`: Set this to your
[Tidelift](https://tidelift.com/) project URL if you want a "Professional
support" section in your sidebar.
