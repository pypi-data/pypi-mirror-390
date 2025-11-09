from __future__ import annotations

from pathlib import Path

import pytest

from nbgv_python.config import PluginConfig


def test_plugin_config_defaults(tmp_path: Path) -> None:
    """Ensure defaults use the project root and simple_version field."""

    config = PluginConfig.from_mapping(tmp_path, None)
    assert config.command is None
    assert config.version_field == "simple_version"
    assert config.working_directory == tmp_path


def test_plugin_config_parses_command_and_directory(tmp_path: Path) -> None:
    """String commands should be normalised and directories resolved."""

    mapping = {
        "command": "python stub.py",
        "working-directory": "src/project",
        "version-field": "SimpleVersion",
    }
    config = PluginConfig.from_mapping(tmp_path, mapping)
    assert config.command == ("python", "stub.py")
    assert config.version_field == "SimpleVersion"
    assert config.working_directory == tmp_path / "src/project"


def test_plugin_config_rejects_unknown_keys(tmp_path: Path) -> None:
    """Reject unsupported configuration options."""

    with pytest.raises(ValueError):
        PluginConfig.from_mapping(tmp_path, {"unexpected": 1})
