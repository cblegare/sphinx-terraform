from __future__ import annotations

import re

import pytest
from sphinx.application import Sphinx


@pytest.mark.sphinx(testroot="basic")
def test_tf(built_index_html: str, status, warning):
    html = (
        r"<h1>test-basic<a "
        r'class="headerlink" '
        r'href="#test-basic" '
        r'title="Permalink to this headline">¶'
        r"</a></h1>"
    )

    assert re.search(html, built_index_html, re.DOTALL)


@pytest.mark.sphinx(testroot="md-comment-from-md-document")
def test_md_in_md(built_index_html: str, status, warning):
    html = (
        r"<p>Terraform documentation in Markdown</p>\s*"
        r"<p>.+<a .+>hyperlink</a></p>"
    )

    assert re.search(html, built_index_html, re.DOTALL)


@pytest.mark.sphinx(testroot="rst-comment-from-rst-document")
def test_rst_in_rst(built_index_html: str, status, warning):
    html = (
        r"<p>Terraform documentation in RestructuredText</p>\s*"
        r"<p>.+<a .+>hyperlink</a></p>"
    )

    assert re.search(html, built_index_html, re.DOTALL)


@pytest.mark.sphinx(testroot="md-directive-in-rst-document")
def test_md_in_rst(built_index_html: str, status, warning):
    html = (
        r"<p>Terraform documentation in Markdown</p>\s*"
        r"<p>.+<a .+>hyperlink</a></p>"
    )

    assert re.search(html, built_index_html, re.DOTALL)


@pytest.mark.sphinx(
    testroot="md-directive-in-rst-document",
    confoverrides={"terraform_comment_markup": "rst"},
)
def test_md_in_rst_force_conf(built_index_html: str, status, warning):
    html = (
        r"<p>Terraform documentation in Markdown</p>\s*"
        r"<p>.+<a .+>hyperlink</a></p>"
    )

    assert re.search(html, built_index_html, re.DOTALL)


@pytest.mark.sphinx(testroot="rst-directive-in-md-document")
def test_rst_in_md(built_index_html: str, status, warning):
    html = (
        r"<p>Terraform documentation in RestructuredText</p>\s*"
        r"<p>.+<a .+>hyperlink</a></p>"
    )

    assert re.search(html, built_index_html, re.DOTALL)


@pytest.mark.sphinx(
    testroot="rst-directive-in-md-document",
    confoverrides={"terraform_comment_markup": "md"},
)
def test_rst_in_md_force_conf(built_index_html: str, status, warning):
    html = (
        r"<p>Terraform documentation in RestructuredText</p>\s*"
        r"<p>.+<a .+>hyperlink</a></p>"
    )

    assert re.search(html, built_index_html, re.DOTALL)


@pytest.mark.sphinx(testroot="config-terraform_comment_markup-md")
def test_config_terraform_comment_markup_md(
    built_index_html: str, status, warning
):
    html = (
        r"<p>Terraform documentation in Markdown</p>\s*"
        r"<p>.+<a .+>hyperlink</a></p>"
    )

    assert re.search(html, built_index_html, re.DOTALL)


@pytest.mark.sphinx(testroot="config-terraform_comment_markup-rst")
def test_config_terraform_comment_markup_rst(
    built_index_html: str, status, warning
):
    html = (
        r"<p>Terraform documentation in RestructuredText</p>\s*"
        r"<p>.+<a .+>hyperlink</a></p>"
    )

    assert re.search(html, built_index_html, re.DOTALL)


@pytest.fixture()
def built_index_html(app: Sphinx) -> str:
    app.builder.build_all()

    content = (app.outdir / "index.html").read_text()
    return content
