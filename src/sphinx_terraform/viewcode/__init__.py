"""
Similar to :mod:`sphinx.ext.viewcode`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterator

from docutils import nodes
from docutils.nodes import Element, Node
from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.environment import BuildEnvironment
from sphinx.transforms.post_transforms import SphinxPostTransform
from sphinx.util import status_iterator
from sphinx.util.logging import getLogger
from sphinx.util.nodes import make_refnode

from sphinx_terraform import __version__, get_builder
from sphinx_terraform.i18n import t_, t__
from sphinx_terraform.markup import TerraformDomain
from sphinx_terraform.sphinxapi import ExtensionMetadata, HtmlPage
from sphinx_terraform.terraform import make_identifier
from sphinx_terraform.viewcode.html import HtmlWriter

OUTPUT_DIRNAME = "_terraform_files"

log = getLogger(__name__)


def setup(app: Sphinx) -> ExtensionMetadata:
    app.require_sphinx("3")

    app.connect("env-purge-doc", env_purge_doc)
    app.connect("doctree-read", doctree_read)
    app.connect("html-collect-pages", collect_pages)
    app.add_post_transform(ViewcodeAnchorToggler)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def env_purge_doc(app: Sphinx, env: BuildEnvironment, docname: str) -> None:
    domain = TerraformDomain.get_instance(app)
    domain.store.purge_usage(docname)


class viewcode_anchor(Element):
    """
    A sentinel node for viewcode anchors.

    Nodes of this type will be

    *   converted to anchors in supported builders or
    *   removed otherwise.

    This happens as a post transform phase.
    See also :class:`~ViewcodeAnchorToggler`.
    """


def doctree_read(app: Sphinx, doctree: Node) -> None:
    """
    Find HCL documentation and gather associated source code.

    Args:
        app:
            From the app we get the environment, our storage (cache).
        doctree:
            The document tree we will traverse in order to find HCL signatures.
    """
    domain = TerraformDomain.get_instance(app)

    writer = HtmlWriter(domain, Path(OUTPUT_DIRNAME))

    for signature_node in _gen_hcl_signatures(doctree):
        module = signature_node.get("module")
        signature = signature_node.get("signature", None)

        if module and signature:
            entry = domain.register(module, signature)
            signature_node += viewcode_anchor(
                reftarget=str(writer.make_pagename(entry.file)),
                refid=make_identifier(entry.signature),
                refdoc=domain.env.docname,
            )


class ViewcodeAnchorToggler(SphinxPostTransform):
    """
    Convert or remove :class:`~viewcode_anchor`.
    """

    default_priority = 100

    def run(self, **kwargs: Any) -> None:
        if is_supported_builder(self.app):
            self.convert_viewcode_anchors()
        else:
            self.remove_viewcode_anchors()

    def convert_viewcode_anchors(self) -> None:
        for node in self.document.findall(viewcode_anchor):
            anchor = nodes.inline("", t_("[source]"), classes=["viewcode-link"])
            refnode = make_refnode(
                get_builder(self.app),
                node["refdoc"],
                node["reftarget"],
                node["refid"],
                anchor,
            )
            node.replace_self(refnode)

    def remove_viewcode_anchors(self) -> None:
        for node in list(self.document.findall(viewcode_anchor)):
            node.parent.remove(node)


def is_supported_builder(app: Sphinx) -> bool:
    if not isinstance(app.builder, Builder):
        return False

    if app.builder.format != "html":
        return False
    elif app.builder.name == "singlehtml":
        return False
    elif (
        app.builder.name.startswith("epub")
        and not app.builder.config.viewcode_enable_epub
    ):
        return False
    else:
        return True


def collect_pages(app: Sphinx) -> Iterator[HtmlPage]:
    domain = TerraformDomain.get_instance(app)
    writer = HtmlWriter(domain, Path(OUTPUT_DIRNAME))

    tf_files = sorted(domain.store.get_documented_files())

    for tf_file in status_iterator(
        tf_files,
        t__("highlighting code..."),
        "blue",
        len(tf_files),
        app.verbosity,
        str,
    ):
        code_page = writer.gen_sourcecode_html(tf_file)
        yield code_page

    index_page = writer.gen_root_module_index()
    yield index_page


def _gen_hcl_signatures(node: Node) -> Iterator[addnodes.desc_signature]:
    def condition(candidate: Node) -> bool:
        return (
            isinstance(candidate, addnodes.desc)
            and candidate.get("domain") == "tf"
        )

    description_node: addnodes.desc
    for description_node in node.findall(condition=condition):
        signature_node: addnodes.desc_signature
        for signature_node in description_node.findall(  # type: ignore # error: <nothing> has no attribute "findall" ?!?
            addnodes.desc_signature
        ):
            yield signature_node
