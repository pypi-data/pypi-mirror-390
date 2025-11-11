#!/usr/bin/env python3
import os
import sys
from pathlib import Path, PosixPath, WindowsPath
from typing import Optional

# Detect proper Path subclass to inherit from based on the user's platform,
# since the top-level Path subclass is not designed to be subclassed directly
if sys.platform == "win32":
    BasePath = WindowsPath
else:
    BasePath = PosixPath


class ExpandedPath(BasePath):
    """
    Path subclass that automatically expands the user's home directory (i.e. ~)
    """

    def __new__(cls, path: str, **kwargs: object) -> "ExpandedPath":
        return super().__new__(cls, os.path.expanduser(path), **kwargs)


# Match pathlib defaults: universal newline translation unless overridden.
DEFAULT_TEXT_NEWLINE: Optional[str] = None


def read_text(
    path: Path,
    *,
    newline: Optional[str] = DEFAULT_TEXT_NEWLINE,
) -> str:
    with path.open("r", newline=newline) as file:
        return file.read()


def write_text(
    path: Path,
    text: str,
    *,
    newline: Optional[str] = DEFAULT_TEXT_NEWLINE,
) -> None:
    with path.open("w", newline=newline) as file:
        file.write(text)
