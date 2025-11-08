from __future__ import annotations

from typing import Iterable, Mapping, Sequence

from fnmatch import fnmatchcase

from sphinx.application import Sphinx
from sphinx.util import logging
from sphinx import addnodes
from docutils import nodes


LOGGER = logging.getLogger(__name__)
CFG_KEY = "sphinx_tutorials_sig_shaper"

# ------------------------------
# Defaults (safe; do nothing)
# ------------------------------
_DEFAULTS: dict = {
    # 1) Visible prefix rewrites (UI-only; does not touch Sphinx attrs).
    #    Each entry: {"from": "old.prefix.", "to": "new.prefix.", "targets": [patterns]}
    #    If "targets" is omitted/empty, the rule is GLOBAL (applies everywhere).
    "visible_prefix_rules": [],

    # 2) Ensure a visible prefix for these targets if none exists
    #    (useful when Sphinx omits desc_addname). Supports exact, prefix, or glob.
    "ensure_prefix_targets": [],
    "ensure_prefix_text": "",   # e.g. "pkg." (include trailing dot if you want one)

    # 3) Strip nodes that follow desc_name for matching signatures
    #    (e.g., for "data" objects to hide type/value). Patterns support exact/prefix/glob.
    "strip_after_name": {
        "objtypes": ["data"],          # which objtypes to affect (e.g., ["data"])
        "targets": [],                 # list[str] of FQN patterns (exact | prefix | glob)
    },

    # 4) Rename fully-qualified names (class/function paths); also drops "class" artifacts.
    #    Mapping is exact or common-prefix. Example:
    #    {"old.pkg.Class": "new.alias", "old.pkg.Class.__call__": "new.alias"}
    "renames": {},

    # Logging & order
    "debug": False,
    "priority": 1000,  # run late
}


# ------------------------------
# Utilities
# ------------------------------

def _cfg(app: Sphinx) -> dict:
    raw = getattr(app.config, CFG_KEY, {}) or {}
    cfg = _DEFAULTS.copy()
    # shallow-merge dicts that are dicts in defaults
    for k, v in raw.items():
        if isinstance(v, dict) and isinstance(cfg.get(k), dict):
            merged = cfg[k].copy()
            merged.update(v)
            cfg[k] = merged
        else:
            cfg[k] = v
    return cfg


def _full_name(sig: addnodes.desc_signature) -> str:
    module = sig.get("module", "") or ""
    fullname = sig.get("fullname", "") or ""
    return f"{module}.{fullname}".strip(".")


def _is_prefix(s: str) -> bool:
    # Heuristic: treat as "prefix match" when string has no glob chars and we want
    # both exact match and startswith(old + ".") to count.
    return not any(ch in s for ch in "*?[]")


def _matches(full: str, patterns: Sequence[str]) -> bool:
    """
    Pattern semantics:
      - Exact match
      - Prefix match: "pkg.name" matches "pkg.name" and "pkg.name.*"
      - Glob: uses fnmatchcase
    """
    for pat in patterns:
        if not pat:
            continue
        if any(ch in pat for ch in "*?[]"):
            if fnmatchcase(full, pat):
                return True
        else:
            if full == pat or full.startswith(pat + "."):
                return True
    return False


def _rewrite_visible_prefix(
    sig: addnodes.desc_signature,
    old: str,
    new: str,
    *,
    full: str,
    targets: Sequence[str] | None = None,
) -> bool:
    """
    Rewrite only the *visible* dotted prefix (desc_addname) from `old` → `new`,
    but only if `full` (module.fullname) matches `targets` (exact/prefix/glob).
    If `targets` is falsy, the rule applies globally.
    Does not touch signature attributes (module/fullname).
    Returns True if any rewrite occurred.
    """
    if not old:
        return False
    if targets and not _matches(full, targets):
        return False

    rewritten = False
    for add in list(sig.findall(addnodes.desc_addname)):
        text = add.astext()
        if old in text:
            add.clear()
            add += addnodes.desc_addname("", text.replace(old, new))
            rewritten = True
    return rewritten


def _ensure_visible_prefix(sig: addnodes.desc_signature, prefix_text: str) -> None:
    """If a signature lacks desc_addname, synthesize one before desc_name."""
    if not prefix_text:
        return
    for i, child in enumerate(sig.children):
        if isinstance(child, addnodes.desc_name):
            sig.insert(i, addnodes.desc_addname("", prefix_text))
            return


def _strip_after_name(sig: addnodes.desc_signature) -> None:
    """Remove all nodes after desc_name (e.g., type/value annotations)."""
    seen_name = False
    for child in list(sig.children):
        if isinstance(child, addnodes.desc_name):
            seen_name = True
            continue
        if seen_name:
            sig.remove(child)


def _rename_signature(sig: addnodes.desc_signature, new_fqn: str) -> None:
    """
    Rebuild visible name and update signature attributes for a new FQN.
    Also removes Sphinx 'class' artifacts.
    """
    # Remove automatic "class " prefix if present
    if "sig_prefix" in sig:
        del sig["sig_prefix"]

    # Remove <em class="property">class</em>
    for em in list(sig.findall(nodes.emphasis)):
        if "property" in em.get("classes", []) and "class" in em.astext():
            em.parent.remove(em)

    # Rebuild visible name
    for ch in list(sig.children):
        if isinstance(ch, (addnodes.desc_addname, addnodes.desc_name)):
            sig.remove(ch)

    if "." in new_fqn:
        prefix, name = new_fqn.rsplit(".", 1)
        sig.insert(0, addnodes.desc_name("", name))
        sig.insert(0, addnodes.desc_addname("", prefix + "."))
        sig["module"] = prefix
        sig["fullname"] = name
    else:
        sig.insert(0, addnodes.desc_name("", new_fqn))
        sig["module"] = ""
        sig["fullname"] = new_fqn


def _maybe_debug(cfg: Mapping, msg: str) -> None:
    if cfg.get("debug"):
        LOGGER.info("[sigshaper] %s", msg)


# ------------------------------
# Transform A: visible prefix shaping + optional stripping
# ------------------------------

def _transform_visible_and_strip(app, domain, objtype, contentnode):
    if domain != "py":
        return
    desc = contentnode.parent
    if not isinstance(desc, addnodes.desc):
        return

    cfg = _cfg(app)

    # 1) apply visible prefix rules
    rules: Sequence[Mapping[str, object]] = cfg.get("visible_prefix_rules") or []
    # 2) ensure prefix
    ensure_targets = cfg.get("ensure_prefix_targets") or []
    ensure_text = cfg.get("ensure_prefix_text") or ""
    # 3) strip config
    strip_cfg: Mapping[str, object] = cfg.get("strip_after_name") or {}
    strip_objtypes: Sequence[str] = strip_cfg.get("objtypes") or []
    strip_targets: Sequence[str] = strip_cfg.get("targets") or []

    for sig in desc.findall(addnodes.desc_signature):
        full = _full_name(sig)

        # A1) rewrite visible prefixes (optionally gated by rule["targets"])
        did_rewrite = False
        for r in rules:
            old = str(r.get("from", "") or "")
            new = str(r.get("to", "") or "")
            targets = r.get("targets") or []  # optional per-rule scoping
            if old:
                changed = _rewrite_visible_prefix(
                    sig, old, new, full=full, targets=targets
                )
                did_rewrite = did_rewrite or changed

        # A2) synthesize prefix if asked and target matches
        if ensure_text and _matches(full, ensure_targets):
            if not did_rewrite:
                _ensure_visible_prefix(sig, ensure_text)
                _maybe_debug(cfg, f"inserted addname for {full}: '{ensure_text}'")

        # A3) stripping for configured objtypes + targets
        if objtype in strip_objtypes and _matches(full, strip_targets):
            _strip_after_name(sig)
            _maybe_debug(cfg, f"stripped trailing nodes for {objtype} {full}")


# ------------------------------
# Transform B: rename FQNs (exact or common-prefix)
# ------------------------------

def _transform_renames(app, domain, objtype, contentnode):
    if domain != "py":
        return
    desc = contentnode.parent
    if not isinstance(desc, addnodes.desc):
        return

    cfg = _cfg(app)
    renames: Mapping[str, str] = cfg.get("renames") or {}
    if not renames:
        return

    for sig in desc.findall(addnodes.desc_signature):
        full = _full_name(sig)

        new_fqn = None
        # exact or common-prefix mapping
        for old, new in renames.items():
            if full == old:
                new_fqn = new
                break
            # common-prefix (treat as move/alias)
            if _is_prefix(old) and (full.startswith(old + ".") or full == old):
                new_fqn = new + full[len(old):]
                break

        if not new_fqn:
            continue

        _rename_signature(sig, new_fqn)
        _maybe_debug(cfg, f"renamed {full} → {new_fqn}")


# ------------------------------
# Setup
# ------------------------------

def setup(app: Sphinx):
    # Register one dict config for simplicity
    app.add_config_value(CFG_KEY, _DEFAULTS.copy(), "env")

    # Run late so we act after other transforms
    def _connect(fn):
        app.connect(
            "object-description-transform",
            fn,
            priority=int((_cfg(app) or {}).get("priority", 1000)),
        )

    _connect(_transform_visible_and_strip)
    _connect(_transform_renames)

    return {"version": "1.0", "parallel_read_safe": True}
