from __future__ import annotations

try:
    from ._version import __version__, __version_tuple__
except ModuleNotFoundError:  # pragma: no cover
    import warnings

    __version__ = "0.0.0"
    __version_tuple__ = (0, 0, 0)
    warnings.warn(
        "\nAn error occurred during package install "
        "where setuptools_scm failed to create a _version.py file."
        "\nDefaulting version to 0.0.0."
    )

from sphinx_tutorials.sphinx_tutorials import generate
from sphinx_tutorials.other_extensions.sig_shaper import sig_shaper
from sphinx_tutorials.other_extensions import autodoc_ext

__all__ = ["generate", "sig_shaper"]
