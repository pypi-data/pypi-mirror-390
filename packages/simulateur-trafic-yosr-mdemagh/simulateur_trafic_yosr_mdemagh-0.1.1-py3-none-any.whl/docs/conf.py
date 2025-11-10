import os
import sys
sys.path.insert(0, os.path.abspath(".."))

# -- Project information -----------------------------------------------------
project = 'simulateur_trafic'
copyright = '2025, Yosr Mdemagh'
author = 'Yosr Mdemagh'
release = '1.0'

# -- General configuration ---------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon"
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

language = 'fr'

# -- Options for HTML output -------------------------------------------------
html_theme = 'alabaster'  # ou 'sphinx_rtd_theme'
html_static_path = ['_static']
