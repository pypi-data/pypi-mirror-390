# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "clig"
copyright = "2025, Diogo Rossi"
author = "Diogo Rossi"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

import os
from pathlib import Path


import sys
from pathlib import Path

path = Path(__file__).parent
sys.path.insert(0, str((path).resolve()))
os.chdir(path)

import convert_notebook

extensions = ["myst_parser", "sphinx_copybutton"]

templates_path = ["_templates"]
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_title = '<p style="text-align: center"><b>clig</b></p>'
html_static_path = ["_static"]
# conf.py
html_css_files = ["css/custom.css"]
html_logo = "logo.png"

def setup(app):
    app.add_css_file("custom.css")
