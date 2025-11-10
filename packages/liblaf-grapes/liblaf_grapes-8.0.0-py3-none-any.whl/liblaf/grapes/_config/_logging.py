from pathlib import Path

from liblaf.grapes.conf import BaseConfig, Field, field


class ConfigLogging(BaseConfig):
    file: Field[Path | None] = field(default=None, env="LOG_FILE")
    hide_frame: Field[list[str]] = field(factory=lambda: ["rich.progress"])
    level: Field[int | str] = field(default="TRACE")
    time: Field[bool] = field(default=False, env="LOG_TIME")
