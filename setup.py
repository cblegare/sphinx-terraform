from __future__ import annotations

from pathlib import Path

from setuptools import find_packages, setup

extras_require = {
    "test": ["nox"],
    "docs": [
        "sphinx_autodoc_typehints",
        "sphinx_paramlinks",
        "sphinx_copybutton",
        "sphinxcontrib_bibtex",
        "sphinxcontrib_programoutput",
        "sphinx_tabs",
        "pydata-sphinx-theme",
    ],
}
extras_require["all"] = set(
    dependency
    for extra_dependencies in extras_require.values()
    for dependency in extra_dependencies
)

this_directory = Path(__file__).parent


if __name__ == "__main__":
    setup(
        name="sphinx-terraform",
        version="0.1",
        description="A Sphinx extension for documenting Terraform modules.",
        long_description=(this_directory / "README.rst").read_text(),
        long_description_content_type="text/x-rst",
        url="https://cblegare.gitlab.io/sphinx-terraform",
        author="Charles Bouchard-Légaré",
        author_email="charlesbouchardlegare@gmail.com",
        license="BSD-2-Clause-Patent",
        project_urls={
            "Documentation": "https://cblegare.gitlab.io/sphinx-terraform",
            "Source": "https://gitlab.com/cblegare/sphinx-terraform",
            "Issue Tracker": "https://gitlab.com/cblegare/sphinx-terraform/-/issues",
        },
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            "Development Status :: 3 - Alpha",
            # Indicate who your project is intended for
            "Intended Audience :: Developers",
            "Intended Audience :: Information Technology",
            "Intended Audience :: System Administrators",
            "Topic :: Documentation",
            "Topic :: Documentation :: Sphinx",
            "Framework :: Sphinx",
            "Framework :: Sphinx :: Extension",
            # Pick your license as you wish (should match "license" above)
            "License :: OSI Approved :: MIT License",
            "Programming Language :: Python :: 3.7",
            "Programming Language :: Python :: 3.8",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Operating System :: OS Independent",
            "Typing :: Typed",
        ],
        keywords="hcl tf terraform sphinx iac cloud infrastructure",
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        python_requires=">=3.7",
        install_requires=[
            "sphinx>=3",
            "docutils",
            "typing_extensions ; python_version<'3.8'",
            "importlib_metadata ; python_version<'3.8'",
        ],
        extras_require=extras_require,
        include_package_data=True,
    )
