.. _usage:

###########
User manual
###########


Documenting your Terraform files
--------------------------------

|project| will extract RestructuredText_ documentation string
(and Markdown_ if you are using the MyST_ parser) from comments in HCL_
code.

.. _RestructuredText: https://en.wikipedia.org/wiki/ReStructuredText
.. _Markdown: https://en.wikipedia.org/wiki/Markdown
.. _MyST: https://myst-parser.readthedocs.io/en/latest/
.. _HCL: https://github.com/hashicorp/hcl


.. _markup:

Extension markup
----------------

|project| provides new markup (roles and directives) to document your
Terraform projects. Several Terraform definition types are supported.

Since |project| can document many **root modules** within the same documentation
projects, as well as any sub-modules, you may need to provide the following
options (respectively ``:rootmodule:`` and ``module``) in non-tivial module
layouts.

.. admonition:: **A note about Terraform modules**

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


.. _directives:

Directives
~~~~~~~~~~

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
~~~~~

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
-------------

The following con

.. confval:: terraform_sources

    *required*

    Can be either

    **A string**
        that provide the path to your Terraform root module. The root module
        name will default to the Terraform root module folder name.

    **A dictionary**
        that maps root module names to path to Terraform root modules.

Indices
-------

|project| generate one domain index.


