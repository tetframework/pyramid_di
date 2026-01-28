#!/usr/bin/env python3
# pyramid_di documentation build configuration file

import os
import re

# -- General configuration ------------------------------------------------

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.viewcode",
    "myst_parser",
]

templates_path = ["_templates"]

# Support both RST and Markdown
source_suffix = {
    ".rst": "restructuredtext",
    ".md": "markdown",
}

master_doc = "index"

# General information about the project.
project = "pyramid_di"
copyright = "2020, Antti Haapala"
author = "Antti Haapala"

# Read version from setup.py
setup_py_path = os.path.join(os.path.dirname(__file__), "..", "setup.py")
with open(setup_py_path) as f:
    content = f.read()
    match = re.search(r'version="([^"]+)"', content)
    if match:
        release = match.group(1)
        version = ".".join(release.split(".")[:2])
    else:
        version = "0.4"
        release = "0.4.2"

language = "en"

exclude_patterns = ["_build"]

pygments_style = "sphinx"


# -- Options for HTML output ----------------------------------------------

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "logo_only": True,
}

html_static_path = ["_static"]

htmlhelp_basename = "pyramid_di_doc"


# -- Options for intersphinx ----------------------------------------------

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "pyramid": ("https://docs.pylonsproject.org/projects/pyramid/en/latest/", None),
}
