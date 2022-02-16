from __future__ import annotations

import sys

if sys.version_info < (3, 8, 0):
    from typing_extensions import runtime_checkable
else:
    from typing import runtime_checkable

from sphinx_terraform.terraform import HclSignature, TerraformResourceSignature


def test_protocol():
    a_signature = TerraformResourceSignature(
        "someprovider", "somekind", "somename"
    )

    checkable = runtime_checkable(HclSignature)

    assert isinstance(a_signature, checkable)
