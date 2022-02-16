from __future__ import annotations

import re
import sys
from collections import defaultdict
from enum import Enum
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Iterator,
    List,
    NamedTuple,
    Optional,
    Set,
    Tuple,
    Type,
    TypeVar,
    Union,
)

from sphinx.environment import BuildEnvironment
from sphinx.util.logging import getLogger

from sphinx_terraform import SphinxTerraformError, get_config_terraform_sources
from sphinx_terraform.code import CodePosition, CodeSpan
from sphinx_terraform.i18n import t__

if TYPE_CHECKING or sys.version_info < (3, 8, 0):
    from typing_extensions import Protocol
else:
    from typing import Protocol

log = getLogger(__name__)

_TerraformModule = TypeVar("_TerraformModule", bound="TerraformModule")


class TerraformModule(NamedTuple):
    """
    Represent a Terraform module.

    A Terraform module is a directory containing Terraform definition files.
    and other modules.

    This implementation extends the meaning of Terraform modules for our
    documentation purposes by giving the each module a :attr:`~name` and
    a :attr:`~fullname`.

    The top-most module is called the **root** module.

    The root module name comes from the documentation configuration. See
    :confval:`terraform_sources`.  Its *fullname* is the same as its
    name.

    Sub modules are named by their directory name and their *fullname* is
    derived from their parents names using slashes (``/``) as separators.

    Example:
        .. code-block:: text

            └── root_module/
                ├── main.tf
                ├── first_sub_module/
                │   ├── main.tf
                │   └── sub_sub_module/
                └── second_sub_module/
                    └── main.tf

        defines the following module fullnames:

        *   ``root_module``
        *   ``root_module/first_sub_module``
        *   ``root_module/first_sub_module/sub_sub_module``
        *   ``root_module/second_sub_module``

    .. tip:: In Terraform, **files** have no structural meaning.
    """

    root_name: str
    root_path: Path
    name: str
    path: Path
    fullname: str

    @classmethod
    def from_module_path(
        cls: Type[_TerraformModule],
        env: BuildEnvironment,
        module_path: Union[str, Path] = "",
    ) -> _TerraformModule:
        if not module_path:
            return cls.from_module_parts(env)
        else:
            root, *rest = Path(module_path).parts
            return cls.from_module_parts(env, root, "/".join(rest))

    @classmethod
    def from_module_parts(
        cls: Type[_TerraformModule],
        env: BuildEnvironment,
        root_module_name: Optional[str] = None,
        submodule: Union[str, Path] = "",
    ) -> _TerraformModule:
        root = cls._find_root(env, root_module_name)

        if not submodule:
            return root

        path = Path(submodule)
        if not path.is_absolute():
            path = root.path.joinpath(path)

        name = str(path.relative_to(root.path))
        fullname = f"{root.name}/{name}"

        return cls(root.name, root.path, name, path.resolve(), fullname)

    @classmethod
    def _find_root(
        cls: Type[_TerraformModule],
        env: BuildEnvironment,
        root_module_name: Optional[str] = None,
    ) -> _TerraformModule:
        sources = get_config_terraform_sources(env)
        if len(sources) == 1:
            root_name, root_path = next(iter(sources.items()))
        elif root_module_name is None:
            raise SphinxTerraformError(
                t__("Can't determine the proper terraform source to use.")
            )
        else:
            try:
                root_name = root_module_name
                root_path = sources[root_name]
            except KeyError as e:
                raise SphinxTerraformError(
                    t__(
                        "Unknown Terraform source '%s'. "
                        "Please review 'terraform_sources' in conf.py."
                    )
                    % root_module_name
                ) from e
        return cls(
            root_name,
            root_path.resolve(),
            root_name,
            root_path.resolve(),
            root_name,
        )

    def __str__(self) -> str:
        return self.fullname


class HclSignature(Protocol):
    """
    Signature of a Hashicorp Configuration Language (HCL) body element.

    This does not consider anything regarding a block's definition body,
    only its signature.  All signature **must** be defined on a single
    line of HCL code, as per the grammar.

    In the context of Terraform, which is a software that uses HCL by default
    for its configuration, HCL signatures are **unique in a given module**.
    Even sub module can have some signature equivalent to one of its parents
    ones without conflicts.

    Body elements can be one of the following.

    **Blocks**
        Blocks are multi line definitions.  Their pseudo-grammar is

        .. code-block:: bnf

            Block = Identifier (StringLit|Identifier)* "{" Newline Body "}" Newline;

        A block's *signature* is anything **before** the opening scope
        (``{``)

    **One line blocks**
        One line blocks are the same as blocks but on a single line,
        and thus can only have a simple definition body.  Their grammar is

        .. code-block:: bnf

            OneLineBlock = Identifier (StringLit|Identifier)* "{" (Identifier "=" Expression)? "}" Newline;

        A one line block's *signature* is anything **before** the opening
        scope (``{``), just like multi-line blocks.

    **Attributes**
        Attributes are simple key-value pairs.  Their grammar is

        .. code-block:: bnf

            Attribute = Identifier "=" Expression Newline;

        In this case, the signature would only include the left operand of
        the assignation, labeled ``Identifier`` above.

    In Terraform, the first **Identifier** of **blocks** and
    **one line blocks** is the signature's :attr:`~type` and zero (0) or
    more **labels** (:attr:`~labels`) based on the remaining **Identifiers**.
    **Attributes** have an implicit type and one (1) label.

    See also:
        `The HCL syntax`_

    .. _The HCL syntax: https://github.com/hashicorp/hcl/blob/main/hclsyntax/spec.md
    """

    @property
    def type(self) -> TerraformBlockType:
        """
        The Terraform object type (``resource``, ``data``, etc).
        """
        ...

    @property
    def labels(self) -> List[str]:
        """
        The object's labels, the amount of which depends on the :attr:`~type`.
        """
        ...

    def regex(self) -> Union[str, re.Pattern[str]]:
        """
        A regex that will reliably match the right code signature in a line.

        See also:
            The :func:`~regex` implementation that covers most cases.
        """
        ...

    def __repr__(self) -> str:
        """
        A string representation of
        Returns:

        """
        ...

    def __str__(self) -> str:
        """
        A string representation of
        Returns:

        """
        ...


def regex(self: HclSignature) -> Union[str, re.Pattern[str]]:
    """
    Return a regex that matches the signature reliably within a module.

    The regex will match a line of HCL code

    *   starting with 0 or more whitespaces,
    *   followed by an identifier without quotes
        (:attr:`sphinx_terraform.terraform.HclSignature.type`),
    *   followed by 1 or more non-newline whitespaces,
    *   followed by the signature's labels
        (:attr:`sphinx_terraform.terraform.HclSignature.labels`),
        possibily between double quotes `"` and
        separated by 1 or more non-newline whitespaces,
    *   followed by 1 or more non-newline whitespaces,
    *   followed by the `{` character and
    *   ending with the newline character.

    In Terraform, signatures are unique in a given module, hence this
    implementation is only reliable when scoped within a module.

    Args:
        self:
            The HCL block signature object we want to find in HCL code.

    Returns:
        Compiled regular expression.
    """
    # Use a double negation to match non-newline whitespace characters.
    # That is
    #   - Not
    #     - one of
    #       - Non-whitespace
    #       - Carriage return character
    #       - New line character
    non_newline_whitespace = r"[^\S\r\n]"

    signature_regex_inner = rf"{non_newline_whitespace}+".join(
        [
            # the type do not have quotes
            self.type.value,
            *[
                # labels can be between double quotes
                rf"(\"{label}\"|{label})"
                for label in self.labels
            ],
            # end with the block opening bracket
            "{.*",
        ]
    )

    # Enclose with accepted leading and trailing whitespace characters
    signature_regex = rf"^\s*{signature_regex_inner}$"
    return signature_regex


def _repr(self: HclSignature) -> str:
    """
    Make a valid Python code string that create an equivalent instance.
    """
    labels_within_quotes = [f"'{label}'" for label in self.labels]
    return (
        f"{self.__class__.__name__}("
        f"'{self.type}', "
        f"{', '.join(labels_within_quotes)}"
        f")"
    )


def _str(self: HclSignature) -> str:
    return f"{'.'.join(self.labels)}"


def make_identifier(
    signature: HclSignature, module: Optional[TerraformModule] = None
) -> str:
    """
    Create an URL friendly identifier string from a signature.

    This notion of identifier string does not exist in Terraform per se,
    since we do factor in the definituon's module.

    The below example illustrates how the identifier is built.

    Example:
        Given the following definitions within the module "mod":

        .. code-block:: terraform

            # in submodule "mod", in any file

            resource "null_resource" "some-name" {
            }

            data "null_data" "other-name" {
            }

        The identifiers would be

        .. code-block:: text

            mod/resource-null_resource.some-name

            mod/data-null_data.other-name

        >>> resource = TerraformResourceSignature("null", "resource", "some-name")
        >>> make_identifier(resource)
        'resource-null_resource.some-name'

    Args:
        signature:
            The HCL block signature for the definition we create an identifier.
        module:
            An optional module name.

    Returns:
        URL friendly identifier.
    """
    base_identifier = f"{signature.type.value}-{'.'.join(signature.labels)}"

    if module:
        return f"{module.name}/{base_identifier}"
    else:
        return base_identifier


class TerraformBlockType(Enum):
    DATA = "data"
    VARIABLE = "variable"
    MODULE = "module"
    OUTPUT = "output"
    PROVIDER = "provider"
    REQUIREMENT = "requirement"
    RESOURCE = "resource"


class HclDefinition(NamedTuple):
    """
    Define a HCL object.

    We use this because many definitions could have identical signature
    scattered across different modules (folders).
    """

    signature: HclSignature
    """
    Identify a definition, the signature is the definition *header*.
    """

    file: Path
    """
    HCL file where this definition is found.
    """

    doc_code: CodeSpan
    """
    HCL code section where this is documented.
    """

    signature_code: CodeSpan
    """
    HCL code section where this is defined.
    """

    body_code: CodeSpan
    """
    HCL code section where this is defined.
    """

    usages: Set[str]
    """
    Document name where this definition is referenced.
    """

    @property
    def code(self) -> CodeSpan:
        """
        Return where to find the whole code of this definition.

        We consider that the docstring, signature and body are contiguous.
        """
        return CodeSpan(
            self.doc_code.start_position, self.body_code.end_position
        )


class TerraformResourceSignature(NamedTuple):
    provider: str
    kind: str
    name: str

    @property
    def type(self) -> TerraformBlockType:
        return TerraformBlockType.RESOURCE

    @property
    def labels(self) -> List[str]:
        return [f"{self.provider}_{self.kind}", self.name]

    regex = regex  # type: ignore # Assigning methods is unsupported by mypy

    __repr__ = _repr  # type: ignore # Assigning methods is unsupported by mypy

    __str__ = _str  # type: ignore # Assigning methods is unsupported by mypy


class TerraformDataSignature(NamedTuple):
    provider: str
    kind: str
    name: str

    @property
    def type(self) -> TerraformBlockType:
        return TerraformBlockType.DATA

    @property
    def labels(self) -> List[str]:
        return [f"{self.provider}_{self.kind}", self.name]

    regex = regex  # type: ignore # Assigning methods in NamedTuple is unsupported by mypy

    __repr__ = _repr  # type: ignore # Assigning methods in NamedTuple is unsupported by mypy

    __str__ = _str  # type: ignore # Assigning methods is unsupported by mypy


class TerraformModuleSignature(NamedTuple):
    name: str

    @property
    def type(self) -> TerraformBlockType:
        return TerraformBlockType.MODULE

    @property
    def labels(self) -> List[str]:
        return [self.name]

    regex = regex  # type: ignore # Assigning methods is unsupported by mypy

    __repr__ = _repr  # type: ignore # Assigning methods is unsupported by mypy

    __str__ = _str  # type: ignore # Assigning methods is unsupported by mypy


class TerraformVariableSignature(NamedTuple):
    name: str

    @property
    def type(self) -> TerraformBlockType:
        return TerraformBlockType.VARIABLE

    @property
    def labels(self) -> List[str]:
        return [self.name]

    regex = regex  # type: ignore # Assigning methods is unsupported by mypy

    __repr__ = _repr  # type: ignore # Assigning methods is unsupported by mypy

    __str__ = _str  # type: ignore # Assigning methods is unsupported by mypy


class TerraformOutputSignature(NamedTuple):
    name: str

    @property
    def type(self) -> TerraformBlockType:
        return TerraformBlockType.OUTPUT

    @property
    def labels(self) -> List[str]:
        return [self.name]

    regex = regex  # type: ignore # Assigning methods is unsupported by mypy

    __repr__ = _repr  # type: ignore # Assigning methods is unsupported by mypy

    __str__ = _str  # type: ignore # Assigning methods is unsupported by mypy


_TerraformStore = TypeVar("_TerraformStore", bound="TerraformStore")


class TerraformStore:
    def __init__(self, data: Dict[Any, Any]) -> None:
        """
        Private constructor. Use :meth:`~from_build_env` instead.

        Args:
            data: Existing data, probably read from cache.
        """
        self.data: Dict[TerraformModule, ModuleData] = data

    @classmethod
    def initial_data(cls: Type[_TerraformStore]) -> Dict[Any, Any]:
        return defaultdict(ModuleData.new)

    def register(
        self,
        module: TerraformModule,
        signature: HclSignature,
        docname: str,
    ) -> HclDefinition:
        """
        Register a definition signature for a given module.

        This signals that a definition is documented. It makes sure we know
        about this HCL definition within the local cache, then registers
        the docname in its know documentation usages.

        Args:
            module:
                The module where this definition is found.  Multiple
                definitions should be unique within a module.
            signature:
                A signature identifies a definition.
            docname:
                The document where this signature is documented.

        Raises:
            sphinx_terraform.SphinxTerraformError: No definition could
                be found matching the signature within this module.

        Returns
            The registered definition.
        """
        hcl_definition = self.data[module].find_definition(module, signature)
        hcl_definition.usages.add(docname)
        return hcl_definition

    def purge_usage(self, usage_source: str) -> None:  # noqa
        for module in self.data.values():
            if not isinstance(module, TerraformModule):
                continue
            for signature in self.data[module].definitions.keys():
                entry = self.data[module].definitions[signature]
                if usage_source in entry.usages:
                    entry.usages.remove(usage_source)
                if not entry.usages:
                    del self.data[module].definitions[signature]

    def get_code(self, tf_file: Path) -> List[str]:
        module = self.get_module(tf_file)
        return self.data[module].get_code(tf_file)

    def get_module(self, tf_file: Path) -> TerraformModule:
        module_path = tf_file.parent
        for module in self.data:
            if module.path == module_path:
                return module
        else:
            raise SphinxTerraformError(f"No module found at '{module_path}'.")

    def get_definitions(
        self,
        module: Optional[TerraformModule] = None,
        tf_file: Optional[Path] = None,
    ) -> Dict[HclSignature, HclDefinition]:
        module = self.get_module(tf_file) if tf_file else module

        def gen_definitions(
            module: Optional[TerraformModule],
        ) -> Iterator[Tuple[HclSignature, HclDefinition]]:
            if module:
                yield from self.data[module].definitions.items()
            else:
                for module in self.data:
                    yield from self.data[module].definitions.items()

        def condition(entry: HclDefinition) -> bool:
            return entry.file == tf_file if tf_file else True

        return {
            signature: definition
            for signature, definition in gen_definitions(module)
            if condition(definition)
        }

    def get_module_files(self) -> List[Tuple[TerraformModule, Path]]:
        return sorted(
            [
                (module, filepath)
                for module in self.data
                for filepath in self.data[module].get_documented_files()
            ]
        )

    def get_documented_files(
        self, module: Optional[TerraformModule] = None
    ) -> Set[Path]:
        def gen_files() -> Iterator[Path]:
            if module:
                yield from self.data[module].get_documented_files()
            else:
                for module_data in self.data.values():
                    yield from module_data.get_documented_files()

        return set(tf_file for tf_file in gen_files())

    def get_documentation(self, definition: HclDefinition) -> List[str]:
        start_line = definition.doc_code.start_position.line
        end_line = definition.doc_code.end_position.line

        code_with_doc = self.get_code(definition.file)[start_line:end_line]

        documentation = extract_docstring_from_comment(code_with_doc)
        return documentation


_ModuleData = TypeVar("_ModuleData", bound="ModuleData")


class ModuleData(NamedTuple):
    """
    What we store in the build environment for a given Terraform module.

    Here is a JSON-like representation:

    .. code-block:: text

        {
            code: {
                Path: [
                    # lines of code
                ]
            },
            definitions: {
                HclBlockSignature: HclSignatureDefinition
            }
        }
    """

    code: Dict[Path, List[str]]
    """
    Cache of raw HCL code indexed by file path.
    """

    definitions: Dict[HclSignature, HclDefinition]
    """
    Found block definitions indexed by their signature.
    """

    @classmethod
    def new(cls: Type[_ModuleData]) -> _ModuleData:
        return cls(defaultdict(list), dict())

    def find_definition(
        self, module: TerraformModule, signature: HclSignature
    ) -> HclDefinition:
        """
        Look for a Terraform definition in all HCL files of a module.

        We use an internal cache that is pickled with the Sphinx environment.
        If the cache misses, we parse the code to find the definition.

        Args:
            signature:
                A signature identifies a definition.

        Raises:
            sphinx_terraform.SphinxTerraformError: No definition could
                be found matching the signature within this module.

        Returns:
            The found definition.
        """
        log.debug(f"Looking for definition of {repr(signature)}.")
        try:
            hcl_definition = self.definitions[signature]
            log.debug(f"Found definition of {repr(signature)} in cache.")
        except KeyError:
            for tf_file in module.path.glob("*.tf"):
                hcl_definition = self._find_definition(signature, tf_file)  # type: ignore
                if not hcl_definition:
                    continue
                log.debug(f"Caching definition of {repr(signature)}.")
                self.definitions[signature] = hcl_definition
                return hcl_definition
            else:
                raise SphinxTerraformError(
                    f"Definition not found for {repr(signature)} in module {module}."
                )
        return hcl_definition

    def get_definitions(
        self, tf_file: Optional[Path] = None
    ) -> Dict[HclSignature, HclDefinition]:
        """
        Make a mapping of known HCL definitions.

        Args:
            tf_file:
                Optionally filter for a specific file.

        Returns:
            The returned dictionary is created on each call, thus removing
            items from it won't remove them from this store.
        """

        def condition(entry: HclDefinition) -> bool:
            return entry.file == tf_file if tf_file else True

        return {
            signature: entry
            for signature, entry in self.definitions.items()
            if condition(entry)
        }

    def get_documentation(self, signature: HclSignature) -> List[str]:
        definition = self.definitions[signature]

        start_line = definition.doc_code.start_position.line
        end_line = definition.doc_code.end_position.line
        code_with_doc = self.get_code(definition.file)[start_line:end_line]

        documentation = extract_docstring_from_comment(code_with_doc)
        return documentation

    def get_code(self, tf_file: Path) -> List[str]:
        if tf_file not in self.code:
            log.debug(f"Putting code from {tf_file} in cache.")
            self.code[tf_file] = tf_file.read_text().splitlines()
        raw_code = self.code[tf_file]
        return raw_code

    def get_documented_files(self) -> Set[Path]:
        return set(entry.file for entry in self.definitions.values())

    def _find_definition(
        self, signature: HclSignature, tf_file: Path
    ) -> Optional[HclDefinition]:
        log.debug(f"Looking for definition of {repr(signature)} in files.")
        raw_code = self.get_code(tf_file)
        log.debug(f"Looking for definition of {repr(signature)} in {tf_file}.")
        found_code = self._find_definition_code(signature, raw_code)
        if not found_code:
            return None

        doc_code, signature_code, body_code = found_code
        log.debug(f"Found definition of {repr(signature)} in code.")
        hcl_definition = HclDefinition(
            signature,
            tf_file,
            doc_code,
            signature_code,
            body_code,
            set(),
        )
        return hcl_definition

    def _find_definition_code(
        self, signature: HclSignature, lines: List[str]
    ) -> Optional[Tuple[CodeSpan, CodeSpan, CodeSpan]]:
        signature_code = self._lookup_signature(signature, lines)

        if not signature_code:
            return None

        return self._find_whole_definition_code(signature_code, lines)

    def _find_whole_definition_code(
        self, signature_code: CodeSpan, lines: List[str]
    ) -> Tuple[CodeSpan, CodeSpan, CodeSpan]:
        # We found the signature, now let's try to climb up to the
        # last signature in order to find include a comment
        log.debug("Looking for beginning of definition, including comment.")
        begining_line = self._find_begining_of_documented_code(
            signature_code.start_position.line, lines
        )
        doc_code = CodeSpan(
            CodePosition(begining_line, 0),
            CodePosition(
                signature_code.start_position.line,
                signature_code.start_position.column,
            ),
        )
        log.debug(f"Found beginning of definition on line {begining_line}.")
        log.debug("Looking for definition body.")
        end_line = self._find_end_of_block(
            signature_code.start_position.line + 1, lines
        )
        body_code = CodeSpan(
            CodePosition(
                signature_code.end_position.line,
                signature_code.end_position.column,
            ),
            CodePosition(end_line, 0),
        )
        log.debug(f"Definition body ends on line {end_line}.")
        return doc_code, signature_code, body_code

    def _lookup_signature(
        self, signature: HclSignature, lines: List[str]
    ) -> Optional[CodeSpan]:
        signature_regex = signature.regex()
        for i, line_of_code in enumerate(lines):
            if re.match(signature_regex, line_of_code):
                log.debug(f"Found signature on line {i}.")
                signature_code = CodeSpan(
                    CodePosition(
                        i, len(line_of_code) - len(line_of_code.lstrip())
                    ),
                    CodePosition(i, len(line_of_code.rstrip())),
                )
                return signature_code
        else:
            # We could not find 'signature' in this code.
            return None

    def _find_begining_of_documented_code(
        self, start_line: int, lines: List[str]
    ) -> int:
        inspected_line = start_line - 1
        within_multiline_comment = False
        while inspected_line > 0:
            current_line = lines[inspected_line].strip()
            if current_line.startswith("*/"):
                log.debug(
                    f"Found the end of a multiline comment on line {inspected_line}."
                )
                within_multiline_comment = True
                inspected_line -= 1
                continue
            if within_multiline_comment and current_line.startswith("/*"):
                # we found the begining of a '/* ... */' comment.
                # That marks the start of the docstring, thus the end of
                # this search.
                log.debug(
                    f"Found the beginning of a multiline comment on line {inspected_line}."
                )
                return inspected_line
            if (
                current_line.startswith("#")
                or current_line.startswith("//")
                or within_multiline_comment
            ):
                # We found a single line comment.
                # Continue upward
                log.debug(
                    f"Found a single line comment on line {inspected_line}."
                )
                inspected_line -= 1
                continue
            # We found something else:
            # - empty line
            # - something that is not a comment
            log.debug(f"Found a non-comment line on line {inspected_line}.")
            return inspected_line + 1
        # We got to the top of the file. That's ok.
        log.debug("Went up to start of file.")
        return 0

    def _find_end_of_block(  # noqa
        self, start_line_within_block: int, all_lines: List[str]
    ) -> int:
        inspected_line = start_line_within_block
        # Within a block, there is one brace in the stack
        curly_brace_balance = 1

        while inspected_line < len(all_lines):
            log.debug(f"Looking for block delimiters on line {inspected_line}.")
            log.debug(f"Delimiter stack is {curly_brace_balance}")
            inspected_line_of_code = all_lines[inspected_line]
            for character in inspected_line_of_code:
                if character == "{":
                    curly_brace_balance += 1
                elif character == "}":
                    curly_brace_balance -= 1
                if curly_brace_balance == 0:
                    return inspected_line
            inspected_line += 1

        raise SphinxTerraformError(
            f"Found end of file when expecting closing scope opened before "
            f"line {start_line_within_block}"
        )


def extract_docstring_from_comment(  # noqa
    code_with_doc: List[str],
) -> List[str]:
    found_some_docs = False
    absolute_doc_indent = 0
    documentation = []
    for line in code_with_doc:
        if not found_some_docs:
            match = re.match(r"^[/\*\s#]* (?P<content>\S+.*)", line)
            if not match:
                continue
            content = match.group("content")
            absolute_doc_indent = len(line) - len(content)
            found_some_docs = True
        else:
            content = line[absolute_doc_indent:]
        if content and re.match(r"^[/\*\s#]+$", content):
            content = None

        if content is not None:
            documentation.append(content)
    return documentation
