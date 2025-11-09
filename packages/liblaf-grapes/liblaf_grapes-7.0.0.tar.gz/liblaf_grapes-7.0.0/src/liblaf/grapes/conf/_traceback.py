import pydantic
import pydantic_settings as ps

from ._base import BaseConfig


class ConfigTraceback(BaseConfig):
    model_config = ps.SettingsConfigDict(env_prefix="TRACEBACK_")
    width: int | None = None
    show_locals: bool = True
    locals_hide_sunder: bool = True
    suppress: list[str] = pydantic.Field(
        default=["comet_ml", "liblaf.cherries", "pydantic", "rich.progress"]
    )
