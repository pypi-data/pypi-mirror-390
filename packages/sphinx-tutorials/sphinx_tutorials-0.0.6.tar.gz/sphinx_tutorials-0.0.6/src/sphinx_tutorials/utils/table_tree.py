from __future__ import annotations

import os
import re
from collections.abc import Iterable
from pathlib import Path


def rst_table_from_path(
    folder_path: str | Path,
    file_name: str,
    include_extensions: Iterable[str] = (".rst", ".ipynb"),
    hidden_toctree_maxdepth: int = 2,
    stub_root_dirname: str = "tutorials-autotoc",  # where folder stub pages are written
) -> None:
    """
    Build an index page with sectioned 2-col tables (link + description) and
    also a *nested* hidden toctree that mirrors folder hierarchy.

    How hierarchy is achieved:
      - We generate small per-folder "stub" pages under <source>/<stub_root_dirname>/...
      - Each stub contains a toctree of its *immediate* files and child folder stubs.
      - The main page includes a single hidden toctree pointing to:
          * top-level files, and
          * top-level folder stubs.
        Sphinx follows stubs recursively, preserving hierarchy for sidebars/breadcrumbs.

    The visible main page remains just your tables; the toctrees are all hidden.
    """
    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"{folder_path} directory does not exist")

    source_root = folder_path.parent  # where main page lives
    template_file = source_root / f"_{file_name}"
    output_file = source_root / file_name
    stub_root = source_root / stub_root_dirname  # where we write folder stub pages
    stub_root.mkdir(parents=True, exist_ok=True)

    # Read template (optional) or synthesize a title
    if template_file.exists():
        existing_content = template_file.read_text(encoding="utf-8")
        file_exists = True
    else:
        overall_title = folder_path.name.replace("_", " ")
        existing_content = f"{overall_title}\n{('=' * len(overall_title))}\n\n"
        file_exists = False

    include_extensions = tuple(include_extensions)

    # ---------- Scan: determine relevant dirs, direct files, and child dirs ----------
    direct_files: dict[Path, list[Path]] = {}
    children_dirs: dict[Path, list[Path]] = {}
    relevant_dirs: set[Path] = set()

    # Walk once to gather immediate files per dir and note relevance
    for dirpath, dirnames, filenames in os.walk(folder_path, topdown=True):
        dirnames[:] = sorted(dirnames, key=_natural_key)  # stable traversal
        filenames_sorted = sorted(filenames, key=_natural_key)
        root = Path(dirpath)

        files_here = [
            root / fn
            for fn in filenames_sorted
            if not fn.startswith((".", "_")) and (root / fn).suffix in include_extensions
        ]
        if files_here:
            direct_files[root] = files_here
            # mark this dir and ancestors as relevant
            cur = root
            while True:
                relevant_dirs.add(cur)
                if cur == folder_path:
                    break
                cur = cur.parent

        # fill children dirs (filter to only immediate subdirs; we'll prune later)
        children_dirs[root] = [root / d for d in dirnames]

    # Prune children to only those that are relevant
    for parent, kids in list(children_dirs.items()):
        children_dirs[parent] = [k for k in kids if k in relevant_dirs]

    # ---------- Build the visible tables (top-down order) ----------
    parts: list[str] = []

    # Top-level files table (no extra header)
    top_files = _collect_files(folder_path, include_extensions)
    if top_files:
        parts.append(
            _generate_table_section(
                title=None,
                files=top_files,
                link_prefix=f"{folder_path.stem}/",
            )
        )

    # Subfolders: emit header for every relevant dir (excluding the root)
    for dirpath, dirnames, _filenames in os.walk(folder_path, topdown=True):
        dirnames[:] = sorted(dirnames, key=_natural_key)
        root = Path(dirpath)
        if root == folder_path or root not in relevant_dirs:
            continue

        rel_path = root.relative_to(folder_path)
        depth = len(rel_path.parts) - 1  # first level => 0 (uses '-')
        title = rel_path.name.replace("_", " ")
        parts.append(_generate_section_header(title, depth))

        files_here = direct_files.get(root, [])
        if files_here:
            parts.append(
                _generate_table_section(
                    title=None,
                    files=files_here,
                    link_prefix=f"{folder_path.stem}/{rel_path}/",
                )
            )

    # ---------- Write folder stub pages with nested toctrees ----------
    # Each relevant directory gets a stub page under stub_root/<rel>/index.rst
    for d in sorted(relevant_dirs, key=lambda p: _natural_key(str(p.relative_to(folder_path)))):
        rel_dir = d.relative_to(folder_path) if d != folder_path else Path(".")
        stub_dir = (stub_root / rel_dir) if rel_dir != Path(".") else stub_root
        stub_dir.mkdir(parents=True, exist_ok=True)
        stub_index = stub_dir / "index.rst"

        # Title
        folder_title = (folder_path.name if d == folder_path else d.name).replace("_", " ")

        # Child file refs (from the stub's directory)
        file_refs = [
            _rel_doc_ref(from_dir=stub_dir, target=p, strip_rst_suffix=True)
            if p.suffix == ".rst"
            else _rel_doc_ref(from_dir=stub_dir, target=p, strip_rst_suffix=False)
            for p in direct_files.get(d, [])
        ]

        # Child folder stub refs (to their own index pages)
        child_stub_refs = []
        for child in children_dirs.get(d, []):
            child_rel = child.relative_to(folder_path)
            child_stub_dir = stub_root / child_rel
            # reference the child's index.rst *docname* from this stub
            child_stub_refs.append(
                _rel_doc_ref(
                    from_dir=stub_dir, target=child_stub_dir / "index.rst", strip_rst_suffix=True
                )
            )

        # Write stub page (toctree can be hidden or visible; we keep it hidden by default)
        stub_index.write_text(
            _render_stub_page(
                folder_title, file_refs, child_stub_refs, hidden_toctree_maxdepth, hidden=True
            ),
            encoding="utf-8",
        )

    # ---------- Hidden toctree on the main page (entry point to the nested tree) ----------
    # Main page should list top-level files (relative to source_root) and
    # top-level folder stubs (autotoc/<top>/index).
    main_hidden_refs: list[str] = []

    # Top-level files under folder_path
    for f in top_files:
        main_hidden_refs.append(
            _rel_doc_ref(from_dir=source_root, target=f, strip_rst_suffix=(f.suffix == ".rst"))
        )

    # Top-level relevant subfolders (direct children of folder_path)
    for sub in sorted(children_dirs.get(folder_path, []), key=lambda p: _natural_key(p.name)):
        if sub in relevant_dirs:
            child_stub = stub_root / sub.relative_to(folder_path) / "index.rst"
            main_hidden_refs.append(
                _rel_doc_ref(from_dir=source_root, target=child_stub, strip_rst_suffix=True)
            )

    if main_hidden_refs:
        parts.append(_generate_hidden_toctree(main_hidden_refs, maxdepth=hidden_toctree_maxdepth))

    # ---------- Write the final main page ----------
    output_file.write_text(existing_content + "".join(parts), encoding="utf-8")
    print(f"Content {'appended to' if file_exists else 'written to'} {output_file}")


# ========================== helpers ==========================


def _natural_key(s: str) -> tuple:
    """Natural sort key: 'a2' < 'a10', case-insensitive."""
    return tuple(int(t) if t.isdigit() else t.lower() for t in re.findall(r"\d+|\D+", s))


def _collect_files(folder: Path, include_extensions: Iterable[str]) -> list[Path]:
    return [
        f
        for f in sorted(folder.iterdir(), key=lambda p: _natural_key(p.name))
        if f.is_file() and f.suffix in include_extensions and not f.name.startswith((".", "_"))
    ]


def _generate_table_section(
    title: str | None,
    files: Iterable[Path],
    link_prefix: str = "",
) -> str:
    rows = []
    for file in files:
        if file.suffix == ".rst":
            link_target = f"{link_prefix}{file.stem}"
            link_text = _prettify_name(file.stem)
            link_cell = f":doc:`{link_text} <{link_target}>`"
            description = _extract_description_from_rst(file)
        else:
            link_target = f"{link_prefix}{file.name}"
            link_text = _prettify_name(file.stem)
            link_cell = f"`{link_text} <{link_target}>`_"
            description = ""
        rows.append((link_cell, description))

    header = []
    if title:
        header.append(title + "\n" + "-" * len(title) + "\n")

    # No header row + add :class: table-rst
    table_lines = [
        ".. list-table::",
        "   :class: table-rst",
        "   :widths: 30 70",
        "   :header-rows: 0",
        "",
    ]
    for link_cell, desc_cell in rows:
        table_lines.extend(
            [
                "   * - " + link_cell,
                "     - " + (desc_cell.strip() if desc_cell else ""),
            ]
        )
    return ("".join(header)) + "\n".join(table_lines) + "\n\n"


# def _generate_table_section(
#         title: str | None,
#         files: Iterable[Path],
#         link_prefix: str = "",
# ) -> str:
#     rows = []
#     for file in files:
#         if file.suffix == ".rst":
#             link_target = f"{link_prefix}{file.stem}"
#             link_text = _prettify_name(file.stem)
#             link_cell = f":doc:`{link_text} <{link_target}>`"
#             description = _extract_description_from_rst(file)
#         else:
#             link_target = f"{link_prefix}{file.name}"
#             link_text = _prettify_name(file.stem)
#             link_cell = f"`{link_text} <{link_target}>`_"
#             description = ""
#         rows.append((link_cell, description))
#
#     header = []
#     if title:
#         header.append(title + "\n" + "-" * len(title) + "\n")
#
#     table_lines = [
#         ".. list-table::",
#         "   :widths: 25 75",
#         "   :header-rows: 1",
#         "",
#         "   * - Page",
#         "     - Description",
#     ]
#     for link_cell, desc_cell in rows:
#         table_lines.extend([
#             "   * - " + link_cell,
#             "     - " + (desc_cell.strip() if desc_cell else ""),
#         ])
#     return ("".join(header)) + "\n".join(table_lines) + "\n\n"


def _prettify_name(stem: str) -> str:
    return stem.replace("_", " ").strip()


def _generate_section_header(title: str, level: int) -> str:
    separators = ["=", "-", "~", "+", "*"]
    sep = separators[level % len(separators)]
    return f"\n{title}\n{sep * len(title)}\n\n"


def _extract_description_from_rst(path: Path) -> str:
    """
    Extract the first descriptive paragraph after the top-level title,
    stopping at the first directive ('.. '), field list (':param:' etc.),
    or the next section underline.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return ""

    lines = text.splitlines()
    i = 0
    n = len(lines)

    def is_underline(line: str, length: int) -> bool:
        s = line.strip()
        return bool(s) and len(s) >= length and len(set(s)) == 1 and s[0] in "= -~+*^`'\"_:#"

    # find top title (line + underline)
    while i + 1 < n:
        if lines[i].strip() and is_underline(lines[i + 1], len(lines[i].rstrip())):
            i += 2
            break
        i += 1

    # skip blank lines
    while i < n and not lines[i].strip():
        i += 1

    desc_lines: list[str] = []
    while i < n:
        line = lines[i]
        if line.lstrip().startswith(".. "):
            break
        if i + 1 < n and lines[i].strip() and is_underline(lines[i + 1], len(lines[i].rstrip())):
            break
        if line.lstrip().startswith(":"):
            break
        if not line.strip() and desc_lines:
            break
        desc_lines.append(line)
        i += 1

    return " ".join(l.strip() for l in desc_lines).strip()  # noqa: E741


def _generate_hidden_toctree(doc_refs: list[str], maxdepth: int = 2) -> str:
    """
    Hidden toctree so Sphinx computes relations/sidebars without rendering a ToC.
    """
    lines = [
        ".. toctree::",
        f"   :maxdepth: {maxdepth}",
        "   :hidden:",
        "   :titlesonly:",
        "",
    ]
    for ref in doc_refs:
        lines.append(f"   {ref}")
    return "\n".join(lines) + "\n"


def _rel_doc_ref(from_dir: Path, target: Path, strip_rst_suffix: bool) -> str:
    """
    Produce a Sphinx doc reference from 'from_dir' to 'target'.
    If strip_rst_suffix=True and target endswith .rst, drop the suffix.
    Always use forward slashes.
    """
    rel = os.path.relpath(target, from_dir)
    rel = rel.replace(os.sep, "/")
    if strip_rst_suffix and rel.endswith(".rst"):
        rel = rel[:-4]
    return rel


def _render_stub_page(
    title: str,
    file_refs: list[str],
    child_stub_refs: list[str],
    maxdepth: int,
    hidden: bool = True,
) -> str:
    """
    Create the contents of a folder stub page. If 'hidden' is True, the toctree
    won't render on the stub page (keeps the page minimal), but it still
    establishes hierarchy for Sphinx.
    """
    header = f"{title}\n{'-' * len(title)}\n\n"
    opt_hidden = "   :hidden:\n" if hidden else ""
    lines = [
        header,
        ".. toctree::\n",
        f"   :maxdepth: {maxdepth}\n",
        "   :titlesonly:\n",
        opt_hidden,
        "\n",
    ]
    for ref in file_refs + child_stub_refs:
        lines.append(f"   {ref}\n")
    lines.append("\n")
    return "".join(lines)
