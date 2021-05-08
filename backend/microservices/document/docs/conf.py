import os
import sys

sys.path.insert(0, os.path.abspath('..'))

project = 'Document Service'
copyright = '2021, thlink'
author = 'thlink'

extensions = [
    "sphinx.ext.autodoc",
    "sphinxcontrib.autodoc_pydantic",
]

templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

html_theme = 'alabaster'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

autodoc_pydantic_model_members = False
autodoc_pydantic_model_show_config_summary = False
