# from __future__ import annotations
# from pathlib import Path
# from typing import Iterable
#
#
# def rst_toctree_from_path(
#         folder_path: str | Path,
#         file_name: str,
#         include_extensions: Iterable[str] = (".ipynb", ".rst")
# ):
#     """
#     Writes or appends to a file specified by 'file_name' in the directory 'folder_path'
#     with a TOC tree based on the subfolder structure of 'folder_path'. Only generates
#     TOC tree sections for directories that contain relevant files.
#     """
#
#     print(f"GENERATING TOC TREE: {folder_path}")
#
#     folder_path = Path(folder_path)
#
#     if not folder_path.exists():
#         raise FileNotFoundError(f"{folder_path} directory does not exist")
#
#     # Determine the output file path outside of the 'folder_path' and check existence
#     template_file = folder_path.parent.absolute() / f"_{file_name}"  # a seperate file
#     file_exists = template_file.exists()
#
#     rst_content = ""
#
#     # Add top-level title if the file does not exist
#     existing_content = ""
#
#     if file_exists:  # template file exists
#         with open(template_file, 'r') as file:
#             existing_content = file.read()
#     else:
#         # add a title if template file does not exist
#         overall_title = folder_path.name.replace("_", " ")  # .title()
#         existing_content += f"{overall_title}\n{('=' * len(overall_title))}\n"
#
#     # Gather top-level files in folder_path
#     top_level_files = [
#         f for f in folder_path.glob("*") if
#         f.is_file() and
#         f.suffix in include_extensions and
#         not f.name.startswith(('.', '_'))
#     ]
#
#     rst_content += _generate_toctree_entries(top_level_files, prefix=f"{folder_path.stem}/")
#
#     # Process subfolders recursively
#     folders = [
#         f for f in folder_path.rglob('*') if f.is_dir()
#     ]
#
#     for root in folders:
#
#         files = [
#             f for f in root.iterdir() if
#             f.is_file() and
#             f.suffix in include_extensions and
#             not f.name.startswith(('.', '_'))
#         ]
#
#         if files:
#             rel_path = root.relative_to(folder_path)
#             depth = len(rel_path.parts) - 1
#
#             # title for each section
#             title = rel_path.name.replace("_", " ")  # .title()
#
#             rst_content += _generate_section_header(title, depth) + _generate_toctree_entries(
#                 files=files, prefix=f"{folder_path.stem}/{rel_path}/"
#             )
#
#     # Write or append the content to the file
#     # mode = 'a' if file_exists else 'w'
#     output_file = folder_path.parent.absolute() / file_name  # a seperate file
#
#     with open(output_file, 'w') as file:
#         file.write(existing_content + rst_content)
#
#     print(f"Content {'appended to' if file_exists else 'written to'} {template_file}")
#
#
# def _generate_toctree_entries(files: Iterable[Path], prefix: str = "") -> str:
#     """Generates TOC tree entries for given files with an optional prefix."""
#     content = ""
#     if files:
#         content += ".. toctree::\n   :maxdepth: 1\n\n"
#         for file in files:
#             entry = f"{prefix}{file.stem}" if file.suffix == ".rst" else f"{prefix}{file.name}"
#             content += f"   {entry}\n"
#     return content
#
#
# def _generate_section_header(title: str, level: int) -> str:
#     """Generates a section header with a dynamic separator based on the level."""
#     separators = ['=', '-', '~', '+', '*']
#     sep = separators[level % len(separators)]
#     return f"\n{title}\n{sep * len(title)}\n\n"
#
#

# ------------------------ NEW -----------------------------------------

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path


def rst_toctree_from_path(
    folder_path: str | Path, file_name: str, include_extensions: Iterable[str] = (".ipynb", ".rst")
):
    """
    Writes or appends to a file specified by 'file_name' in the directory 'folder_path'
    with a TOC tree based on the subfolder structure of 'folder_path'. Generates
    headers for all subfolders in the hierarchy, and preserves template content.
    """

    print(f"GENERATING TOC TREE: {folder_path}")

    folder_path = Path(folder_path)
    if not folder_path.exists():
        raise FileNotFoundError(f"{folder_path} directory does not exist")

    # Template and output files
    template_file = folder_path.parent / f"_{file_name}"
    output_file = folder_path.parent / file_name

    # Load template or create a default title
    if template_file.exists():
        with open(template_file, encoding="utf-8") as f:
            existing_content = f.read()
        file_exists = True
    else:
        overall_title = folder_path.name.replace("_", " ")
        existing_content = f"{overall_title}\n{('=' * len(overall_title))}\n\n"
        file_exists = False

    # Start generating new RST content
    rst_content = ""

    # Top-level files (directly under folder_path)
    top_level_files = [
        f
        for f in sorted(folder_path.glob("*"))
        if f.is_file() and f.suffix in include_extensions and not f.name.startswith((".", "_"))
    ]
    rst_content += _generate_toctree_entries(top_level_files, prefix=f"{folder_path.stem}/")

    # All subfolders depth-first
    folders = sorted(f for f in folder_path.rglob("*") if f.is_dir())

    for root in folders:
        # Skip folders that don't eventually lead to files
        if not any(
            f.is_file() and f.suffix in include_extensions and not f.name.startswith((".", "_"))
            for f in root.rglob("*")
        ):
            continue

        # Generate headers for all subfolders
        rel_path = root.relative_to(folder_path)
        depth = len(rel_path.parts) - 1
        title = rel_path.name.replace("_", " ")
        rst_content += _generate_section_header(title, depth)

        # Add toctree only if folder has files
        files = [
            f
            for f in sorted(root.iterdir())
            if f.is_file() and f.suffix in include_extensions and not f.name.startswith((".", "_"))
        ]
        if files:
            rst_content += _generate_toctree_entries(
                files, prefix=f"{folder_path.stem}/{rel_path}/"
            )

    # Write final RST with template + generated content
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(existing_content + rst_content)

    print(f"Content {'appended to' if file_exists else 'written to'} {output_file}")


def _generate_toctree_entries(files: Iterable[Path], prefix: str = "") -> str:
    if not files:
        return ""
    content = ".. toctree::\n   :maxdepth: 1\n\n"
    for file in files:
        entry = f"{prefix}{file.stem}" if file.suffix == ".rst" else f"{prefix}{file.name}"
        content += f"   {entry}\n"
    return content + "\n"


def _generate_section_header(title: str, level: int) -> str:
    separators = ["=", "-", "~", "+", "*"]
    sep = separators[level % len(separators)]
    return f"\n{title}\n{sep * len(title)}\n\n"
