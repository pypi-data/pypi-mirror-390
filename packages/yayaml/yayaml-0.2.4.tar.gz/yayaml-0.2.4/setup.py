"""Sets up the yayaml package installation"""

from setuptools import find_packages, setup

# .. Dependency lists .........................................................

INSTALL_DEPS = [
    "numpy",
    "ruamel.yaml",
]

# Dependencies for running tests and general development of utopya
TEST_DEPS = [
    "pytest",
    "pytest-cov",
    "pre-commit",
]

# Dependencies for building the utopya documentation
DOC_DEPS = [
    "sphinx>=5.3",
    "sphinx-book-theme",
    "sphinx-togglebutton",
    "ipython>=7.0",
    "myst-parser[linkify]",
    "pytest",
]

# .............................................................................


def find_version(*file_paths) -> str:
    """Tries to extract a version from the given path sequence"""
    import codecs
    import os
    import re

    def read(*parts):
        """Reads a file from the given path sequence, relative to this file"""
        here = os.path.abspath(os.path.dirname(__file__))
        with codecs.open(os.path.join(here, *parts), "r") as fp:
            return fp.read()

    # Read the file and match the __version__ string
    file = read(*file_paths)
    match = re.search(r"^__version__\s?=\s?['\"]([^'\"]*)['\"]", file, re.M)
    if match:
        return match.group(1)
    raise RuntimeError("Unable to find version string in " + str(file_paths))


# .............................................................................

DESCRIPTION = "yayaml makes yaml nicer. yay!"

LONG_DESCRIPTION = """
The `yayaml` package provides extensions to `ruamel.yaml` that allow creating
some often-needed Python objects directly via YAML tags and making it easier
to represent custom objects when writing YAML files.

`yayaml` is used in the following projects to read and write YAML files,
including custom constructors and representers:

* `paramspace <https://gitlab.com/blsqr/paramspace>`_: for config-file-based
  grid search with deeply nested dicts
* `dantro <https://gitlab.com/utopia-project/dantro>`_: for loading, processing
  and visualizing high-dimensional simulation output
* `utopya <https://gitlab.com/utopia-project/utopya>`_: a versatile simulation
  framework
"""
# .............................................................................


setup(
    name="yayaml",
    #
    # Package information
    version=find_version("yayaml", "__init__.py"),
    #
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    #
    url="https://gitlab.com/blsqr/yayaml",
    author="Yunus Sevinchan",
    author_email="Yunus Sevinchan <yunussevinchan@gmail.com>",
    classifiers=[
        "License :: OSI Approved :: BSD License",
        #
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        #
        "Development Status :: 5 - Production/Stable",
        #
        "Topic :: Utilities",
    ],
    #
    # Package content
    packages=find_packages(exclude=("tests",)),
    data_files=[("", ["README.md", "LICENSE", "CHANGELOG.md"])],
    #
    # Dependencies
    install_requires=INSTALL_DEPS,
    extras_require=dict(
        test=TEST_DEPS,
        doc=DOC_DEPS,
        dev=TEST_DEPS + DOC_DEPS,
    ),
)
