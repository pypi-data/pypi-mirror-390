"""Python bindings that wrap the `nbgv` CLI."""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

from .command import ENV_COMMAND_OVERRIDE, discover_command, parse_command_tokens
from .errors import (
    NbgvCommandError,
    NbgvError,
    NbgvJsonError,
    NbgvNotFoundError,
)
from .models import GitVersion
from .runner import NbgvRunner
from .versioning import normalize_version_field

__all__ = [
    "ENV_COMMAND_OVERRIDE",
    "GitVersion",
    "NbgvCommandError",
    "NbgvError",
    "NbgvJsonError",
    "NbgvNotFoundError",
    "NbgvRunner",
    "discover_command",
    "forward",
    "get_version",
    "normalize_version_field",
    "parse_command_tokens",
]


def get_version(
    project_dir: Path | str = ".",
    *,
    command: str | Sequence[str] | None = None,
) -> GitVersion:
    """Return version metadata for *project_dir* via the `nbgv` CLI."""

    runner = NbgvRunner(command=command)
    return runner.get_version(project_dir)


def forward(
    args: Iterable[str] | None = None,
    *,
    project_dir: Path | str | None = None,
    command: str | Sequence[str] | None = None,
) -> int:
    """Forward *args* to the `nbgv` CLI using the shared command resolver."""

    runner = NbgvRunner(command=command)
    return runner.forward(args, cwd=project_dir)
