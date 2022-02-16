:orphan:

.. _glossary:

Glossary
========

.. glossary::

    Terraform module
    Module
    Modules
        HashiCorp describes modules as

            A module is a container for multiple resources that are used together.
            -- https://www.terraform.io/language/modules/syntax

        A Terraform module is a directory containing Terraform definition files
        and other modules.

        The top-most module is called the **root** module.

        See also https://learn.hashicorp.com/tutorials/terraform/module

    Root module
        In |project|, the **root module** name comes from the documentation
        configuration. Its *fullname* is the same as its name.

        See :confval:`terraform_sources`.

    Sub modules
    Submodule
        Sub modules are :term:`modules` that are under a :term:`root module`.
        Sub modules are named by their directory name and their *fullname*
        is derived from their parents names using slashes (``/``) as
        separators. Within |project|, modules are like filesystem path
        relative to a **root module's** name.

    Module block
        A HCL definition block that **calls** a child module.

        See also https://www.terraform.io/language/modules/syntax#calling-a-child-module.

    Roles
        Roles are used to cross-reference any documented objects, even
        traversing documentation sites.  This means you can use roles to
        cross-reference object *defined in other projects*, thanks to the
        :mod:`sphinx.ext.intersphinx` Sphinx builtin extension.

        See also :term:`roles within the Sphinx glossary <sphinx:role>`.

        Roles are inline pieces of interpreted text that looks like:

        .. code-block:: rst

            :domain:object_type:`Explicit title <intersphinx_sourcename:qualified_name>`

        Which could be as short as

        .. code-block:: rst

            :object_type:`qualified_name`

        in many cases.

        **domain**
            This would be the domain name, valued ``tf``.

            The domain can be made optional by either locally (within a
            single document) using the :rst:dir:`default-domain` *directive*
            while the :confval:`primary_domain` *configuration* selects
            a global default

        **object_type**
            The Terraform domain defines several objects types (``resource``,
            ``variable``, and more).

            One can also try the :rst:role:`any` role, which might work
            in some cases, yielding an error at build time if the domain
            could not find a matching cross-reference target.

        **Explicit title**
            By default, without having an explicit title the link text
            rendered will be provided by the cross-reference target.
            Put an explicit title to overwrite it. **Without** an explicit
            title, the above example would look like

            .. code-block:: rst

                :domain:object_type:`intersphinx_sourcename:qualified_name`

            Note that the enclosed `` < `` and `` > `` where not necessary
            anymore.

        **intersphinx_sourcename**
            :mod:`sphinx.ext.intersphinx` let us cross-reference objects
            from any third-party documentation.  When two or more
            documentation provide entries for a object of the same name
            and kind, you need to explicitly select the documentation
            source name to which this cross-reference targets. These
            documentation source name are specified by the user as the
            **keys** in the :confval:`intersphinx_mapping` configuration
            dictionary.

            In practice, this is seldom used. **Without** an Intersphinx
            mapping name, the above example would look like

            .. code-block:: rst

                :domain:object_type:`qualified_name`

        **qualified_name**
            The target name of the thing you are cross-referencing to.

        See also:
            Details about roles and cross-references is also covered in
            the :ref:`xref-syntax` section from the official Sphinx docs.
