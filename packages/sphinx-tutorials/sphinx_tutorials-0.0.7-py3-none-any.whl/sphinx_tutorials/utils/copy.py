from __future__ import annotations

import shutil
from collections.abc import Callable, Iterable
from pathlib import Path

from sphinx_tutorials.utils.py_rules import py_to_rst
from sphinx_tutorials.utils.table_tree import rst_table_from_path


def copy_tutorials(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    overwrite: bool = False,
    include_suffixes: Iterable[str] | None = None,
    exclude_prefixes: Iterable[str] | None = None,
):
    _copy_all_folders(
        source_path=source_path,
        destination_path=Path(destination_path) / Path(source_path).name,
        overwrite=overwrite,
        include_suffixes=include_suffixes,
        exclude_prefixes=exclude_prefixes,
    )

    include_extensions = []

    if include_suffixes is not None:
        for i in include_suffixes:
            if i == ".py":
                include_extensions.append(".rst")
            else:
                include_extensions.append(i)

    # rst_toctree_from_path(
    #     folder_path=destination_path / source_path.name,
    #     file_name=f"{source_path.name}.rst",
    #     include_extensions=include_extensions
    # )

    rst_table_from_path(
        folder_path=Path(destination_path) / Path(source_path).name,
        file_name=f"{Path(source_path).name}.rst",
        include_extensions=include_extensions,
        hidden_toctree_maxdepth=2,
        stub_root_dirname="tutorials-autotoc",
    )


def _copy_all_folders(
    source_path: str | Path,
    destination_path: str | Path,
    *,
    overwrite: bool = False,
    include_suffixes: Iterable[str] | None = None,
    exclude_prefixes: Iterable[str] | None = None,
):
    """
    Copies all folders from the source path to the destination path with options for overwriting,
    file type inclusion, and name exclusion.

    Parameters:
        source_path (str | Path): The source directory from which to copy folders.
        destination_path (str | Path): The destination directory to copy folders to.
        overwrite (bool): If True, existing files will be overwritten.
        include_suffixes (list of str): List of file suffixes to include in the copy.
        exclude_prefixes (list of str): List of file prefixes to exclude from the copy.
    """
    source = Path(source_path)
    destination = Path(destination_path)

    # Ensure the destination directory exists
    destination.mkdir(parents=True, exist_ok=True)

    def should_exclude(path: Path) -> bool:
        """Determine if a path should be excluded based on prefixes."""
        return (
            any(path.name.startswith(prefix) for prefix in exclude_prefixes)
            if exclude_prefixes
            else False
        )

    def copy_contents(source_dir: Path, dest_dir: Path):
        contents_copied = False

        for sub_item in source_dir.iterdir():
            if sub_item.is_dir():
                if should_exclude(sub_item):
                    print(f"Skipping excluded folder {sub_item}")
                    continue

                # Recursively call to copy contents of the subdirectory
                sub_dest_dir = dest_dir / sub_item.name

                if copy_contents(sub_item, sub_dest_dir):
                    contents_copied = True

            elif sub_item.is_file():
                if should_exclude(sub_item):
                    print(f"Skipping excluded file {sub_item}")
                    continue

                has_suffix = include_suffixes is None or sub_item.suffix in include_suffixes

                if has_suffix:
                    # Ensure parent directory exists before copying
                    dest_dir.mkdir(parents=True, exist_ok=True)
                    dest_file = dest_dir / sub_item.name

                    _copy_or_modify(source_file=sub_item, dest_file=dest_file, overwrite=overwrite)

                    contents_copied = True
        return contents_copied

    # Handling both directories and files at the root level
    for item in source.iterdir():
        if not should_exclude(item):
            if item.is_dir():
                new_dest_dir = destination / item.name

                if not copy_contents(item, new_dest_dir):
                    print(f"No contents were copied for {item}, skipping directory creation.")

            elif item.is_file():
                has_suffix = include_suffixes is None or item.suffix in include_suffixes

                if has_suffix:
                    dest_file = destination / item.name

                    dest_file.parent.mkdir(
                        parents=True, exist_ok=True
                    )  # Ensure parent directory exists

                    _copy_or_modify(source_file=item, dest_file=dest_file, overwrite=overwrite)

                else:
                    print(f"Skipping file {item}, does not meet suffix criteria")
        else:
            print(f"Skipping {item}, excluded by prefix")


# ----------------------------------------------------------------------


def _copy_or_modify(
    source_file: Path,
    dest_file: Path,
    *,
    overwrite: bool = False,
) -> None:
    source_file = Path(source_file)
    dest_file = Path(dest_file)

    if source_file.suffix == ".py":
        _modify_and_save_as_rst(
            source_file=source_file, destination_path=dest_file.parent, modify_function=py_to_rst
        )
    else:
        _copy_file(source_file=source_file, dest_file=dest_file, overwrite=overwrite)


def _copy_file(source_file: Path, dest_file: Path, overwrite: bool = False):
    """
    Copies a single file from source to destination with an option to overwrite.

    Parameters:
        source_file (Path): The source file path.
        dest_file (Path): The destination file path.
        overwrite (bool): If True, will overwrite the file if it exists.
    """

    if dest_file.exists() and overwrite:
        dest_file.unlink()  # Remove the file if it exists and overwrite is True
        shutil.copy2(source_file, dest_file)  # shutil.copy2 also copies metadata

        print(f"Overwritten {dest_file}")

    elif not dest_file.exists():
        shutil.copy2(source_file, dest_file)

        print(f"Copied {source_file} to {dest_file}")
    else:
        print(f"Skipped {dest_file}, already exists and overwrite is False")


def _modify_and_save_as_rst(
    source_file: Path, destination_path: Path, *, modify_function: Callable | None = None
) -> None:
    """
    Reads a file, modifies its contents if a modify function is provided,
    and saves it with a .rst extension.
    """
    # Read the content of the source file
    with open(source_file, encoding="utf-8") as file:
        content = file.read()

    # Apply modifications if a modification function is provided
    if modify_function is not None:
        content = modify_function(content)

    # Prepare the destination file path
    destination_file = destination_path / (source_file.stem + ".rst")

    # ---- INSERT LABEL AT TOP ----
    # Determine the root of the copied folder (first parent of destination_path)

    # Folder name you want to start after
    marker = "tutorials"

    parts = destination_file.with_suffix("").parts  # Remove suffix, split into parts

    if marker in parts:
        idx = parts.index(marker)
        after_marker = parts[idx:]  # include tutorials and everything after

        # Create a lowercase, hyphen-joined label
        label = "-".join(part.lower() for part in after_marker)

        # Prepend to the content
        content = f".. _{label}:\n\n{content}"
    else:
        print("Folder not found")

    # -----------------------------

    # todo: overwrite

    # Save the modified content to a new .rst file
    with open(destination_file, "w", encoding="utf-8") as file:
        file.write(content)

    print(f"Saved modified file as {destination_file}")
