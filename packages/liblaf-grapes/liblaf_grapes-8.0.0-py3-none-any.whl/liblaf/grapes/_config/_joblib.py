from pathlib import Path

import platformdirs

from liblaf.grapes.conf import BaseConfig, Field, field


def _default_location() -> Path:
    return platformdirs.user_cache_path(appname="joblib")


class ConfigJoblibMemory(BaseConfig):
    bytes_limit: Field[int | str | None] = field(default="4G")
    location: Field[Path] = field(factory=_default_location)


class ConfigJoblib(BaseConfig):
    memory: ConfigJoblibMemory
