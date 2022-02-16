from __future__ import annotations

import os
import sys
from pathlib import Path
from types import TracebackType
from typing import TYPE_CHECKING, Any, Callable, List, Optional, Type, Union

from sphinx.util.logging import getLogger

from sphinx_terraform import get_builder, get_highlighter
from sphinx_terraform.i18n import t_
from sphinx_terraform.markup import TerraformDomain
from sphinx_terraform.sphinxapi import HtmlPage
from sphinx_terraform.terraform import TerraformModule, make_identifier

if TYPE_CHECKING or sys.version_info < (3, 8, 0):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


log = getLogger(__name__)


class HtmlWriter:
    def __init__(self, domain: TerraformDomain, output_dirname: Path):
        self._domain = domain
        self._output_dirname = Path(output_dirname)

        self._highlighter = get_highlighter(domain.env)

    def make_pagename(self, tf_file: Path) -> Path:
        page_name = self._output_dirname.joinpath(
            self.get_symbolic_path(tf_file)
        )
        return page_name

    def gen_sourcecode_html(self, tf_file: Path) -> HtmlPage:
        code = self._domain.store.get_code(tf_file)
        pagename = self.make_pagename(tf_file)
        highlighted_code = self.highlight_hcl_code(code)

        annotated_highlighted_code = self._add_backlinks_to_documentation(
            highlighted_code, tf_file
        )

        log.debug(f"Emitting HTML for {tf_file}")
        context = {
            "title": self.get_symbolic_path(tf_file),
            "body": (
                t_("<h1>Source code for %s</h1>")
                % self.get_symbolic_path(tf_file)
                + "\n"
                + "\n".join(annotated_highlighted_code)
            ),
        }
        return HtmlPage(str(pagename), context, "page.html")

    def gen_root_module_index(self) -> HtmlPage:
        tree_of_modules = self._get_tree_of_modules_and_files()

        pagename = self._output_dirname.joinpath("index")

        def file_to_url(tf_file: Path) -> str:
            return self._urito(
                pagename,
                self._output_dirname.joinpath(self.get_symbolic_path(tf_file)),
            )

        html_list = list(
            self._tree_of_modules_to_html_list(tree_of_modules, file_to_url)
        )

        context = {
            "title": t_("Overview: module code"),
            "body": (
                t_("<h1>All modules for which code is available</h1>")
                + "\n"
                + "\n".join(html_list)
            ),
        }
        return HtmlPage(str(pagename), context, "page.html")

    def highlight_hcl_code(self, code: List[str]) -> List[str]:
        lexer = "tf"

        highlighted = self._highlighter.highlight_block(
            os.linesep.join(code), lexer, linenos=False
        )
        highlighted_lines = highlighted.splitlines()
        before, after = highlighted_lines[0].split("<pre>")
        highlighted_lines[0:1] = [before + "<pre>", after]

        return highlighted_lines

    def get_symbolic_path(self, tf_file: Path) -> Path:
        """
        Return the path to a file name starting with the root module's name.
        """
        module = self._domain.store.get_module(tf_file)

        return Path(module.fullname, tf_file.relative_to(module.path))

    def _add_backlinks_to_documentation(
        self,
        highlighted_code: List[str],
        tf_file: Path,
    ) -> List[str]:
        pagename = self.make_pagename(tf_file)
        for line_number, line_of_code in enumerate(highlighted_code):
            if line_of_code.startswith("<span"):
                first_line_of_code = line_number
                break
        else:
            first_line_of_code = 0

        module = self._domain.store.get_module(tf_file)

        for signature, entry in self._domain.store.get_definitions(
            tf_file=tf_file
        ).items():
            for docname_where_documented in entry.usages:
                backlink = (
                    f"{self._urito(pagename, docname_where_documented)}"
                    "#"
                    f"{make_identifier(signature, module)}"
                )
                definition_starting_line = (
                    entry.code.start_position.line + first_line_of_code
                )
                definition_ending_line = (
                    entry.code.end_position.line + first_line_of_code
                )
                highlighted_code[definition_starting_line] = "".join(
                    [
                        f'<div class="viewcode-block" id="{make_identifier(signature)}">',
                        f'<a class="viewcode-back" href="{backlink}">',
                        f"{t_('[docs]')}</a>{highlighted_code[definition_starting_line]}",
                    ]
                )
                highlighted_code[definition_ending_line] += "</div>"
        return highlighted_code

    def _urito(
        self,
        from_page: Union[str, Path],
        to_page: Union[str, Path],
        typ: Optional[str] = None,
    ) -> str:
        return get_builder(self._domain.env).get_relative_uri(
            str(from_page), str(to_page), typ  # type: ignore # typ is wrongly typed upstream
        )

    def _get_tree_of_modules_and_files(self) -> TreeOfModulesAndFiles:
        known = set()
        result: TreeOfModulesAndFiles = {}

        documented_files = sorted(self._domain.store.get_documented_files())

        for tf_file in documented_files:
            module = self._domain.store.get_module(tf_file)
            stack = result
            if module in known:
                continue
            known.add(module)

            for part in module.fullname.split("/")[1:]:
                if part not in stack:
                    stack[part] = {}  # type: ignore
                stack = stack[part]  # type: ignore

            stack["__tf_files__"] = list(
                self._domain.store.get_documented_files(module)
            )
            stack["__tf_module__"] = module

        return result

    def _tree_of_modules_to_html_list(
        self,
        _tree: TreeOfModulesAndFiles,
        file_to_url: Callable[[Path], str],
    ) -> List[str]:
        html_parts: List[str] = []
        html = Html(html_parts)

        def _recurse(_tree: TreeOfModulesAndFiles) -> None:
            with html.tag("ul"):
                module = _tree["__tf_module__"]
                with html.tag("li"):
                    with html.tag("strong"):
                        html.append(str(module))

                files = _tree.get("__tf_files__", [])
                if files:
                    with html.tag("ul"):
                        for filepath in files:
                            with html.tag("li"):
                                with html.tag("a", href=file_to_url(filepath)):
                                    html.append(
                                        str(self.get_symbolic_path(filepath))
                                    )

                for subtree in [
                    child
                    for key, child in _tree.items()
                    if not isinstance(key, str) and child
                ]:
                    _recurse(subtree)  # type: ignore

        _recurse(_tree)
        return html_parts


class TreeOfModulesAndFiles(TypedDict, total=False):
    __tf_files__: List[Path]
    __tf_module__: TerraformModule


class Html:
    class _inner(object):
        def __init__(self, tagger: Html, tag: str, **attributes: str):
            self.tagger = tagger
            self.tag = tag
            self.attributes = attributes

        def __enter__(self) -> None:
            if self.attributes:
                attribute_str = " ".join(
                    f'{key}="{value}"' for key, value in self.attributes.items()
                )
                self.tagger.append(f"<{self.tag} {attribute_str}>")
            else:
                self.tagger.append(f"<{self.tag}>")
            self.tagger.indent_count += 1

        def __exit__(
            self,
            exctype: Optional[Type[BaseException]],
            excvalue: Optional[BaseException],
            traceback: Optional[TracebackType],
        ) -> None:
            self.tagger.indent_count -= 1
            self.tagger.append(f"</{self.tag}>")

    def __init__(
        self,
        container: List[str],
        initial_indent_count: int = 0,
        indent_increment: str = "  ",
    ):
        self.container = container
        self.indent_count = initial_indent_count
        self.indent_increment = indent_increment

    def tag(self, tag: str, **attributes: str) -> Any:
        return self._inner(self, tag, **attributes)

    def append(self, some_html: str) -> None:
        self.container.append(
            f"{self.indent_increment * self.indent_count}{some_html}"
        )
