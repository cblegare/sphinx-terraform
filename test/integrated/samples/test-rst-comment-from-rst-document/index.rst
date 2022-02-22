test-rst-comment-from-rst-document
==================================

- Given directive is used without the `:markup:` option
- and the ``terraform_comment_markup`` conf is not set
- and Terraform comment is in RestructuredText
- When documented from a RestructuredText source file
- Then the documentation is properly rendered.

This means that the source file markup is enough to determine to parse
RestructuredText comments.

.. tf:resource:: foo_resource.restructuredtext
