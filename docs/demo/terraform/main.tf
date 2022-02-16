/**
 * Documentation for terraform/main.tf
 *
 * * list item 1
 * * list item 2
 *
 * Even inline **formatting** in *here* is possible.
 * and some link_  `inline link <https://example.com/>`__
 *
 * .. _link: https://example.com
 *
 * *  list item 3
 * *  list item 4
 *
 * Enumerated lists:
 *
 * 3.  This is the first item
 * 4.  This is the second item
 * 5.  Enumerators are arabic numbers,
 *     single letters, or roman numerals
 * 6.  List items should be sequentially
 *     numbered, but need not start at 1
 *     (although not all formatters will
 *     honour the first index).
 * #.  This item is auto-enumerated
 *
 * .. code-block:: tf
 *
 *     module "foo_bar" {
 *       source = "github.com/foo/bar"
 *
 *       id   = "1234567890"
 *       name = "baz"
 *
 *       zones = ["us", "elsewhere"]
 *
 *       tags = {
 *         Name         = "baz"
 *         Created-By   = "first.last@email.com"
 *         Date-Created = "20180101"
 *       }
 *     }
 */

terraform {
  required_version = ">= 0.12"
  required_providers {
    foo = {
      source  = "https://registry.acme.com/foo"
      version = ">= 1.0"
    }
  }
}

module "foobar" {
  source = "git@github.com:module/path?ref=v7.8.9"
}

module "sub" {

}

/**
  Here is a ``resource``.

  .. code-block:: shell

      rm -rf /somepath

  look out :tf:data:`foo_data.qux`
 */
resource "foo_resource" "baz" {
}

# Documentation for this data.
#
# Might be somewhat related to :tf:resource:`foo_resource.baz`.
data "foo_data" "qux" {
}
