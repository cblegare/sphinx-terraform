test-md-comment-from-md-document
================================

- Given directive is used without the `:markup:` option
- and the `terraform_comment_markup` conf is not set
- and Terraform comment is in Markdown
- When documented from a Markdown source file
- Then the documentation is properly rendered.

This means that the source file markup is enough to determine to parse 
Markdown comments.

```{tf:resource} foo_resource.markdown
```
