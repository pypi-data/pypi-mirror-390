from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from sphinx_tutorials.utils.copy import _copy_all_folders, copy_tutorials


def generate(
    docs_path: str | Path,
    tutorials_source_path: str | Path | None = None,
    tutorials_dest_path: str | Path | None = None,  # often same as docs
    *,
    style: bool = True,
    overwrite_style: bool = False,
    overwrite_tutorials: bool = False,
    include_suffixes: Iterable[str] | None = None,
    exclude_prefixes: Iterable[str] | None = None,
) -> None:
    """
    Generates tutorials.

    .. ipython:: python
        :okexcept:
        :okwarning:

        from pathlib import Path

        # Get the current working directory
        cwd = Path.cwd()
        print("Current Working Directory:", cwd)

        # List all files and folders in the current directory
        for item in cwd.iterdir():
            if item.is_file():
                print(f"File: {item.name}")
            elif item.is_dir():
                print(f"Folder: {item.name}")
    """

    if tutorials_source_path is not None and tutorials_dest_path is not None:
        copy_tutorials(
            source_path=tutorials_source_path,
            destination_path=tutorials_dest_path,
            overwrite=overwrite_tutorials,
            include_suffixes=include_suffixes,
            exclude_prefixes=exclude_prefixes,
        )

    if style:
        _copy_all_folders(
            source_path=Path(__file__).parent.absolute() / "_docs_files",
            destination_path=Path(docs_path),
            overwrite=overwrite_style,
        )
