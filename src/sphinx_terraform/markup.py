from __future__ import annotations

import re
import sys
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterable,
    List,
    NamedTuple,
    Optional,
    Tuple,
    Type,
    TypeVar,
    Union,
    cast,
)

import sphinx.parsers
from docutils import nodes, utils
from docutils.nodes import Element, Node, system_message
from docutils.parsers.rst import directives
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.addnodes import desc_signature
from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.directives import ObjectDescription
from sphinx.domains import Domain, Index, IndexEntry, ObjType
from sphinx.environment import BuildEnvironment
from sphinx.roles import XRefRole
from sphinx.util.logging import getLogger
from sphinx.util.nodes import make_refnode
from sphinx.util.typing import OptionSpec

from sphinx_terraform import (
    SphinxTerraformError,
    get_config_terraform_comment_markup,
    get_env,
)
from sphinx_terraform.i18n import t_
from sphinx_terraform.sphinxapi import (
    SphinxDomainObjectDescription,
    SphinxGeneralIndexEntry,
)
from sphinx_terraform.terraform import (
    HclDefinition,
    HclSignature,
    TerraformBlockType,
    TerraformDataSignature,
    TerraformModule,
    TerraformModuleSignature,
    TerraformOutputSignature,
    TerraformResourceSignature,
    TerraformStore,
    TerraformVariableSignature,
    make_identifier,
)

if TYPE_CHECKING or sys.version_info < (3, 8, 0):
    from typing_extensions import TypedDict
else:
    from typing import TypedDict


log = getLogger(__name__)

T = TypeVar("T", bound=str)


def parser_for_markup(markup_language_id: str) -> Type[sphinx.parsers.Parser]:
    markup_language_id = markup_language_id.lower()
    if markup_language_id in ("md", "myst", "markdown"):
        try:
            from myst_parser.sphinx_parser import MystParser

            return MystParser
        except ImportError as e:
            raise SphinxTerraformError(
                "In order to use Markdown in Terraform comments, "
                "you need the MyST parser. "
                "Install Sphinx-Terraform with the 'markdown' extra by "
                "issuing the 'pip install sphinx-terraform[markdown]' command. "
                "Then, enable it in your extensions.  "
                "See https://myst-parser.readthedocs.io/ for details"
            ) from e
    return sphinx.parsers.RSTParser


class TerraformObjectDirective(ObjectDescription[str]):
    option_spec: OptionSpec = {
        "noindex": directives.flag,
        "rootmodule": directives.unchanged,
        "module": directives.unchanged,
        "markup": directives.unchanged,
    }

    allow_nesting = False

    @property
    def _domain(self) -> TerraformDomain:
        return TerraformDomain.get_instance(self.env)

    @property
    def module(self) -> TerraformModule:
        if hasattr(self, "_hcl_mod"):
            return getattr(self, "_hcl_mod")  # type: ignore

        root_module = self.options.get("rootmodule", None)
        module = self.options.get("module", "")

        return TerraformModule.from_module_parts(self.env, root_module, module)

    @property
    def hcl_sig(self) -> Optional[HclSignature]:
        if hasattr(self, "_hcl_sig"):
            return getattr(self, "_hcl_sig")  # type: ignore
        return None

    @property
    def hcl_def(self) -> Optional[HclDefinition]:
        if hasattr(self, "_hcl_def"):
            return getattr(self, "_hcl_def")  # type: ignore
        return None

    @property
    def terraform_block_type(self) -> TerraformBlockType:
        possible_prefix = f"{self.domain}:"
        if self.name.startswith(possible_prefix):
            block_type_name = self.name[len(possible_prefix) :]
        else:
            block_type_name = self.name

        return TerraformBlockType(block_type_name)

    def parse_signature(self, signature: str) -> HclSignature:
        log.debug(f"Parsing signature '{signature}'.")
        block_type = self.terraform_block_type
        log.debug(f"Looking for signature parser for '{block_type.value}'.")

        stripped = signature.strip()
        if "/" in stripped:
            module_path, stripped = stripped.rsplit("/", maxsplit=1)
            self._hcl_mod = TerraformModule.from_module_path(
                self.env, module_path
            )

        parser = self._get_directive_signature_parser(block_type)
        parsed = parser(stripped)
        return parsed

    def _get_directive_signature_parser(
        self, block_type: TerraformBlockType
    ) -> Callable[[str], HclSignature]:
        parser = cast(
            Callable[[str], HclSignature],
            getattr(self, f"_parse_{block_type.value}_signature"),
        )
        return parser

    def _parse_resource_signature(self, signature: str) -> HclSignature:
        provider_kind, name = signature.split(".", maxsplit=1)
        provider, kind = provider_kind.split("_", maxsplit=1)
        return TerraformResourceSignature(provider, kind, name)  # type: ignore # Method assignation to NamedTuple messes with Mypy

    def _parse_data_signature(self, signature: str) -> HclSignature:
        provider_kind, name = signature.split(".", maxsplit=1)
        provider, kind = provider_kind.split("_", maxsplit=1)
        return TerraformDataSignature(provider, kind, name)  # type: ignore # Method assignation to NamedTuple messes with Mypy

    def _parse_module_signature(self, signature: str) -> HclSignature:
        return TerraformModuleSignature(signature)  # type: ignore # Method assignation to NamedTuple messes with Mypy

    def _parse_output_signature(self, signature: str) -> HclSignature:
        return TerraformOutputSignature(signature)  # type: ignore  # Method assignation to NamedTuple messes with Mypy

    def _parse_variable_signature(self, signature: str) -> HclSignature:
        return TerraformVariableSignature(signature)  # type: ignore # Method assignation to NamedTuple messes with Mypy

    def make_signature_nodes(self, parsed_sig: HclSignature) -> List[Node]:
        """
        Make nice but semantic nodes for the HCL block signature.

        A HCL block signature is made of one type identifier followed by
        a number of label identifiers. The amount of label identifiers is
        specified and fixed for a given type identifier.  For instance,
        a Terraform ``resource`` has always 2 label identifiers, like so:

        .. code-block:: tf

            resource "google_storage_bucket" "some-bucket" {
                # body of the block definition
                # ...
            }

        Args:
            parsed_sig:
                At this point, the signature has already been parsed and
                we simply use it to generate the correct nodes.

        Returns:
            A list of nodes to append to the signature node.
        """
        signature_nodes: List[Node] = []

        # start with the Terraform definition block type (resource, data...)
        signature_nodes.append(
            addnodes.desc_annotation(
                rawsource=parsed_sig.type.value, text=parsed_sig.type.value
            )
        )

        if parsed_sig.labels:
            first_label, *other_labels = parsed_sig.labels
            signature_nodes.append(addnodes.desc_sig_space())
            signature_nodes.append(
                addnodes.desc_name(rawsource=first_label, text=first_label)
            )

            for label in other_labels:
                signature_nodes.append(addnodes.desc_sig_literal_char(".", "."))
                signature_nodes.append(
                    addnodes.desc_name(rawsource=label, text=label)
                )

        return signature_nodes

    def handle_signature(self, sig: str, signode: desc_signature) -> str:
        hcl_sig = self.parse_signature(sig)
        hcl_def = self._domain.register(self.module, hcl_sig)
        self._hcl_sig = hcl_sig
        self._hcl_def = hcl_def

        signode["module"] = self.module
        signode["signature"] = hcl_sig
        signode["definition"] = hcl_def

        signature_nodes = self.make_signature_nodes(hcl_sig)
        signode.extend(signature_nodes)

        return make_identifier(hcl_sig, self.module)

    def add_target_and_index(
        self, name: T, sig: str, signode: desc_signature
    ) -> None:
        """
        Add cross-reference IDs and entries to self.indexnode, if applicable.

        This method will add this signature name to the general index.

        Args:
            name:
                The identifier of this signature as returned by
                :meth:`~handle_signature`.
            sig:
                One signature string, which is the object name we are indexing.
            signode:
                The signature document node. It acts like the `term` part
                of a glossary entry.
        """
        # We include our unique identifier in the signature's ids, which
        # in turn can be used to render HTML and "id" attribute.
        signode["ids"].append(name)

        signature = self._hcl_sig

        generalindex_entry = SphinxGeneralIndexEntry(
            entrytype="single",
            entryname=str(signature),
            targetid=name,
            mainname=str(signature),
            key=None,
        )
        inode = addnodes.index(entries=[generalindex_entry])
        self.indexnode.append(inode)

    def transform_content(self, contentnode: addnodes.desc_content) -> None:
        hcl_def = self._hcl_def

        code = self._domain.store.get_documentation(hcl_def)

        for line in code:
            log.debug(line)

        comment_nodes = self._parse_terraform_comment(hcl_def)
        contentnode.extend(comment_nodes)

    def _local_code_url(self, hcl_def: HclDefinition) -> str:
        return f"{hcl_def.file}#L{hcl_def.doc_code.start_position.line}-L{hcl_def.doc_code.end_position.line}"

    def _parse_comment_with_external_parser(
        self, hcl_def: HclDefinition, markup_id: str
    ) -> List[Node]:
        parser_class = parser_for_markup(markup_id)
        parser = parser_class()
        parser.set_application(self.env.app)
        document = utils.new_document(
            self._local_code_url(hcl_def), self.state.document.settings
        )

        code = self._domain.store.get_documentation(hcl_def)

        parser.parse("\n".join(code), document)
        return document.children

    def _parse_comment_with_current_parser(
        self, hcl_def: HclDefinition
    ) -> List[Node]:
        document = utils.new_document(
            self._local_code_url(hcl_def), self.state.document.settings
        )

        code = self._domain.store.get_documentation(hcl_def)

        self.state.nested_parse(
            StringList(
                code,
                source=str(hcl_def.file),
            ),
            self.content_offset,
            document,
        )

        return document.children

    def _parse_comment_markdown_comment(
        self, hcl_def: HclDefinition
    ) -> List[Node]:
        return self._parse_comment_with_external_parser(hcl_def, "markdown")

    def _parse_comment_restructuredtext_comment(
        self, hcl_def: HclDefinition
    ) -> List[Node]:
        return self._parse_comment_with_external_parser(
            hcl_def, "restructuredtext"
        )

    def _parse_terraform_comment(self, hcl_def: HclDefinition) -> List[Node]:
        markup_id = self.options.get(
            "markup", get_config_terraform_comment_markup(self.env)
        )
        if markup_id:
            return self._parse_comment_with_external_parser(hcl_def, markup_id)
        else:
            return self._parse_comment_with_current_parser(hcl_def)


class TerraformCrossReferenceRole(XRefRole):
    """
    Define a Terraform object reference role.

    Cross referencing Terraform objects works alike crossreference to
    objects of the Python domain.

    The customization of a standard cross-reference can be done either
    by supplying constructor parameters or subclassing and overwriting
    the :meth:`sphinx.roles.XRefRole.process_link` and/or
    the :meth:`sphinx.roles.XRefRole.result_nodes` methods.
    """

    def process_link(
        self,
        env: BuildEnvironment,
        refnode: Element,
        has_explicit_title: bool,
        title: str,
        target: str,
    ) -> Tuple[str, str]:
        """
        Process link for a given cross-reference role.

        See also:
            The parent class method docstring is something like

                Called after parsing title and target text, and creating
                the reference node (given in *refnode*).  This method can
                alter the reference node and must return a new (or the same)
                ``(title, target)`` tuple.
        Args:
            env:
                Sphinx build environment.
            refnode:
                The created referenced node, which can be altered here.
            has_explicit_title:
                An explicit title in a role is when a display string is
                provided as part of the role's interpreted text. For example

                .. code-block: rst

                    :ref:`Here is an explicit title<some-reference-target>`

                would diplay an hyperlink to ``some-reference-target`` with
                ``Here is an explicit title`` as the link text.

                This value is also available as a instance member with the
                same name (``self.has_explicit_title``).
            title:
                The link title.
            target:
                The link target identifier.

        Returns:
            Title and target strings.
        """
        log.debug(f"Processing links for {self._role_string()}.")
        return super().process_link(
            env, refnode, has_explicit_title, title, target
        )

    def result_nodes(
        self,
        document: nodes.document,
        env: BuildEnvironment,
        node: Element,
        is_ref: bool,
    ) -> Tuple[List[Node], List[system_message]]:
        """
        Add general index nodes just before returning the finished xref nodes.

        See also:
            The parent class method docstring is something like

                Called before returning the finished nodes.

                *node* is the reference node if one was created (*is_ref*
                is then true), else the content node.  This method can add
                other nodes and must return a ``(nodes, messages)`` tuple
                (the usual return value of a role function).
        Args:
            document:
                Source document where this ref was defined.
            env:
                Current Sphinx build environment.
            node:
                This role's node.
            is_ref:
                True when this is the reference node, else it's the content
                node.

        Returns:
            A tuple having a list of final nodes for this role and a list
            of system messages if appropriate.
        """
        log.debug(f"Resulting nodes for {self._role_string()}.")
        entry = SphinxGeneralIndexEntry(
            entrytype="single",
            entryname=self.target,
            targetid="",  # targetid=self.rawtext,
            mainname=node.attributes.get("refdoc", ""),
            key=None,
        )
        inode = addnodes.index(entries=[entry])
        node.append(inode)
        return [node], []

    def _role_string(self) -> str:
        if self.has_explicit_title:
            return f":{self.name}:`{self.title} <{self.target}>`"
        else:
            return f":{self.name}:`{self.target}`"


class TerraformDefinitionsIndex(Index):
    name = "definitionsindex"
    localname = "Terraform Definitions Index"
    shortname = localname

    def generate(
        self, docnames: Optional[Iterable[str]] = None
    ) -> Tuple[List[Tuple[str, List[IndexEntry]]], bool]:
        """
        Generate terraform domain index entries.

        Note:
             Entries should be filtered by the docnames provided. To do.

        Args:
            docnames: Restrict source Restructured text documents to these.

        Returns:
            See :meth:`sphinx.domains.Index.generate` for details.
        """
        content_working_copy = defaultdict(list)

        if not isinstance(self.domain, TerraformDomain):
            raise SphinxTerraformError("Incompatible domain class.")

        objects = self.domain.get_objects()

        # generate the expected output, shown below, from the above using the
        # first letter of the npc as a key to group thing
        #
        # name, subtype, docname, anchor, extra, qualifier, description
        #
        # This shows:
        #
        #     D
        #   - **Display Name** *(extra info)* **qualifier:** typ
        #       **Sub Entry** *(extra info)* **qualifier:** typ
        SUBTYPE_NORMAL = 0
        SUBTYPE_WITHSUBS = 1  # noqa: F841
        SUBTYPE_SUB = 2  # noqa: F841

        name_entry: SphinxDomainObjectDescription

        for name_entry in objects:
            first_letter = name_entry.dispname[0].lower()
            content_working_copy[first_letter].append(
                IndexEntry(
                    name_entry.name,
                    SUBTYPE_NORMAL,
                    name_entry.docname,
                    name_entry.anchor,
                    "",  # extra info
                    "",  # qualifier
                    name_entry.type,
                )
            )

        # convert the dict to the sorted list of tuples expected
        content = sorted(content_working_copy.items())

        return content, True


D = TypeVar("D", bound="TerraformDomain")


class SphinxData(NamedTuple):
    identifier: str
    sphinx_obj: SphinxDomainObjectDescription
    module: TerraformModule
    signature: HclSignature
    definition: HclDefinition


class DomainData(TypedDict, total=False):
    version: int
    terraform: Dict[Any, Any]
    sphinx: Dict[str, SphinxData]


class TerraformDomain(Domain):

    name: str = "tf"
    """
    The domain name, short and unique.
    """

    label: str = "Terraform"
    object_types = {
        "resource": ObjType(t_("resource"), "resource"),
        "variable": ObjType(t_("variable"), "variable"),
        "output": ObjType(t_("output"), "output"),
        "module": ObjType(t_("module"), "module"),
        "data": ObjType(t_("data"), "data"),
    }
    directives = {
        "resource": TerraformObjectDirective,
        "variable": TerraformObjectDirective,
        "output": TerraformObjectDirective,
        "module": TerraformObjectDirective,
        "data": TerraformObjectDirective,
    }
    roles = {
        "resource": TerraformCrossReferenceRole(),
        "variable": TerraformCrossReferenceRole(),
        "output": TerraformCrossReferenceRole(),
        "module": TerraformCrossReferenceRole(),
        "data": TerraformCrossReferenceRole(),
    }
    indices: List[Type[Index]] = [TerraformDefinitionsIndex]
    initial_data: DomainData = {  # type: ignore # base class defined the type as "Dict[Any, Any]"
        "terraform": TerraformStore.initial_data(),
        "sphinx": {},
    }

    @classmethod
    def get_instance(
        cls: Type[D], app_or_env: Union[Sphinx, BuildEnvironment]
    ) -> D:
        env = get_env(app_or_env)
        domain = env.get_domain(cls.name)
        return domain  # type: ignore

    @property
    def store(self) -> TerraformStore:
        return TerraformStore(self.data["terraform"])

    @property
    def sphinx_references(self) -> Dict[str, SphinxData]:
        return self.data["sphinx"]  # type: ignore

    def register(
        self,
        module: TerraformModule,
        signature: HclSignature,
    ) -> HclDefinition:
        definition = self.store.register(module, signature, self.env.docname)
        identifier = make_identifier(signature, module)

        sphinx_obj = SphinxDomainObjectDescription(
            name=str(signature),
            dispname=f"{signature.type.value} {signature}",
            type=signature.type.value,
            docname=self.env.docname,
            anchor=identifier,
            priority=0,
        )

        self.sphinx_references[identifier] = SphinxData(
            identifier, sphinx_obj, module, signature, definition
        )

        return definition

    def get_objects(self) -> Iterable[SphinxDomainObjectDescription]:
        """
        Return an iterable of "object descriptions".

        See Also:
             Parent method :meth:`sphinx.domains.Domain.get_objects`.

        Returns:
            Object descriptions are tuples with six items.
            See :class:`sphinx_terraform.sphinxapi.SphinxDomainObjectDescription`.
        """
        for sphinx_data in self.sphinx_references.values():
            yield sphinx_data.sphinx_obj

    def resolve_xref(
        self,
        env: "BuildEnvironment",
        fromdocname: str,
        builder: Builder,
        typ: str,
        target: str,
        node: addnodes.pending_xref,
        contnode: Element,
    ) -> Optional[Element]:
        """
        Resolve the pending_xref *node* with the given *typ* and *target*.

        See also:
            The parent class method docstring is something like

                Resolve the pending_xref *node* with the given *typ* and
                *target*.

                This method should return a new node, to replace the xref
                node, containing the *contnode* which is the markup content
                of the cross-reference.

                If no resolution can be found, None can be returned; the
                xref node will then given to the :event:`missing-reference`
                event, and if that yields no resolution, replaced by *contnode*.

                The method can also raise :exc:`sphinx.environment.NoUri`
                to suppress the :event:`missing-reference` event being emitted.

        Args:
            env:
                Current Sphinx build environment.
            fromdocname:
                Document name where the cross-reference was used.
            builder:
                Current Sphinx builder.
            typ:
                Object type name.
            target:
                Looked up object identifier.
            node:
                Document node for the xref.
            contnode:
                The markup content of the cross-reference.

        If no resolution can be found, ``None`` can be returned;
        the xref node will then given to the ``missing-reference`` event,
        and if that yields no resolution, replaced by contnode.

        Returns:
            A reference node or None if no reference could be resolved.
        """

        def not_found() -> None:
            log.warning(
                "Cross reference to '{!s}' "
                "could not be resolved "
                "within the '{!s}' domain".format(target, self.name)
            )

        candidates = self._resolve_target(target, typ)

        if not candidates:
            not_found()
            return None

        if len(candidates) == 1:
            sphinx_reference = candidates[0]
            return make_refnode(
                builder,
                fromdocname,
                sphinx_reference.sphinx_obj.docname,
                sphinx_reference.sphinx_obj.anchor,
                contnode,
                str(sphinx_reference.signature),
            )

        log.warning(f"Many canditates found for xref to '{typ}' '{target}'.")
        return None

    def resolve_any_xref(
        self,
        env: "BuildEnvironment",
        fromdocname: str,
        builder: "Builder",
        target: str,
        node: addnodes.pending_xref,
        contnode: Element,
    ) -> List[Tuple[str, Element]]:
        candidates = self._resolve_target(target)

        return [
            (
                f"{self.name}:{sphinx_reference.sphinx_obj.type}",
                make_refnode(
                    builder,
                    fromdocname,
                    sphinx_reference.sphinx_obj.docname,
                    sphinx_reference.sphinx_obj.anchor,
                    contnode,
                    str(sphinx_reference.signature),
                ),
            )
            for sphinx_reference in candidates
        ]

    def _resolve_target(
        self, target: str, typename: Optional[str] = None
    ) -> List[SphinxData]:
        match = re.match(
            r"^(?P<module>(\w+\/)*)?((?P<type>[a-z]+)-)?(?P<name>(([\w-]+)(\.([\w-]+))*)?)$",
            target,
        )

        if not match:
            return []

        matcher = self._make_matcher(target, typename)

        return list(filter(matcher, self.sphinx_references.values()))

    def _make_matcher(
        self, target: str, typename: Optional[str]
    ) -> Callable[[SphinxData], bool]:
        match = re.match(
            r"^(?P<module>(\w+\/)*)?((?P<type>[a-z]+)-)?(?P<name>(([\w-]+)(\.([\w-]+))*)?)$",
            target,
        )

        if not match:
            return lambda x: False

        def matcher(sphinx_reference: SphinxData) -> bool:
            matched_module = match.group("module")  # type: ignore # matched checked above
            matched_name = match.group("name")  # type: ignore # matched checked above

            typename_ok = (
                not typename or typename == sphinx_reference.sphinx_obj.type
            )
            module_ok = (
                not matched_module
                or matched_module.strip("/") == sphinx_reference.module.fullname
            )
            name_ok = not matched_name or matched_name in str(
                sphinx_reference.signature
            )

            return all([typename_ok, module_ok, name_ok])

        return matcher
