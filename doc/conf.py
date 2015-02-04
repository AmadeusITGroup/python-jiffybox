# coding=utf-8

import datetime
import os
import pkg_resources

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'


dist = pkg_resources.get_distribution('jiffybox')

project = dist.project_name
author = u'Thomas Weißschuh'
version = dist.version
release = version
this_year = datetime.date.today().year
copyright = 'Amadeus IT Group'

extensions = ['sphinx.ext.autodoc']
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'
exclude_patterns = ['_build']
pygments_style = 'sphinx'
html_static_path = ['_static']

if not on_rtd:
    import sphinx_rtd_theme
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
    html_theme = 'sphinx_rtd_theme'
else:
    html_theme = 'default'
