from __future__ import annotations

import pytest
from sphinx.application import Sphinx


@pytest.mark.sphinx(testroot="basic", confoverrides={"nitpicky": True})
def test_tf(app: Sphinx, status, warning):
    print(app, status, warning)
