import typing as t

from .structs import ConfigDict
from .walk import walk_config


def _format_value(key: str, value: t.Any) -> str:
    name = key.split(".")[-1]
    if any(pw in name for pw in ("password", "passwd", "pwd", "secret", "salt")):
        return "**********"
    return str(value)


def pprint(cdict: ConfigDict, output: None | t.List[str] = None) -> str:
    """
    Formats a ConfigDict for visualization. Primarily for
    testing or debugging scenarios.

    """
    if not output:
        output = []

    for _, full_key, key, value in walk_config(cdict):
        # if not isinstance(value, (dict, list, tuple)):
        _value = _format_value(str(key), value)
        _output = "[config] {}: {}".format(full_key, _value)
        output.append(_output)
        # elif isinstance(value, (list, tuple)):
        #     _output = "[config] {}: {}".format(full_key, _format_sequence(value))
        #     output.append(_output)
    return "\n".join(output)
