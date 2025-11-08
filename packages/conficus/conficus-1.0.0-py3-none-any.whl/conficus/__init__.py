import typing as t
from os import environ
from os import path
from pathlib import Path
from tomlkit import parse as parse_toml
from . import coerce
from . import inherit
from .readonly import ReadOnlyDict
from .structs import ConfigDict
from .exceptions import ConfigError  # noqa
from .exceptions import CoercionError  # noqa
from .exceptions import InheritanceError  # noqa

__all__ = (
    "read_config",
    "load",
    "ReadOnlyDict",
    "ConfigDict",
    "ConfigError",
    "CoercionError",
    "InheritanceError",
)

__version__ = "1.0.0"


def read_config(config_input: Path | str, encoding: str = "utf-8") -> t.List[str]:
    """
    read_config assumes `config_input` is one of the following in this
    order:

        1. a file path string.
        2. an environment variable name.
        3. a raw config string.

    """

    if isinstance(config_input, Path):
        return config_input.read_text(encoding=encoding).split("\n")

    if path.exists(config_input):
        return Path(config_input).read_text(encoding=encoding).split("\n")

    if config_input in environ and path.exists(environ[config_input]):
        return Path(environ[config_input]).read_text(encoding=encoding).split("\n")

    return config_input.split("\n")


def load(config_path: Path | str, **kwargs) -> ConfigDict | ReadOnlyDict:
    """
    keyword arguments:

        inheritance=False
        readonly=True
        use_pathlib=False
        use_decimal=False
        coercers=None

    """
    encoding: str = kwargs.get("encoding", "utf-8")
    use_pathlib: bool = kwargs.get("use_pathlib", False) or kwargs.get("pathlib", False)
    use_decimal: bool = kwargs.get("use_decimal", False) or kwargs.get("decimal", False)
    coercers: t.List[coerce.CoercerArgument] = kwargs.get("coercers", [])

    config = ConfigDict(
        parse_toml("\n".join(read_config(config_path, encoding=encoding)))
    )

    config = coerce.apply(
        config, pathlib=use_pathlib, decimal=use_decimal, coercers=coercers
    )

    if kwargs.get("inheritance", False) is True:
        config = inherit.apply(config)

    if kwargs.get("readonly", True) is True:
        config = ReadOnlyDict(config)

    return config
