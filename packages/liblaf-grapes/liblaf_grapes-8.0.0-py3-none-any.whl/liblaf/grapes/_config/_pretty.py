from liblaf.grapes.conf import BaseConfig, Field, field


class ConfigPretty(BaseConfig):
    """.

    References:
        1. [wadler_lindig.pformat](https://docs.kidger.site/wadler_lindig/api/#wadler_lindig.pformat)
    """

    width: Field[int | None] = field(default=None)
    """a best-effort maximum width to allow. May be exceeded if there are unbroken pieces of text which are wider than this."""

    indent: Field[int] = field(default=2)
    """when the contents of a structured type are too large to fit on one line, they will be indented by this amount and placed on separate lines."""

    short_arrays: Field[bool | None] = field(default=None)
    """whether to print a NumPy array / PyTorch tensor / JAX array as a short summary of the form `f32[3,4]` (here indicating a `float32` matrix of shape `(3, 4)`)"""

    hide_defaults: Field[bool] = field(default=True)
    """whether to show the default values of dataclass fields."""

    show_type_module: Field[bool] = field(default=True)
    """whether to show the name of the module for a type: `somelib.SomeClass` versus `SomeClass`."""

    show_dataclass_module: Field[bool] = field(default=False)
    """whether to show the name of the module for a dataclass instance: `somelib.SomeClass()` versus `SomeClass()`."""

    show_function_module: Field[bool] = field(default=False)
    """whether to show the name of the module for a function: `<function some_fn>` versus `<function somelib.some_fn>`."""

    respect_pdoc: Field[bool] = field(default=True)

    short_arrays_threshold: Field[int] = field(default=100)
