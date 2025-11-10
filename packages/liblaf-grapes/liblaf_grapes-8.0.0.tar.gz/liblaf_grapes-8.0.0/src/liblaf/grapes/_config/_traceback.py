from liblaf.grapes.conf import BaseConfig, Field, field


class ConfigTraceback(BaseConfig):
    width: Field[int | None] = field(default=None)
    extra_lines: Field[int] = field(default=1)
    show_locals: Field[bool] = field(default=True)
    locals_hide_sunder: Field[bool] = field(default=True)
    locals_hide_dunder: Field[bool] = field(default=True)
