"""Sphinx autodoc helpers for ``sphinx_tutorials``.

This module encapsulates autodoc-specific behavior so it can be enabled
independently from other features. It exposes a Sphinx extension that wires
standard autodoc event hooks and a few optional monkey patches.

Configuration is provided via the ``sphinx_tutorials_autodoc`` dict in
``conf.py``. See the docstring of :func:`setup` for details.
"""

from __future__ import annotations

from typing import Any

import sphinx
from sphinx.util import logging

logger = logging.getLogger(__name__)

_DEFAULT_CFG: dict[str, Any] = {
    "skip_private_members": True,
    "special_members": [
        "__repr__",
        "__str__",
        "__int__",
        "__call__",
        "__len__",
        "__eq__",
    ],
    "skip_namespaces": [],
    "skip_members_call": [],

    "enable_modify_type_hints": False,
    "enable_see_also_monkey_patch": False,
}


def _get_cfg(app) -> dict[str, Any]:
    """Return merged configuration for this extension.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application instance.

    Returns
    -------
    dict
        The user configuration merged over defaults.
    """
    cfg = getattr(app.config, "sphinx_tutorials_autodoc", None)
    if not isinstance(cfg, dict):
        return dict(_DEFAULT_CFG)
    merged = dict(_DEFAULT_CFG)
    merged.update(cfg)
    return merged


# --- autodoc hooks

def autodoc_skip_member(app, what, name, obj, skip, options):
    """Decide whether autodoc should skip a member.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application.
    what : str
        The type of the object which the docstring belongs to (e.g.,
        ``"module"``, ``"class"``, ``"exception"``, ``"function"``,
        ``"method"``, ``"attribute"``).
    name : str
        Name of the object to be documented.
    obj : Any
        The object itself.
    skip : bool
        A boolean indicating if autodoc will skip this member by default.
    options : Any
        The options given to the directive.

    Returns
    -------
    bool
        ``True`` to skip the member, ``False`` to include it.

    Notes
    -----
    Behavior is controlled via ``sphinx_tutorials_autodoc`` options:

    - ``skip_private_members``: skip names starting with ``_``.
    - ``skip_namespaces``: list of fully-qualified names whose ``__init__``
      should be skipped.
    """
    if skip:
        # Allow configured special members even if Sphinx would skip them
        cfg = _get_cfg(app)
        if name in set(cfg.get("special_members", [])):
            return False
        return True

    cfg = _get_cfg(app)

    # Handle __init__ first: allow by default, but skip if in configured namespaces
    if name == "__init__":
        namespaces = cfg.get("skip_namespaces", [])
        qualname = getattr(obj, "__qualname__", "")
        if any(
                qualname == f"{ns}.__init__" or qualname.endswith(f".{ns}.__init__")
                for ns in namespaces
        ):
            return True
        return False

    # Handle __init__ first: allow by default, but skip if in configured namespaces
    if name == "__call__":
        namespaces = cfg.get("skip_members_call", [])
        qualname = getattr(obj, "__qualname__", "")
        if any(
                qualname == f"{ns}.__call__" or qualname.endswith(f".{ns}.__call__")
                for ns in namespaces
        ):
            return True
        return False

    # Include configured special members
    if name in set(cfg.get("special_members", [])):
        return False

    # Optionally skip private members (does not affect __init__ due to early return above
    if cfg.get("skip_private_members", True) and name.startswith("_"):
        return True

    return False


def autodoc_process_bases(app, name, obj, options, bases):
    """Filter class bases shown in the documentation.

    Removes private bases and mixin classes from the rendered bases list.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application.
    name : str
        Fully-qualified name of the object being documented.
    obj : Any
        The class object being documented.
    options : Any
        Directive options.
    bases : list[type]
        In-place list of base classes to be displayed.
    """
    # Remove private/mixin bases from rendered class bases list
    to_remove = [b for b in bases if
                 b.__name__.startswith("_") or "Mixin" in b.__name__]
    for base in to_remove:
        bases.remove(base)


def autodoc_process_signature(app, what, name, obj, options, signature,
                              return_annotation):
    """Optionally rewrite type names in signatures for better cross-references.

    Currently performs a minimal mapping of ``np`` to ``~numpy`` to help
    Sphinx/Napoleon resolve references when using string annotations.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application.
    what : str
        The type of object processed.
    name : str
        Fully-qualified object name.
    obj : Any
        The object itself.
    options : Any
        Directive options.
    signature : str | None
        The original signature string.
    return_annotation : str | None
        The original return annotation string.

    Returns
    -------
    tuple[str | None, str | None]
        Possibly modified ``(signature, return_annotation)``.
    """
    # Minimal, safe modification: map np->~numpy in text signatures
    if signature:
        signature = signature.replace("np", "~numpy")
    if return_annotation:
        return_annotation = return_annotation.replace("np", "~numpy")
    return signature, return_annotation


# --- optional monkey patching

def _monkey_patch_parse_see_also() -> None:
    """Enable NumPy-style See Also parsing in Google docstrings.

    Monkey-patches Napoleon's Google docstring parser to use the See Also
    parsing logic from NumPy docstrings, and strips whitespace in the section
    to be resilient to formatting.

    Notes
    -----
    This patch is only applied when
    ``sphinx_tutorials_autodoc["enable_see_also_monkey_patch"]`` is ``True``.
    """
    method = sphinx.ext.napoleon.NumpyDocstring._parse_numpydoc_see_also_section
    sphinx.ext.napoleon.GoogleDocstring._parse_numpydoc_see_also_section = method

    def _parse_see_also_section(self, section: str):
        lines = self._consume_to_next_section()
        for i in range(len(lines)):
            lines[i] = lines[i].strip()
        try:
            return self._parse_numpydoc_see_also_section(lines)
        except ValueError:
            return self._format_admonition("seealso", lines)

    sphinx.ext.napoleon.GoogleDocstring._parse_see_also_section = _parse_see_also_section


# --- setup

def setup(app):
    """Sphinx entry point for the ``sphinx_tutorials.autodoc_ext`` extension.

    This extension is configured via ``sphinx_tutorials_autodoc`` in
    ``conf.py`` with the following keys:

    ``skip_private_members`` : bool, default True
        If ``True``, private names (starting with ``_``) are skipped.

    ``special_members`` : list[str]
        Reserved for potential future use; included for API stability.

    ``skip_namespaces`` : list[str]
        Fully-qualified names whose ``__init__`` should be skipped.

    ``enable_modify_type_hints`` : bool, default False
        If ``True``, connects a handler that rewrites ``np`` to ``~numpy`` in
        stringified signatures to help cross-references resolve.

    ``enable_see_also_monkey_patch`` : bool, default False
        If ``True``, applies a small monkey-patch to make Napoleon's Google
        docstrings parse See Also sections like NumPy docstrings and to
        strip whitespace for robustness.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        The Sphinx application.

    Returns
    -------
    dict
        The Sphinx extension metadata.
    """
    app.add_config_value("sphinx_tutorials_autodoc", dict(_DEFAULT_CFG), "env")

    def on_config_inited(app, _):
        cfg = _get_cfg(app)
        if cfg.get("enable_see_also_monkey_patch", False):
            _monkey_patch_parse_see_also()
        app.connect("autodoc-skip-member", autodoc_skip_member)
        app.connect("autodoc-process-bases", autodoc_process_bases)
        if cfg.get("enable_modify_type_hints", False):
            app.connect("autodoc-process-signature", autodoc_process_signature)

    app.connect("config-inited", on_config_inited)

    return {
        "version": "0.0",
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }

# # -- Monkey-patching ---------------------------------------------------------
#
# SPECIAL_MEMBERS = [
#     "__repr__",
#     "__str__",
#     "__int__",
#     "__call__",
#     "__len__",
#     "__eq__",
# ]
#
#
# def autodoc_skip_member(app, what, name, obj, skip, options):
#     """
#     Instruct autodoc to skip members
#     """
#
#     if skip:
#         # Continue skipping things Sphinx already wants to skip
#         return skip
#
#     namespaces = [
#         "_ValidBase",
#         "ValidColumn",
#         "ValidFrame",
#         "ValidRelations",
#         "ValidPairRelation",
#
#         "InfoList",
#     ]
#
#     if name in "__init__" and obj.__qualname__ in [f"{ns}.__init__" for ns in namespaces]:
#         print("SKIPPING OBJECT NAME: ---->", obj.__qualname__)
#
#         return True
#
#     if name == "__init__":
#         return False
#
#     # if name in SPECIAL_MEMBERS:
#     #     # Don't skip members in "special-members"
#     #     return False
#
#     # elif hasattr(obj, "__objclass__"):
#     #     # This is a NumPy method, don't include docs
#     #     return True
#     # elif getattr(obj, "__qualname__", None) in ["FunctionMixin.dot", "Array.astype"]:
#     #     # NumPy methods that were overridden, don't include docs
#     #     return True
#     # elif (
#     #         hasattr(obj, "__qualname__")
#     #         and getattr(obj, "__qualname__").split(".")[0] == "FieldArray"
#     #         and hasattr(numpy.ndarray, name)
#     # ):
#     #     if name in ["__repr__", "__str__"]:
#     #         # Specifically allow these methods to be documented
#     #         return False
#     #     else:
#     #         # This is a NumPy method that was overridden in one of our ndarray subclasses. Also don't include
#     #         # these docs.
#     #         return True
#
#     if name[0] == "_":
#         # For some reason we need to tell Sphinx to hide private members
#         return True
#
#     return skip
#
#
# def autodoc_process_bases(app, name, obj, options, bases):
#     """
#     Remove private classes or mixin classes from documented class bases.
#     """
#     # Determine the bases to be removed
#     remove_bases = []
#     for base in bases:
#         if base.__name__[0] == "_" or "Mixin" in base.__name__:
#             remove_bases.append(base)
#
#     # Remove from the bases list in-place
#     for base in remove_bases:
#         bases.remove(base)
#
#
# # Only during Sphinx builds, monkey-patch the metaclass properties into this class as "class properties". In Python 3.9 and greater,
# # class properties may be created using `@classmethod @property def foo(cls): return "bar"`. In earlier versions, they must be created
# # in the metaclass, however Sphinx cannot find or document them. Adding this workaround allows Sphinx to document them.
#
# # INHERITED MEMBERS : https://github.com/jbms/sphinx-immaterial/issues/122
#
# # def classproperty(obj):
# #     ret = classmethod(obj)
# #     ret.__doc__ = obj.__doc__
# #     return ret
# #
# #
# # ArrayMeta_properties = [
# #     member for member in dir(galois.Array) if inspect.isdatadescriptor(getattr(type(galois.Array), member, None))
# # ]
# # for p in ArrayMeta_properties:
# #     # Fetch the class properties from the private metaclasses
# #     ArrayMeta_property = getattr(galois._domains._meta.ArrayMeta, p)
# #
# #     # Temporarily delete the class properties from the private metaclasses
# #     delattr(galois._domains._meta.ArrayMeta, p)
# #
# #     # Add a Python 3.9 style class property to the public class
# #     setattr(galois.Array, p, classproperty(ArrayMeta_property))
# #
# #     # Add back the class properties to the private metaclasses
# #     setattr(galois._domains._meta.ArrayMeta, p, ArrayMeta_property)
# #
# #
# # FieldArrayMeta_properties = [
# #     member
# #     for member in dir(galois.FieldArray)
# #     if inspect.isdatadescriptor(getattr(type(galois.FieldArray), member, None))
# # ]
# # for p in FieldArrayMeta_properties:
# #     # Fetch the class properties from the private metaclasses
# #     if p in ArrayMeta_properties:
# #         ArrayMeta_property = getattr(galois._domains._meta.ArrayMeta, p)
# #     FieldArrayMeta_property = getattr(galois._fields._meta.FieldArrayMeta, p)
# #
# #     # Temporarily delete the class properties from the private metaclasses
# #     if p in ArrayMeta_properties:
# #         delattr(galois._domains._meta.ArrayMeta, p)
# #     delattr(galois._fields._meta.FieldArrayMeta, p)
# #
# #     # Add a Python 3.9 style class property to the public class
# #     setattr(galois.FieldArray, p, classproperty(FieldArrayMeta_property))
# #
# #     # Add back the class properties to the private metaclasses
# #     if p in ArrayMeta_properties:
# #         setattr(galois._domains._meta.ArrayMeta, p, ArrayMeta_property)
# #     setattr(galois._fields._meta.FieldArrayMeta, p, FieldArrayMeta_property)
#
#
# # def autodoc_process_signature(app, what, name, obj, options, signature, return_annotation):
# #     signature = modify_type_hints(signature)
# #     return_annotation = modify_type_hints(return_annotation)
# #     return signature, return_annotation
#
#
# # def modify_type_hints(signature):
# #     """
# #     Fix shortening numpy type annotations in string annotations created with
# #     `from __future__ import annotations` that Sphinx can't process before Python
# #     3.10.
# #
# #     See https://github.com/jbms/sphinx-immaterial/issues/161
# #     """
# #     if signature:
# #         signature = signature.replace("np", "~numpy")
# #     return signature
#
#
# def monkey_patch_parse_see_also():
#     """
#     Use the NumPy docstring parsing of See Also sections for convenience. This automatically
#     hyperlinks plaintext functions and methods.
#     """
#     # Add the special parsing method from NumpyDocstring
#     method = sphinx.ext.napoleon.NumpyDocstring._parse_numpydoc_see_also_section
#     sphinx.ext.napoleon.GoogleDocstring._parse_numpydoc_see_also_section = method
#
#     def _parse_see_also_section(self, section: str):
#         """Copied from NumpyDocstring._parse_see_also_section()."""
#         lines = self._consume_to_next_section()
#
#         # Added: strip whitespace from lines to satisfy _parse_numpydoc_see_also_section()
#         for i in range(len(lines)):
#             lines[i] = lines[i].strip()
#
#         try:
#             return self._parse_numpydoc_see_also_section(lines)
#         except ValueError:
#             return self._format_admonition("seealso", lines)
#
#     sphinx.ext.napoleon.GoogleDocstring._parse_see_also_section = _parse_see_also_section
#
#
# def setup(app):
#     monkey_patch_parse_see_also()
#     app.connect("autodoc-skip-member", autodoc_skip_member)
#     app.connect("autodoc-process-bases", autodoc_process_bases)
#     # app.connect("autodoc-process-signature", autodoc_process_signature)
