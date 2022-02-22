test-md-in-rst
==============

- Given directive is used with `:markup: rst`
- and the ``terraform_comment_markup`` conf is not set
- and Terraform comment is in RestructuredText
- When documented from a Markdown source file
- Then the documentation is properly rendered.

This means that the directive ``markup`` option precedres the source file 
markup when determining to parse RestructuredText comments

```{tf:resource} foo_resource.restructuredtext
:markup: rst
```
