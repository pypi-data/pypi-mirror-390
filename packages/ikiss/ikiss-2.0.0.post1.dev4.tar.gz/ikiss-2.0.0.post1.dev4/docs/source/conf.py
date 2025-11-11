#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
# add flag for readthedocs https://docs.readthedocs.io/en/stable/feature-flags.html#available-flags
DONT_OVERWRITE_SPHINX_CONTEXT = 'dont_overwrite_sphinx_context'

import os
import sys
from datetime import datetime

# Insert project root so autodoc can import modules
sys.path.insert(0, os.path.abspath('../..'))  # docs/source → project root

# -- Project information -----------------------------------------------------

# Load metadata from pyproject.toml using stdlib tomllib (3.11+) or tomli fallback
try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

with open(os.path.abspath(os.path.join(sys.path[0], 'pyproject.toml')), 'rb') as f:
    metadata = tomllib.load(f)['project']

project = metadata['name']                                          # PEP 621 project name
authors = [a['name'] for a in metadata.get('authors', [])]         # List of author names
# Dynamically assign version and release
version = metadata.get('version', '0.0.0').split('+')[0]           # short X.Y.Z version
release = metadata.get('version', version)                         # full release string

# Set current year for copyright
year = datetime.now().year
copyright = f"2024–{year}, {', '.join(authors)}"

# -- General configuration ---------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',          # Auto-generate API docs from docstrings
    'sphinx.ext.autosummary',  # <-- enable autosummary
    'sphinx_automodapi.automodsumm',  # <-- enable autosummary
    'sphinx_automodapi.automodapi',  # Automates module & class API pages
    'sphinx.ext.viewcode',         # Add links to highlighted source
    'sphinx.ext.napoleon',         # Google & NumPy style docstrings
    'sphinx.ext.intersphinx',      # Link to external project docs
    'sphinx.ext.graphviz',         # Render Graphviz diagrams
    'sphinx_copybutton',           # “Copy” buttons for code blocks
    'sphinx_design',               # Layout components (cards, grids
    'myst_parser',                 # Markdown support
    'click_extra.sphinx',          # Enhanced Click integration
]

# Configuration pour autosummary (si tu l'utilises)
autosummary_generate = True
autosummary_generate_overwrite = True
# Do NOT document classes/functions imported into modules
autosummary_imported_members = False   # default is False
# If you do use __all__, only honor that and nothing else
autosummary_ignore_module_all = False   # default is True
# Configuration pour automodapi (si tu l'utilises)
automodapi_default_toctree_dir = 'api' # Répertoire où les fichiers .rst de l'API seront générés
automodapi_toctreedirnm = 'api'      # Assure la cohérence du nom du répertoire dans le toctree

# Configuration pour autodoc
autodoc_typehints = "description" # Affiche les types dans la description des paramètres
autodoc_member_order = 'bysource' # Ordonne les membres comme ils apparaissent dans le code
autodoc_default_options = {
    'members': False,
    'undoc-members': True,
    'inherited-members': False, # Exclut les membres hérités de classes parentes
    'show-inheritance': False
}
# Active (par défaut) les figures ERD pour autodoc_pydantic
autodoc_pydantic_model_erdantic_figure = True
# Configuration pour napoleon (si tu l'utilises)
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = False
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = False

# Source file types
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# The master toctree document
master_doc = 'index'

# Patterns to exclude
exclude_patterns = ['_build', '**.ipynb_checkpoints']

# -- Intersphinx configuration -----------------------------------------------

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master', None),
}

gitlab_url = 'forge.ird.fr'
gitlab_user = 'ikiss'
gitlab_repo = 'forge.ird.fr'
gitlab_version = 'main'
display_gitlab = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    'flyout_display': 'attached',
    'version_selector': True,
    'language_selector': True,
    # Toc options
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 3,
    'includehidden': False,
    'titles_only': False,
}

# Add templates and static assets
templates_path = ['_templates']
html_static_path = ['_static']
source_suffix = ['.rst', "md"]
exclude_patterns = ['_build']
master_doc = 'index'

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'native'

# Logo and favicon
html_logo = '_static/logo_ikiss.png'
html_favicon = '_static/ikiss.png'

# Titles
html_title = f"{project} v{release} Documentation"
html_short_title = project

# Show/hide Sphinx branding
html_show_sphinx = False
html_use_index = True
html_split_index = False
# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

# -- HTML context for GitLab integration -------------------------------------
global html_context
html_context = {
    "gitlab_host": "forge.ird.fr",
    "display_gitlab": True, # Integrate Gitlab
    "gitlab_user": "diade", # Username
    "gitlab_repo": "ikiss", # Repo name
    "gitlab_version": "main", # Version
    "conf_py_path": "/docs/source/", # Path in the checkout to the docs root
}


# -- End of configuration -----------------------------------------------------
