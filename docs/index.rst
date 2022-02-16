#########
|project|
#########

.. container:: tagline

    A Sphinx_ extension for documenting Terraform modules.

    .. important:: **Terraform** and the Terraform Logo are trademarks
        of HashiCorp_. |project| is not associated with HashiCorp.


Installation
============

.. code-block:: shell

    pip install -U sphinx-terraform


Configuration
=============

In your ``conf.py`` (:mod:`conf`) add the enable the extension and configure
where to find the Terraform files:

.. code-block:: python

    extensions = [
        # other extensions ...
        "sphinx_terraform"
    ]

    terraform_sources = "../relativeto/docsfolder/terraform"

.. tip:: For details about **configuration**, see :ref:`configuration`.


Usage
=====

Place your Terraform documentation within your RestructuredText source files
using one of our directive:

.. code-block:: rst

    .. tf:resource:: foo_resource.bar

.. tip:: For details about provided **directives**, see :ref:`directives`.

Then cross-reference your definitions with some of our roles:

.. code-block:: rst

    You should really check out :rf:resource:`foo_resource.bar`.

.. tip:: for details about supported **roles**, see :ref:`roles`.

.. _Sphinx: https://www.sphinx-doc.org/en/master/index.html
.. _HashiCorp: https://www.hashicorp.com/

.. toctree::
    :maxdepth: 1
    :hidden:

    usage
    demo/index
    contributing
    changelog
    Code <apidoc/index>
    about


Indices and references
======================

*   :ref:`genindex`
*   :ref:`tf-terraformindex`
*   :ref:`search`
*   :ref:`glossary`
