"""Hatchling integration that surfaces `nbgv` as a version source."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from hatchling.plugin import hookimpl
from hatchling.version.source.plugin.interface import VersionSourceInterface

from .config import PluginConfig
from .runner import NbgvRunner
from .versioning import normalize_version_field


class NbgvVersionSource(VersionSourceInterface):
    """Hatch plugin that resolves package versions via `nbgv`."""

    PLUGIN_NAME = "nbgv"

    def __init__(self, *args: Any, **kwargs: Any) -> None:  # pragma: no cover
        super().__init__(*args, **kwargs)
        self._config: PluginConfig | None = None
        self._version_data: dict[str, Any] | None = None

    def get_version_data(self) -> dict[str, Any]:
        """Return the version mapping consumed by hatchling."""

        config = PluginConfig.from_mapping(Path(self.root), self.config)
        self._config = config
        runner = NbgvRunner(command=config.command)
        version = runner.get_version(config.working_directory)
        selected = version.get(config.version_field)
        if selected is None:
            message = (
                "Field '{field}' was not produced by 'nbgv get-version'"
            ).format(field=config.version_field)
            raise RuntimeError(message)
        normalized = normalize_version_field(selected, field=config.version_field)
        data = {
            "version": normalized,
            "metadata": version.as_dict(include_raw=True),
        }
        self._version_data = data
        return data

    def set_version(  # pragma: no cover - hatch isolates CLI so we cannot test
        self, version: str, version_data: dict[str, Any]
    ) -> None:
        message = (
            "The nbgv hatch plugin does not support mutating the project "
            "version. Create a Git tag instead."
        )
        raise NotImplementedError(message)


@hookimpl
def hatch_register_version_source() -> type[VersionSourceInterface]:
    """Register the nbgv version source with hatch."""

    return NbgvVersionSource


__all__ = [
    "NbgvVersionSource",
    "hatch_register_version_source",
]
