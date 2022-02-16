"""
Register object types that exists in referenced documentation.

Intersphinx will only link to objects of types it knows, hence we
register some types, only for hyperlinking purposes.

See also:
    Taken from https://github.com/sphinx-doc/sphinx/blob/master/doc/conf.py
"""

from __future__ import annotations

import re

from sphinx import addnodes  # noqa

event_sig_re = re.compile(r"([a-zA-Z-]+)\s*\((.*)\)")


def setup(app):
    from sphinx.util.docfields import GroupedField

    app.add_object_type(
        "confval",
        "confval",
        objname="configuration value",
        indextemplate="pair: %s; configuration value",
    )

    fdesc = GroupedField(
        "parameter", names=("param",), label="Parameters", can_collapse=True
    )

    app.add_object_type(
        "event",
        "event",
        "pair: %s; event",
        parse_event,
        doc_field_types=[fdesc],
    )


def parse_event(env, sig, signode):
    m = event_sig_re.match(sig)
    if not m:
        signode += addnodes.desc_name(sig, sig)
        return sig
    name, args = m.groups()
    signode += addnodes.desc_name(name, name)
    plist = addnodes.desc_parameterlist()
    for arg in args.split(","):
        arg = arg.strip()
        plist += addnodes.desc_parameter(arg, arg)
    signode += plist
    return name
