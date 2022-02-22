test-config-terraform_comment_markup-md
=======================================

- Given ``terraform_comment_markup = "md"``
- and Terraform comment is in Markdown
- When documented from a RestructredText source file
- Then the documentation is properly rendered.

This means that the configuration value precedes the source file
when determining to parse Markdown comments

.. tf:resource:: foo_resource.markdown
