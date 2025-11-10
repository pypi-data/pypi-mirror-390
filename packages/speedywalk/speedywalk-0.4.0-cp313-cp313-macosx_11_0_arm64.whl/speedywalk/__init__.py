"""
.. include:: ../../README.md
"""

from __future__ import annotations

import dataclasses
import functools
from collections.abc import Collection, Iterator
from pathlib import Path

from speedywalk import _core  # ty: ignore[unresolved-import]

_PathLike = Path | str


def walk(
    root: _PathLike,
    *,
    filter: str | Collection[str] = (),
    exclude: str | Collection[str] = (),
    ignore_hidden: bool = True,
    respect_git_ignore: bool = True,
    respect_global_git_ignore: bool = True,
    respect_git_exclude: bool = True,
    respect_ignore: bool = True,
    follow_symlinks: bool = False,
    max_depth: int | None = None,
    min_depth: int | None = None,
    max_filesize: int | None = None,
    threads: int = 0,
) -> Iterator[DirEntry]:
    """Walk a directory tree in parallel, yielding DirEntry objects.

    This function uses Rust's `ignore` crate for fast parallel directory traversal
    with built-in support for gitignore rules and other common ignore patterns.

    ## Arguments

    - `root`: The root directory to start walking from.
    - `filter`: Glob pattern(s) to filter files (any matching pattern includes the file).
      Example: `"*.py"` or `["*.py", "*.txt"]`
    - `exclude`: Glob pattern(s) to exclude files and directories.
      Example: `"**/node_modules"` or `["**/__pycache__", "**/node_modules"]`
    - `ignore_hidden`: If True, ignore hidden files and directories.
    - `respect_git_ignore`: If True, respect .gitignore files.
    - `respect_global_git_ignore`: If True, respect global gitignore.
    - `respect_git_exclude`: If True, respect .git/info/exclude.
    - `respect_ignore`: If True, respect .ignore files.
    - `follow_symlinks`: If True, follow symbolic links.
    - `max_depth`: Maximum depth to descend.
    - `min_depth`: Minimum depth before yielding entries.
    - `max_filesize`: Maximum file size in bytes to consider.
    - `threads`: Number of threads to use (0 for automatic, based on CPU count).

    ## Yields

    `DirEntry` objects representing files and directories found during the walk.

    ## Raises

    `OSError` if an error occurs while walking (e.g., permission denied).

    ## Example

    ```python
    # Match .py files at any depth (use ** for recursive matching)
    for entry in walk(".", filter="**/*.py", max_depth=2):
        if entry.is_file:
            print(entry.path)

    # Match only root-level .py files (no ** means current directory only)
    for entry in walk(".", filter="*.py"):
        print(entry.path)

    # Exclude patterns
    for entry in walk(".", filter="**/*.py", exclude=["**/test_*", "**/__pycache__"]):
        print(entry.path)
    ```
    """
    # Convert root to string
    root_str = str(root)

    # Convert filter to list
    filter_list = [filter] if isinstance(filter, str) else list(filter)

    # Convert exclude to list
    exclude_list = [exclude] if isinstance(exclude, str) else list(exclude)

    # Call the Rust implementation which returns an iterator
    walk_iterator = _core.walk(
        root_str,
        filter_list,
        exclude_list,
        ignore_hidden,
        respect_git_ignore,
        respect_global_git_ignore,
        respect_git_exclude,
        respect_ignore,
        follow_symlinks,
        max_depth,
        min_depth,
        max_filesize,
        threads,
    )

    # Wrap each core entry in a DirEntry and yield
    for core_entry in walk_iterator:
        yield DirEntry(_core_entry=core_entry)


@dataclasses.dataclass(frozen=True)
class DirEntry:
    """A directory entry returned by walk().

    This class wraps the Rust DirEntry and provides convenient access to
    path information and file type checks.
    """

    _core_entry: _core.DirEntry

    @functools.cached_property
    def path(self) -> Path:
        """The full path as a Path object."""
        return Path(self._core_entry.path)

    @functools.cached_property
    def path_str(self) -> str:
        """The full path as a string."""
        return self._core_entry.path

    @functools.cached_property
    def is_file(self) -> bool:
        """True if this entry is a regular file."""
        return self._core_entry.is_file

    @functools.cached_property
    def is_dir(self) -> bool:
        """True if this entry is a directory."""
        return self._core_entry.is_dir

    @functools.cached_property
    def is_symlink(self) -> bool:
        """True if this entry is a symbolic link."""
        return self._core_entry.is_symlink
