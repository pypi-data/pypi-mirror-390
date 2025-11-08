import typing as t
import re
from decimal import Decimal
from pathlib import Path
from .structs import ConfigDict, DoubleLinkedDict
from .walk import walk_config
from .exceptions import CoercionError

CoerceFunction = t.Callable[[t.Any], t.Any]

CoercerBundle = t.Tuple[str, CoerceFunction]

CoercerArgument = t.Tuple[str, CoercerBundle]

CoercerMatcher = t.Callable[[str], t.Dict | None]


def matcher(regex: str) -> t.Callable[[str], None | t.Dict]:
    """
    Wrapper around a regex that always returns the
    group dict if there is a match.

    This requires that all regex have named groups.

    """
    rx = re.compile(regex, re.I)

    # pylint: disable=inconsistent-return-statements
    def _matcher(line: str) -> t.Dict | None:
        if not isinstance(line, str):
            return
        m = rx.match(line)
        if m:
            return m.groupdict()

    return _matcher


WINDOWS_PATH_REGEX = r'^(?P<value>[a-z]:\\(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*)$'
UNIX_PATH_REGEX = r"^(?P<value>(/[^\0/]*)*)$"


def coerce_path(value: str) -> Path:
    return Path(value)


coerce_win_path = (matcher(WINDOWS_PATH_REGEX), coerce_path)
coerce_unx_path = (matcher(UNIX_PATH_REGEX), coerce_path)

coerce_str_to_decimal = (matcher(r"^(?P<value>\d+\.\d+)$"), Decimal)


def handle_custom_coercers(
    custom_coercers: t.List[CoercerArgument] | None,
) -> t.Iterator[t.Tuple[str, t.Tuple[CoercerMatcher, CoerceFunction]]]:
    if not custom_coercers:
        return
    for name, _coercer in custom_coercers:
        if not _coercer:
            continue  # pragma: no cover
        regex_str, converter = _coercer

        if "(?P<value>" not in regex_str:
            raise CoercionError(
                "Custom matcher regular expressions must contain a named group `<value>`."
            )

        if not callable(converter):
            raise CoercionError(
                "Custom converters must be callable."
            )  # pragma: no cover

        yield name, (matcher(regex_str), converter)


def apply(
    config: ConfigDict, **kwargs
) -> ConfigDict:  # pragma pylint: disable=redefined-builtin
    coercers = DoubleLinkedDict()

    if kwargs.get("pathlib", False) is True:
        coercers.append("win_path", coerce_win_path)
        coercers.append("unix_path", coerce_unx_path)

    if kwargs.get("decimal", False) is True:
        coercers.append("decimal", coerce_str_to_decimal)

    # # add any custom coercers
    for name, custom_coercer in handle_custom_coercers(kwargs.get("coercers")):
        if not custom_coercer:
            continue  # pragma: no cover
        if name in coercers:
            coercers.replace(name, custom_coercer)
        else:
            coercers.prepend(name, custom_coercer)

    for section, _, key, value in walk_config(config):
        for coercer in coercers:
            if not coercer:
                continue  # pragma: no cover
            m, converter = coercer.content
            if m(value):
                new_value = converter(value)
                section[key] = new_value
                break

    return config
