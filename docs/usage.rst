.. _usage:

###########
User manual
###########

|project| will extract RestructuredText_ documentation string
(and Markdown if you are using the MyST_ parser)
from comments in HCL_ code. For details about using Markdown,
see :ref:`markdown`.

.. hint:: This documentaton uses RestructuredText when providing examples,
    but the equivalent MyST-compatible markup should work.


Documenting your Terraform files
================================

In order for |project| to parse documentation from HCL comments properly,
the documentation markup text **must** be consistently indented.

.. tabs::

    .. tab:: Good comment indent

        .. code-block:: tf

            # This summary line start at a 2 characters indentation
            #
            # All the remaining docs are assumed to have the same starting
            # indent.
            #
            #     so this line will render as a block quote in RestructuredText
            resource "foo_resource" "some-resource" {
            }

    .. tab:: Bad comment indent

        .. code-block:: tf

            #   This summary line start at a 4 characters indentation
            #
            # Comment starting at 2 chars will get cut.
            resource "foo_resource" "some-resource" {
            }

Also, |project| does not care what kind of comment you use, multiline or not.

.. tabs::

    .. tab:: ``#`` comments

        .. code-block:: tf

            ###
            # Hashtag single line comments are valid!
            #
            # This is the recommended way of writing comments.
            resource "foo_resource" "some-resource" {
            }

    .. tab:: ``/** ... */`` comments

        .. code-block:: tf

            /******
             * Multi line comments also are valid!
             */
            resource "foo_resource" "some-resource" {
            }

    .. tab:: ``//`` comments

        .. code-block:: text

            // Hashtag single line comments are valid!
            //
            // But ``#`` are prefered.
            resource "foo_resource" "some-resource" {
            }

    .. tab:: Mixed style comments

        .. code-block:: text

            /* Mixing things is also valid */
            #
            #  But please
            // Don't do this
            #
            # Use ``#`` instead.
            resource "foo_resource" "some-resource" {
            }

.. important:: **It is best to use the idiomatic HCL style.**

    While |project| is quite flexible about HCL code formatting
    and conventions, you can save yourself some trouble by formatting your
    code with ``terraform fmt``

    This also applies to comments:

        The ``#`` single-line comment style is the default comment style
        and should be used in most cases. Automatic configuration formatting
        tools may automatically transform ``//`` comments into ``#`` comments,
        since the double-slash style is not idiomatic.

        -- https://www.terraform.io/language/syntax/configuration#comments


.. _markup:

Extension markup
================

|project| provides new markup (roles and directives) to document your
Terraform projects. Several Terraform definition types are supported.

Since |project| can document many **root modules** within the same documentation
projects, as well as any sub-modules, you may need to provide the following
options (respectively ``:rootmodule:`` and ``module``) in non-tivial module
layouts.

For details about how |project| can manage multiple Terraform modules, see
:ref:`tf-modules`.


.. _directives:

Directives
----------

.. tip:: Using this directive is what makes the ✨*magic*✨ happen.

|project| provides the following :ref:`sphinx:rst-directives` to include
the documentation found within your HCL source files.

.. rst:directive:: tf:resource

    Include documentation from a `Terraform resource`_.

    .. tip:: Cross-reference these definitions with the
        :rst:role:`tf:resource` role.

    .. rst:directive:option:: rootmodule: root module name
        :type: string

        This option is required when you have **more than one**
        :term:`root module` configured in :confval:`terraform_sources`.
        Its value must be the name of one of the configured root modules.

        **Example**
            .. code-block:: rst

                .. tf:resource:: foo_resource.bar
                    :rootmodule: other_terraform

    .. rst:directive:option:: module
        :type: path-ish string

        This option is required when you are documenting a definition
        within a :term:`submodule` (not directly in the root module).

        **Example**
            .. code-block:: rst

                .. tf:output:: sub_output
                    :module: sub

            Would render as

            .. tf:output:: sub_output
                :module: sub

    .. tip:: Instead of using the ``:rootmodule:`` and ``:module:`` options
        above, you can also specify the module path within the signature
        like so:

        .. code-block:: rst

            .. tf:variable:: terraform/sub/submodule-input

        Would render as

        .. tf:variable:: terraform/sub/submodule-input

        .. _Terraform resource: https://www.terraform.io/language/resources

    .. rst:directive:option:: markup
        :type: string

        .. versionadded:: 0.2

        Force the expected markup language for a HCL definition.
        See :ref:`markdown` for details.

.. rst:directive:: tf:data

    Works exactly the same way as :rst:dir:`tf:resource`.

.. rst:directive:: tf:variable

    Works exactly the same way as :rst:dir:`tf:resource`.

.. rst:directive:: tf:output

    Works exactly the same way as :rst:dir:`tf:resource`.

.. rst:directive:: tf:module

    This directive does not document a :term:`module`, but a
    :term:`module block`, which is the *calling* of a child module.

    Works exactly the same way as :rst:dir:`tf:resource`.


.. _roles:

Roles
-----

|project| provides the following :term:`roles` to create inline
cross-references (hyperlinks) to your definitions' documentation.

.. tip:: |project| will keep track of all these cross-references and add
    them to the :ref:`genindex` as well under their respective target entry.

Roles that cross-references HCL definitions can be quite flexible.
|project| will be as permissive as possible to resolve cross-references.
If your definitions across all *modules* and *submodules* minimize naming
conflicts, you might be able to keep the *role* markup concise.

.. rst:role:: tf:resource

    Cross reference a documented Terraform resource as defined using the
    :rst:dir:`tf:resource` directive.

    Example:
        Here is some markup text followed by its rendered result.

        .. code-block:: rst

            You really should check out :tf:resource:`terraform/foo_resource.baz`.

            Since we dont have deep modules or several root module, we can
            even shorten this to :tf:resource:`foo_resource.baz`. And since
            we might be in luck, we can even try the shortest thing with
            :tf:resource:`baz`, but that will only work if ``baz`` does
            not collide with any other ``resource`` object.

        Would render as

            You really should check out :tf:resource:`terraform/foo_resource.baz`.

            Since we dont have deep modules or several root module, we can
            even shorten this to :tf:resource:`foo_resource.baz`. And since
            we might be in luck, we can even try the shortest thing with
            :tf:resource:`baz`, but that will only work if ``baz`` does
            not collide with any other ``resource`` object.

.. rst:role:: tf:data

    Cross reference a documented Terraform module call as defined using
    the :rst:dir:`tf:data` directive.

    This role works exactly the same as the :rst:role:`tf:resource`.

.. rst:role:: tf:variable

    Cross reference a documented Terraform input variable as defined using
    the :rst:dir:`tf:variable` directive.

    This role works exactly the same as the :rst:role:`tf:resource`.

.. rst:role:: tf:output

    Cross reference a documented Terraform input variable as defined using
    the :rst:dir:`tf:output` directive.

    This role works exactly the same as the :rst:role:`tf:resource`.

.. rst:role:: tf:module

    Cross reference a documented Terraform module call as defined using
    the :rst:dir:`tf:module` directive.

    This role works exactly the same as the :rst:role:`tf:resource`.


.. _configuration:

Configuration
=============

|project| can use the following configuration from your :mod:`conf`.

.. confval:: terraform_sources

    *required*

    Can be either

    **A string**
        that provide the path to your Terraform root module. The root module
        name will default to the Terraform root module folder name.

    **A dictionary**
        that maps root module names to path to Terraform root modules.


.. confval:: terraform_comment_markup

    .. versionadded:: 0.2

    *optional*

    Tell the markup language |project| should expected to find in HCL comments.
    See :ref:`markdown` for details.

    Accepted values are (case insensitive)

    *   ``md``, ``markdown``, ``myst`` for using Markdown
    *   Any other truthy value means RestructuredText


.. _markdown:

Using Markdown
==============

Thanks to the MyST_ parser, you can write `Markdown markup <MarkdownLanguage>`_
in both the documentation source files and HCL source files.

.. versionchanged:: 0.2
    |project| supports mixing Markdown and RestructuredText.

To use Markdown, you need the ``markdown`` extra dependencies:

.. code-block:: shell

    $ pip install sphinx-terraform[markdown]

Make sur the MyST parser is properly enabled and configured in
:mod:`conf`.
See the `MyST parser documentation <https://myst-parser.readthedocs.io/en/latest/>`__.

#.  **By default**, |project| will expect the HCL comments to be written
    in the same markup language as the documentation source file they are
    included from.

    This means that when the :rst:dir:`tf:resource` directive used from
    a RestructedText file will expect ResctructedText in the HCL comment,
    and will respectively expect Markdown when used from a Mardown file.

#.  **Configuration** can set the expected markup language for all HCL
    comment using the :confval:`terraform_comment_markup` configuration.

#.  **Locally**, the ``:markup:`` directive option can be used to force
    a markup language for a given HCL definition.

.. tip:: While the MyST parser does a very good job at providing the very
    popular Markdown markup language into the Sphinx ecosystem, there are
    some remaining compatibility issues and is arguably more verbose than
    the traditional RestructuredText syntax.

    On the other hand, RestructuredText simply does exist in the Terraform
    ecosystem, while there are a few tools for generating documentation
    from Markdown comments in HCL files.

    A **compromise** could be to use

    *   RestructuredText for the regular documentation prose
    *   Markdown in HCL comments, leveraging the
        :confval:`terraform_comment_markup` configuration key.


.. _tf-modules:

Documenting multiple Terraform modules
======================================

A Terraform module is a directory containing Terraform definition files
and other modules.

.. tip:: In Terraform, **files** have no structural meaning.

For details, see :term:`module`, :term:`root module` and :term:`submodule`
from our :ref:`glossary`.

**Example**
    The following example illustrates exactly how module names work.

    Given the following filesystem layout

    .. code-block:: text

        /some/path/to/your/project/
        └── terraform/
            ├── main.tf
            ├── first_sub_module/
            │   ├── main.tf
            │   └── sub_sub_module/
            │       └── main.tf
            └── second_sub_module/
                └── main.tf

    the following |project| configuration within a ``conf.py`` are
    **equivalent**:

    .. code-block:: python

        terraform_sources = {
            "terraform": "/some/path/to/your/project/terraform"
        }

    .. code-block:: python

        terraform_sources = "/some/path/to/your/project/terraform"

    This would define the following module **fullnames**:

    *   ``terraform`` (this one is the **root module**)
    *   ``terraform/first_sub_module``
    *   ``terraform/first_sub_module/sub_sub_module``
    *   ``terraform/second_sub_module``


.. _viewcode:

Embedding Terraform code
========================

You can embed your documented Terraform code in the HTML pages.

For each Terraform file containing a :ref:`documented <directives>`
definition, a separate HTML page is output with a highlighted version
of the source code.  All definitions also get a link to the highlighted
source code, and all documented highighted source code get a link back
to the definition documentation.

To enable this feature, add the ``sphinx_terraform.viewcode`` extension
to your :mod:`conf`:

.. code-block:: python
    :caption: conf.pf

    extensions = [
        # other extensions ...
        "sphinx_terraform",
        "sphinx_terraform.viewcode",  # <- this one right here!
    ]


.. warning:: While |project| is lenient with non idiomatic HCL code style,
    Pygments_, our syntax highlighter, can be picky in some cases and refuse
    to highlight your code.  To prevent this, use idiomatic HCL code style.
    The ``terraform fmt`` command can be put to good use in this case.

    .. _Pygments: https://pygments.org/


This is inspired by :mod:`sphinx.ext.viewcode`.  See :ref:`demo` to see
it in action.


Indices
=======

|project| generate one domain index.  You can link to it with the following
role:

.. code-block:: rst

    :ref:`tf-definitionsindex`

Which would produce the following link: :ref:`tf-definitionsindex`.



.. _RestructuredText: https://en.wikipedia.org/wiki/ReStructuredText
.. _MarkdownLanguage: https://en.wikipedia.org/wiki/Markdown
.. _MyST: https://myst-parser.readthedocs.io/en/latest/
.. _HCL: https://github.com/hashicorp/hcl

