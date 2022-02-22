test-config-terraform_comment_markup-md
========================================

- Given `terraform_comment_markup = "rst"`
- and Terraform comment is in RestructuredText
- When documented from a Markdown source file
- Then the documentation is properly rendered.

This means that the configuration value precedes the source file
when determining to parse RestructuredText comments

```{tf:resource} foo_resource.restructuredtext
```
