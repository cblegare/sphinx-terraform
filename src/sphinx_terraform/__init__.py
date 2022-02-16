"""
This is **not** an API.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Dict, Union

from sphinx.application import Sphinx
from sphinx.builders import Builder
from sphinx.environment import BuildEnvironment
from sphinx.errors import SphinxError
from sphinx.highlighting import PygmentsBridge
from sphinx.util.logging import getLogger

from sphinx_terraform.i18n import t__
from sphinx_terraform.sphinxapi import ExtensionMetadata

if TYPE_CHECKING or sys.version_info < (3, 8, 0):
    from importlib_metadata import PackageNotFoundError, version
else:
    from importlib.metadata import PackageNotFoundError, version


try:
    # _package_name = __name__
    _package_name = "sphinx_terraform"
    __version__ = str(version(_package_name))  # type: ignore
except PackageNotFoundError:
    # package is not installed
    __version__ = "(please install the package)"


log = getLogger(__name__)


DOMAIN_NAME = "tf"


class SphinxTerraformError(SphinxError):
    category = "Sphinx-Terraform error"


def setup(app: Sphinx) -> ExtensionMetadata:
    app.require_sphinx("3")

    app.add_config_value("terraform_sources", ".", "", [str, dict])
    from sphinx_terraform.markup import TerraformDomain

    app.add_domain(TerraformDomain)

    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }


def get_config_terraform_sources(
    env: BuildEnvironment,
) -> Dict[str, Path]:
    configured = env.config.terraform_sources

    if not configured or not isinstance(configured, (str, Dict, Path)):
        raise SphinxTerraformError(
            t__(
                "No terraform sources where configured in conf.py. "
                "Please provide a value to 'terraform_sources'."
            )
        )

    if isinstance(configured, (str, Path)):
        configured = {Path(configured).name: configured}

    for name in configured:
        path = Path(configured[name])
        if not path.is_absolute():
            path = Path(env.project.srcdir, path)
        configured[name] = path

    return configured


def get_env(app_or_env: Union[Sphinx, BuildEnvironment]) -> BuildEnvironment:
    if isinstance(app_or_env, BuildEnvironment):
        return app_or_env
    if isinstance(app_or_env.env, BuildEnvironment):
        return app_or_env.env
    raise SphinxTerraformError("Build environment not ready.")


def get_app(app_or_env: Union[Sphinx, BuildEnvironment]) -> Sphinx:
    if isinstance(app_or_env, BuildEnvironment):
        return app_or_env.app
    return app_or_env


def get_builder(app_or_env: Union[Sphinx, BuildEnvironment]) -> Builder:
    app = get_app(app_or_env)
    if isinstance(app.builder, Builder):
        return app.builder

    raise SphinxTerraformError("Builder not ready.")


def get_highlighter(
    app_or_env: Union[Sphinx, BuildEnvironment]
) -> PygmentsBridge:
    builder = get_builder(app_or_env)

    if hasattr(builder, "highlighter"):
        return builder.highlighter  # type: ignore

    raise SphinxTerraformError("Unsupported builder.")
