.. _changelog:


#########
Changelog
#########

All releases are available in the project `releases page`_.

All notable changes to this project will be documented in this file.

The format is based on `Keep a Changelog`_, and this project will adheres to
`Semantic Versioning`_ from version 1.0 and after.

.. _releases page: https://gitlab.com/exfo/products/tandm/basecamp/sphinxexfo/-/releases
.. _Keep a Changelog: https://keepachangelog.com/en/1.0.0/
.. _Semantic Versioning: https://semver.org/spec/v2.0.0.html


..
    How do I make a good changelog?
    ===============================

    Guiding Principles
    ------------------

    - Changelogs are for humans, not machines.
    - There should be an entry for every single version.
    - The same types of changes should be grouped.
    - Versions and sections should be linkable.
    - The latest version comes first.
    - The release date of each version is displayed.
    - Mention whether you follow Semantic Versioning.

    Types of changes
    ----------------

    - **Added** for new features.
    - **Changed** for changes in existing functionality.
    - **Deprecated** for soon-to-be removed features.
    - **Removed** for now removed features.
    - **Fixed** for any bug fixes.
    - **Security** in case of vulnerabilities.

    [1.0.0] - 2017-06-20
    --------------------

    Added
    ~~~~~

    - Added a feature.


.. _release-next:

0.3 - unreleased
================

.. admonition:: Downloads

    Stay tuned!


.. _release-0.2:

0.2 - 2022-03-15
================

.. admonition:: Downloads

    :release:`0.2`


Added
-----

*   Added :confval:`terraform_comment_markup` and the ``:markup:`` option
    in :ref:`directives` to allow mixing Markdown and RestructuredText.
    See :ref:`markdown` for details. (:mr:`5`)


.. _release-0.1:

0.1 - 2022-02-15
================

.. admonition:: Downloads

    :release:`0.1`


Added
-----

*   Directives for documenting Terraform resources, data, variables and
    modules. See :ref:`directives`.

*   Roles for cross-referencing Terraform resources, data, variables and
    modules. See :ref:`roles`.

*   Domain Index.

*   Link to source code similar to :mod:`sphinx.ext.viewcode`.
