##############################################################################
# == Configuration file for the Sphinx documentation builder =================
#####
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from sphinx.application import Sphinx

DOC_ROOT = Path(__file__).parent.resolve()
PROJECT_ROOT = DOC_ROOT.parent
SRC_ROOT = PROJECT_ROOT.joinpath("src")
DOC_EXT_ROOT = DOC_ROOT.joinpath("_ext")

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

source_paths = [
    *os.getenv("SPHINX_APIDOC_SOURCES", "").split(":"),
    DOC_ROOT,
    SRC_ROOT,
    DOC_EXT_ROOT,
]

for source_path in source_paths:
    if not isinstance(source_path, Path):
        source_path = Path(source_path)
    sys.path.insert(0, str(source_path.resolve()))

#####
##############################################################################

##############################################################################
# -- Project information -----------------------------------------------------
#####
from sphinx_terraform import __version__

_today = datetime.today()

project = os.getenv("SPHINX_CONF_PROJECT", "Sphinx-Terraform")
author = os.getenv("SPHINX_CONF_AUTHOR", "Charles Bouchard-Légaré")
copyright = f"{_today.year}, {author}"

# The full version, including alpha/beta/rc tags
release = os.getenv("SPHINX_CONF_RELEASE", __version__)
version = ".".join(release.split(".")[:2])

#####
##############################################################################


##############################################################################
# -- General configuration ---------------------------------------------------

# If your project needs a minimal Sphinx version, state it here.
needs_sphinx = "3"

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named "sphinx.ext.*") or your custom
# ones.
extensions = [
    "sphinx.ext.napoleon",  # Google-style docstrings
    "sphinx.ext.intersphinx",  # Link to other Sphinx docs
    "sphinx.ext.autodoc",  # Generate doc from python source
    "sphinx_autodoc_typehints",  # Read types from type annotations
    "sphinx_paramlinks",  # Link to function parameters
    "sphinx.ext.viewcode",  # Add links to highlighted source code
    "sphinx.ext.todo",  # To do notes within the documentation
    # "sphinx.ext.extlinks",  # Markup to shorten external links
    "sphinx.ext.ifconfig",  # Conditional documentation parts
    "sphinx.ext.graphviz",  # Add Graphviz graphs
    "sphinx_copybutton",  # «Copy» to clipboard javascript button
    "sphinxcontrib.bibtex",  # BibTeX style citations and bibliography
    "sphinxcontrib.programoutput",  # Insert the output of arbitrary commands into documents.
    "sphinx_tabs.tabs",  # Create tabbed content when building HTML.
    "sphinx_terraform",
    "sphinx_terraform.viewcode",
]
for module_file in DOC_EXT_ROOT.glob("[!_]*.py"):
    extensions.append(module_file.stem)


suppress_warnings = ["extlinks.hardcoded"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = [".rst"]

# The master toctree document without its file extension.
master_doc = "index"

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []

# The language for content autogenerated by Sphinx. Refer to documentation
# for a list of supported languages.
#
# This is also used if you do content translation via gettext catalogs.
# Usually you set "language" from the command line for these cases.
language = "en"

# Directories in which to search for additional message catalogs (see language),
# relative to the source directory. The directories on this path are searched
# by the standard gettext module.
#
# Internal messages are fetched from a text domain of sphinx; so if you add the
# directory ./locale to this setting, the message catalogs (compiled from .po
# format using msgfmt) must be in ./locale/language/LC_MESSAGES/sphinx.mo. The
# text domain of individual documents depends on gettext_compact.
locale_dirs = ["locales"]

# The reST default role (used for this markup: `text`) to use for all
# documents.
# default_role = None

# If true, "()" will be appended to :func: etc. cross-reference text.
# add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
# add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
# show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "friendly"

# A list of ignored prefixes for module index sorting.
# modindex_common_prefix = []

# If true, keep warnings as "system message" paragraphs in the built documents.
# keep_warnings = False

# A string of reStructuredText that will be included at the beginning of every
# source file that is read. This is a possible place to add substitutions that
# should be available in every file (another being rst_epilog).
rst_prolog = f"""
.. |project| replace:: **{project}**
"""

# A string of reStructuredText that will be included at the end of every source
# file that is read. This is a possible place to add substitutions that should
# be available in every file (another being rst_prolog).
# rst_epilog = ""

#####
##############################################################################


##############################################################################
# -- Builders configuration --------------------------------------------------
#####

###
# -- Options for linkcheck: the builder that checks all links goes somewhere
#
# A list of regular expressions that match URIs that should not be checked
# when doing a linkcheck build.
linkcheck_ignore = []

#
###

###
# -- Options for HTML output
#
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "icon_links": [
        {
            "name": "GitLab",
            "url": "https://gitlab.com/cblegare/sphinx-terraform",
            "icon": "fab fa-gitlab",
        },
    ],
    "show_prev_next": True,
    "use_edit_page_button": True,
}

# A dictionary of values to pass into the template engine’s context for all
# pages. Single values can also be put in this dictionary using the
# -A command-line option of sphinx-build.
if os.getenv("CI_MERGE_REQUEST_IID", None):
    review_app = {
        "project_id": os.getenv("CI_PROJECT_ID"),
        "project_path": os.getenv("CI_PROJECT_PATH"),
        "mr_id": os.getenv("CI_MERGE_REQUEST_IID"),
        "server_url": os.getenv("CI_SERVER_URL"),
    }
else:
    review_app = None
html_context = {
    # "gitlab_url": "https://gitlab.com", # or your self-hosted GitLab
    "gitlab_user": "cblegare",
    "gitlab_repo": "sphinx-terraform",
    "gitlab_version": "main",
    "doc_path": "docs",
    # Enable the Giltab review app widget,
    # see also
    #   _templates/layout.html
    #   https://docs.gitlab.com/ee/ci/review_apps/#configuring-visual-reviews
    "review_app": review_app,
}

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = project

# A shorter title for the navigation bar.  Default is the same as html_title.
# html_short_title = None

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
# html_logo = "pixmap/logo.svg"

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
# html_favicon = "pixmap/favicon.ico"

# Custom sidebar templates, must be a dictionary that maps document names to
# template names.
#
# The keys can contain glob-style patterns, in which case all matching documents
# will get the specified sidebars. (A warning is emitted when a more than one
# glob-style pattern matches for any document.)
#
# The values can be either lists or single strings.
# If a value is a list, it specifies the complete list of sidebar templates to
# include. If all or some of the default sidebars are to be included, they must
# be put into this list as well.
#
# The default sidebars (for documents that don’t match any pattern) are defined
# by theme itself.
# Builtin themes are using these templates by default:
#  - localtoc.html
#  - relations.html
#  - sourcelink.html
#  - searchbox.html
#
# Builtin sidebar templates that can be rendered are:
#  - localtoc.html – a fine-grained table of contents of the current document
#  - globaltoc.html – a coarse-grained table of contents for the whole documentation set,
#    collapsed
#  - relations.html – two links to the previous and next documents
#  - sourcelink.html – a link to the source of the current document, if enabled
#    in html_show_sourcelink
#  - searchbox.html – the “quick search” box
html_sidebars = {
    "**": [
        "search-field",
        "sidebar-nav-bs.html",
        # "localtoc.html",
        "sourcelink.html",
    ]
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]

# Add any extra paths that contain custom files (such as robots.txt or
# .htaccess) here, relative to this directory. These files are copied
# directly to the root of the documentation.
# html_extra_path = []

# A list of CSS files.
# The entry must be a filename string or a tuple containing the filename
# string and the attributes dictionary. The filename must be relative to
# the html_static_path, or a full URI with scheme like http://example.org/style.css.
# The attributes is used for attributes of <link> tag.
# It defaults to an empty list.
html_css_files = [
    "style.css",
]

# If not "", a "Last updated on:" timestamp is inserted at every page bottom,
# using the given strftime format.
# html_last_updated_fmt = "%b %d, %Y"

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
# html_use_smartypants = True

# Additional templates that should be rendered to pages, maps page names to
# template names.
# html_additional_pages = {}

# If false, no module index is generated.
# html_domain_indices = True

# If false, no index is generated.
# html_use_index = True

# If true, the index is split into individual pages for each letter.
# html_split_index = False

# If true, links to the reST sources are added to the pages.
html_show_sourcelink = True

# If true, "Created using Sphinx" is shown in the HTML footer. Default is True.
html_show_sphinx = True

# If true, "(C) Copyright ..." is shown in the HTML footer. Default is True.
html_show_copyright = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
# html_use_opensearch = ""

# This is the file name suffix for HTML files (e.g. ".xhtml").
# html_file_suffix = None

# Language to be used for generating the HTML full-text search index.
# Sphinx supports the following languages:
#   "da", "de", "en", "es", "fi", "fr", "hu", "it", "ja"
#   "nl", "no", "pt", "ro", "ru", "sv", "tr"
# html_search_language = "en"

# A dictionary with options for the search language support, empty by default.
# Now only "ja" uses this config value
# html_search_options = {"type": "default"}

# The name of a javascript file (relative to the configuration directory) that
# implements a search results scorer. If empty, the default will be used.
# html_search_scorer = "scorer.js"

#
###

###
# -- Options for LaTeX output
#
#   For more information, see https://www.sphinx-doc.org/en/master/latex.html
#

# A dictionary that contains LaTeX snippets overriding those Sphinx usually
# puts into the generated .tex files. Its "sphinxsetup" key is described
# separately.
latex_elements = {
    # The paper size ("letterpaper" or "a4paper").
    # "papersize": "letterpaper",
    # The font size ("10pt", "11pt" or "12pt").
    # "pointsize": "10pt",
    # Additional stuff for the LaTeX preamble.
    # "preamble": "",
}

# We use Unicode character, so xelatex to the rescue.
latex_engine = "xelatex"

# This value determines how to group the document tree into LaTeX source files.
# It must be a list of tuples
#
#   (startdocname, targetname, title, author, theme, toctree_only),
#
# where the items are:
#
# startdocname
#   String that specifies the document name of the LaTeX file’s master
#   document. All documents referenced by the startdoc document in TOC trees
#   will be included in the LaTeX file. (If you want to use the default master
#   document for your LaTeX build, provide your master_doc here.)
#
# targetname
#   File name of the LaTeX file in the output directory.
#
# title
#   LaTeX document title. Can be empty to use the title of the startdoc
#   document. This is inserted as LaTeX markup, so special characters like a
#   backslash or ampersand must be represented by the proper LaTeX commands if
#   they are to be inserted literally.
#
# author
#   Author for the LaTeX document. The same LaTeX markup caveat as for title
#   applies. Use \\and to separate multiple authors, as in: "John \\and Sarah"
#   (backslashes must be Python-escaped to reach LaTeX).
#
# theme
#   LaTeX theme. See latex_theme.
#
# toctree_only
#   Must be True or False. If true, the startdoc document itself is not
#   included in the output, only the documents referenced by it via TOC trees.
#   With this option, you can put extra stuff in the master document that shows
#   up in the HTML, but not the LaTeX output.
latex_documents = [
    (
        master_doc,
        "{!s}-{!s}.tex".format(project, release),
        project,
        author,
        "manual",
        False,
    ),
]

#
###

#####
##############################################################################


##############################################################################
# -- Extension configuration -------------------------------------------------
#####

###
# -- Options for todo extension
#
# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = True
###

###
# -- Options for Copybutto,
#
# Using regexp prompt identifiers
copybutton_prompt_text = (
    r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
)
copybutton_prompt_is_regexp = True
# Honor line continuation characters when copying multline-snippets
copybutton_line_continuation_character = "\\"
# Honor HERE-document syntax when copying multiline-snippets
copybutton_here_doc_delimiter = "EOT"
###

###
# -- Options for sphinxcontrib-bibtex
bibtex_bibfiles = [
    str(bibtext_file.relative_to(DOC_ROOT))
    for bibtext_file in DOC_ROOT.rglob("*.bib")
]
###

###
# -- Options for intersphinx extension ---------------------------------------
#
# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    "python": ("https://docs.python.org/3/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "gitlab": ("https://python-gitlab.readthedocs.io/en/stable/", None),
    "setuptools": ("https://setuptools.readthedocs.io/en/latest/", None),
}
#
nitpicky = True
nitpick_ignore = [
    ("py:class", "re.Pattern"),
    ("py:class", "Path"),
    ("py:class", "typing_extensions.Protocol"),
    ("py:class", "domain label"),  # this one confuses me a lot
    ("py:class", "sphinx.ext.intersphinx.normalize_intersphinx_mapping"),
    ("py:class", "sphinx.environment.NoUri"),
    ("py:exc", "sphinx.environment.NoUri"),
    ("py:class", "sphinx.highlighting.PygmentsBridge"),
    ("py:class", "sphinx.util.typing.OptionSpec"),
    ("py:class", "OptionSpec"),
    ("py:class", "sphinx.roles.XRefRole"),
    ("py:class", "XRefRole"),
    ("py:class", "RoleFunction"),
    ("py:class", "sphinx.directives.ObjectDescription"),
    ("py:class", "ObjectDescription"),
    ("py:class", "sphinx.domains.Index"),
    ("py:class", "Index"),
    ("py:class", "sphinx.domains.ObjType"),
    ("py:class", "sphinx.domains.IndexEntry"),
    ("py:class", "ObjType"),
    ("py:meth", "sphinx.roles.XRefRole.process_link"),
    ("py:meth", "sphinx.roles.XRefRole.result_nodes"),
    ("py:class", "docutils.nodes.Element"),
    ("py:class", "docutils.nodes.document"),
    ("py:class", "docutils.nodes.Node"),
    ("py:class", "docutils.nodes.system_message"),
]
###

###
# -- Options for extlinks ----------------------------------------------------
#
extlinks = {
    "dudir": (
        "http://docutils.sourceforge.net/docs/ref/rst/directives.html#%s",
        "",
    ),
    "release": (
        "https://gitlab.com/cblegare/sphinx-terraform/-/releases/%s",
        "Sphinx-Terraform v",
    ),
    "mr": (
        "https://gitlab.com/cblegare/sphinx-terraform/-/merge_requests/%s",
        "!",
    ),
    "issue": (
        "https://gitlab.com/cblegare/sphinx-terraform/-/issues/%s",
        "#",
    ),
    "commiter": ("https://gitlab.com/%s", "@"),
}
###

###
# -- Options for sphinx_terraform --------------------------------------
#
terraform_sources = {"terraform": str(DOC_ROOT.joinpath("demo/terraform"))}
###

#####
##############################################################################

##############################################################################
# -- Local extension ---------------------------------------------------------
#####
#
# The conf.py file can act directly as a Sphinx extension by defining a
# setup function that takes a Sphinx object as an argument.
def setup(app: Sphinx):
    ...


#####
##############################################################################
