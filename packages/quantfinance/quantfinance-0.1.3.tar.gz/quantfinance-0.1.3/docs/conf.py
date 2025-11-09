

import os
import sys


sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'quantfinance'
copyright = '2025, Marcel ALOEKPO'
author = 'Marcel ALOEKPO'


release = '0.1.2'




# -- Options for HTML output -------------------------------------------------

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',  
    'sphinx.ext.intersphinx',  
    'myst_parser',  
    'sphinx_copybutton',  
]

templates_path = ['_templates']


exclude_patterns = []

html_theme = 'sphinx_rtd_theme'

html_static_path = ['_static']






copybutton_prompt_text = ">>> "
copybutton_prompt_is_regexp = True