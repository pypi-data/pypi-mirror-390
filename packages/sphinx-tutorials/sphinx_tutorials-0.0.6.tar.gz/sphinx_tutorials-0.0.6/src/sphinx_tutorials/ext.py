from __future__ import annotations

from pathlib import Path
from typing import Any

from sphinx_tutorials import __version__
from sphinx_tutorials.sphinx_tutorials import generate


def _resolve_path(base: Path, value: str | Path | None) -> Path | None:
    if value is None:
        return None
    p = Path(value)
    return p if p.is_absolute() else (base / p)


def _on_builder_inited(app) -> None:
    cfg: dict[str, Any] = getattr(app.config, "sphinx_tutorials_generate", {}) or {}

    docs_path = Path(app.confdir)

    tutorials_source_path = _resolve_path(docs_path, cfg.get("tutorials_source_path"))
    tutorials_dest_path = _resolve_path(docs_path, cfg.get("tutorials_dest_path"))

    generate(
        docs_path=docs_path,
        tutorials_source_path=tutorials_source_path,
        tutorials_dest_path=tutorials_dest_path,
        style=bool(cfg.get("style", True)),
        overwrite_style=bool(cfg.get("overwrite_style", False)),
        overwrite_tutorials=bool(cfg.get("overwrite_tutorials", False)),
        include_suffixes=cfg.get("include_suffixes"),
        exclude_prefixes=cfg.get("exclude_prefixes"),
    )

    # Ensure any newly copied local static assets are registered for this build
    static_dir = docs_path / "_static"
    if static_dir.exists():
        for js_file in static_dir.glob("*.js"):
            app.add_js_file(js_file.name)
        for css_file in static_dir.glob("*.css"):
            app.add_css_file(css_file.name)


def setup(app):
    app.add_config_value("sphinx_tutorials_generate", {}, "env")
    app.connect("builder-inited", _on_builder_inited)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
