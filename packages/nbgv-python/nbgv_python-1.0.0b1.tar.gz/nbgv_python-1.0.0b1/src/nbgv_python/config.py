"""Configuration helpers for the hatchling integration."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from .command import parse_command_tokens

_ALLOWED_KEYS = {
    "command",
    "version-field",
    "working-directory",
}


@dataclass(frozen=True, slots=True)
class PluginConfig:
    """Strongly typed view over the hatch configuration mapping."""

    command: tuple[str, ...] | None
    version_field: str
    working_directory: Path

    @classmethod
    def from_mapping(
        cls,
        root: Path,
        config: Mapping[str, Any] | None,
    ) -> "PluginConfig":
        """Parse user configuration under `[tool.hatch.version.nbgv]`."""

        data = dict(config or {})
        extra = set(data) - _ALLOWED_KEYS
        if extra:
            keys = ", ".join(sorted(extra))
            msg = f"Unsupported configuration keys: {keys}"
            raise ValueError(msg)

        command_value = data.get("command")
        command_tokens: tuple[str, ...] | None = None
        if command_value is not None:
            if isinstance(command_value, Sequence) and not isinstance(command_value, str):
                command_tokens = tuple(parse_command_tokens(tuple(command_value)))
            else:
                command_tokens = tuple(parse_command_tokens(str(command_value)))

        raw_field = data.get("version-field", "simple_version")
        if not isinstance(raw_field, str) or not raw_field.strip():
            msg = "'version-field' must be a non-empty string"
            raise ValueError(msg)
        version_field = raw_field.strip()

        raw_directory = data.get("working-directory")
        project_root = Path(root)
        if raw_directory is None:
            working_directory = project_root
        else:
            directory_path = Path(str(raw_directory))
            if not directory_path.is_absolute():
                working_directory = project_root / directory_path
            else:
                working_directory = directory_path
        return cls(command_tokens, version_field, working_directory)


__all__ = ["PluginConfig"]
