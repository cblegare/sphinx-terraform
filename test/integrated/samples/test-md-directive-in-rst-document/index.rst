test-md-directive-in-rst-document
=================================

- Given directive is used with ``:markup: md``
- and the ``terraform_comment_markup`` conf is not set
- and Terraform comment is in Markdown
- When documented from a RestructuredText source file
- Then the documentation is properly rendered.

This means that the directive ``markup`` option precedres the source file
markup when determining to parse Markdown comments

.. tf:resource:: foo_resource.markdown
    :markup: md
