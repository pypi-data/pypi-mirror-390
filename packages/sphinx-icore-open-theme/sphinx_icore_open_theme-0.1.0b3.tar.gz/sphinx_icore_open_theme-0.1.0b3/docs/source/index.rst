=========================
Manon: a Sphinx theme
=========================

Features
========

* Easy ability to use as a zip file.
* Style tweaks compared to the source themes, such as better code-block
  alignment, Github button placement, page source link moved to footer,
  improved (optional) related-items sidebar item, and many more;
* Many customization hooks, including toggle of various sidebar & footer
  components; header/link/etc color control; etc;
* Improved documentation for all customizations (pre-existing & new).

Implementation notes
====================

* Manon includes/requires a tiny Sphinx extension on top of the theme
  itself; this is just so we can inject dynamic metadata into template contexts. It doesn't add any additional
  directives or the like, at least not yet.


.. toctree::
    :hidden:
    :glob:

    *
