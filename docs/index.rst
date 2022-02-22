#########
|project|
#########

.. container:: tagline

    A Sphinx_ extension for documenting **Terraform** modules.

|project| is simple to use and integrate smoothly with your Terraform codebase.

    Programs must be written for people to read, and only incidentally
    for machines to execute.

    -- `SICP <https://mitpress.mit.edu/sites/default/files/sicp/index.html>`__


Code can become reusable when it is clearly visible, searchable and
referenceable.  |project| will help

*   **make reusable modules** that application developers will find easier
    to find, understand and use, thus reducing bugs, support time and *toil*;

*   **show value to stakeholders**, since Infrastructure as Code is an abstract
    and obscure topic for non-practitioners;

*   **promote knowledge** and foster a community spirit around your code;

*   **keep track** of *why* things work the way they do.


Quick start
===========

Install |project|:

.. code-block:: shell

    pip install -U sphinx-terraform

Enable |project| in your ``conf.py`` (:mod:`conf`), and configure where
to find the Terraform files:

.. code-block:: python
    :caption: conf.py

    extensions = [
        # other extensions ...
        "sphinx_terraform"
    ]

    terraform_sources = "../relativeto/docsfolder/terraform"

.. tip:: For details about **configuration**, see :ref:`configuration`.

Place your Terraform documentation within your RestructuredText source files
using one of our directive:

.. code-block:: rst
    :caption: some_documentation.rst

    .. tf:resource:: foo_resource.bar

.. tip:: For details about provided **directives**, see :ref:`directives`.

Then cross-reference your definitions with some of our roles:

.. code-block:: rst
    :caption: some_other_documentation.rst

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


**Sphinx-Terraform** is

- `Hosted on Gitlab <https://gitlab.com/cblegare/sphinx-terraform>`__
- `Mirrored on Github <https://github.com/cblegare/sphinx-terraform>`__
- `Distributed on PyPI <https://pypi.org/project/sphinx-terraform/>`__
- `Documented online <https://cblegare.gitlab.io/sphinx-terraform/>`__


Indices and references
======================

*   :ref:`genindex`
*   :ref:`tf-definitionsindex`
*   :ref:`search`
*   :ref:`glossary`


.. important:: **Terraform** and the Terraform Logo are trademarks
        of HashiCorp_. |project| is not associated with HashiCorp.
