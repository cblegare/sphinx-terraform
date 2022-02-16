from __future__ import annotations

import sys
from enum import Enum
from typing import TYPE_CHECKING, Any, Dict, NamedTuple, Optional

if TYPE_CHECKING or sys.version_info < (3, 8, 0):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


class ExtensionMetadata(TypedDict, total=False):
    """
    Define the optional extension metadata structure.

    See also:
        This is documented in the :ref:`sphinx:ext-metadata` section of
        Sphinx's documentation.
    """

    version: str
    """
    A string that identifies the extension version.

    It is used for extension version requirement checking (see
    :confval:`sphinx:needs_extensions`) and informational purposes.
    If not given, "unknown version" is substituted.
    """

    env_version: int
    """
    An integer that identifies the version of env data structure if the
    extension stores any data to environment.

    It is used to detect the data structure has been changed from last build.
    The extensions have to increment the version when data structure has changed.
    If not given, Sphinx considers the extension does not stores any data
    to environment.
    """

    parallel_read_safe: bool
    """
    A boolean that specifies if parallel reading of source files can be used
    when the extension is loaded.

    It defaults to ``False``, i.e. you have to explicitly specify your extension
    to be parallel-read-safe after checking that it is.
    """

    parallel_write_safe: bool
    """
    A boolean that specifies if parallel writing of output files can be used
    when the extension is loaded.

    Since extensions usually don’t negatively influence the process, this
    defaults to True.
    """


class SphinxEvent(Enum):
    """
    Enumerate Sphinx core events.

    .. note:: Developer, add missing events as needed.

    See also:
        https://www.sphinx-doc.org/en/master/extdev/appapi.html#sphinx-core-events
    """

    CONFIG_INITED = "config-inited"
    BUILDER_INITED = "builder-inited"
    ENV_GET_OUTDATED = "env-get-outdated"
    ENV_BEFORE_READ_DOCS = "env-before-read-docs"
    ENV_PURGE_DOC = "env-purge-doc"
    SOURCE_READ = "source-read"
    OBJECT_DESCRIPTION_TRASFORM = "object-description-transform"
    DOCTREE_READ = "doctree-read"
    MISSING_REFERENCE = "missing-reference"
    WARN_MISSING_REFERENCE = "warn-missing-reference"
    DOCTREE_RESOLVED = "doctree-resolved"
    ENV_MERGE_INFO = "env-merge-info"
    ENV_UPDATED = "env-updated"
    ENV_CHECK_CONSISTENCY = "env-check-consistency"
    HTML_COLLECT_PAGES = "html-collect-pages"
    HTML_PAGE_CONTEXT = "html-page-context"
    LINKCHECK_PROCESS_URI = "linkcheck-process-uri"
    BUILD_FINISHED = "build-finished"


class HtmlPage(NamedTuple):
    """
    Expected tuple by Sphinx when collecting HTML pages.
    """

    pagename: str
    context: Dict[str, Any]
    templatename: str


class SphinxDomainObjectDescription(NamedTuple):
    """
    Identify something of interest for search results, for instance.

    Sphinx uses a lot of tuples.  This one is documented at
    :meth:`sphinx.domains.Domain.get_objects`.
    """

    name: str
    """
    Fully qualified name.
    """

    dispname: str
    """
    Name to display when searching/linking.
    """

    type: str
    """
    Object type name, which may or may not match role and directive names.
    """

    docname: str
    """
    Document name where it is to be found.
    """

    anchor: str
    """
    The anchor name for the object.
    """

    priority: int
    """
    How "important" the object is (determines placement in search results).

    One of:

    ``1``
        Default priority (placed before full-text matches).
    ``0``
        Object is important (placed before default-priority objects).
    ``2``
        Object is unimportant (placed after full-text matches).
    ``-1``
        Object should not show up in search at all.
    """


class SphinxGeneralIndexEntry(NamedTuple):
    """
    An entry in the general index.

    This tuple is documented in :meth:`sphinx.domains.Index.generate`.
    """

    entrytype: str
    """
    One of "single", "pair", "double", "triple".
    """

    entryname: str
    """
    Index entry name.

    As an example, in the case of glossary definitions with multiple terms
    (synonyms, for instance), each term gets its index entry and the entryname
    is the term.
    """

    targetid: str

    mainname: str

    key: Optional[str]
    """
    Categorization characters (usually a single character) for general index page.
    """
