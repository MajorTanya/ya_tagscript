# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys

sys.path.insert(0, os.path.abspath("./_ext"))


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "ya_tagscript"
project_copyright = "2025, MajorTanya"
author = "MajorTanya"

### VERSION SECTION START
version = "1.6.0"
### VERSION SECTION END
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "enum_tools.autoenum",
    "styled_list_directive",
    "glossary_backlink_checker",
    "myst_parser",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# Force all code blocks to be text unless specified otherwise
highlight_language = "text"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.

html_baseurl = os.environ.get("READTHEDOCS_CANONICAL_URL", "/")
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# autodoc
autodoc_default_options = {"show-inheritance": True}
autodoc_member_order = "bysource"
autodoc_inherit_docstrings = True

# simple references within backticks
default_role = "any"

modindex_common_prefix = ["ya_tagscript."]
trim_footnote_reference_space = True

nitpicky = True
# this one can't be expressed in the regex one due to the newline
nitpick_ignore = {
    (
        "py:class",
        """dict[Literal["items", "response"],
list[str] | str | None]""",
    ),
}
# ignore generic type annotations
nitpick_ignore_regex = [(r"py:class", r"(dict|set|list|tuple|Literal|Callable)\[.+\]")]

# Intersphinx
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "dpy": ("https://discordpy.readthedocs.io/en/stable/", None),
    "pyparsing": ("https://pyparsing-docs.readthedocs.io/en/latest", None),
    "dateutil": ("https://dateutil.readthedocs.io/en/stable/", None),
}

# MyST-Parser
myst_heading_anchors = 3

# Glossary Ref Checker
## this is referring to document names without the .html suffix (/changelog.html -> changelog)
refcheck_ignore_documents = ["changelog"]
