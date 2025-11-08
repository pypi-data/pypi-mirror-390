import typing as t
from collections import OrderedDict
from .structs import ConfigDict

WalkIterator = t.Iterator[t.Tuple[t.Any, str, str | int, t.Any]]


def join_keys(parent_path: str, key: str) -> str:
    if not parent_path:
        return key
    return f"{parent_path}.{key}"


def walk_config(cfg: ConfigDict) -> WalkIterator:
    def _recurse(
        parent_object: t.Any, full_key_path: str, key: str, key_value: t.Any
    ) -> WalkIterator:
        if isinstance(key_value, (OrderedDict, ConfigDict, dict)):
            # if its dict-like then loop through
            # the key/value pairs
            for key, value in key_value.items():
                _parent_key = join_keys(full_key_path, key)
                yield from _recurse(key_value, _parent_key, key, value)

        elif isinstance(key_value, (list, tuple)):
            # if its list-like then loop through
            # the items
            for index, item in enumerate(key_value):
                _parent_key = join_keys(full_key_path, str(index))
                yield from _recurse(key_value, _parent_key, str(index), item)

        else:
            # otherwise yield the value
            yield parent_object, full_key_path, key, key_value

    yield from _recurse(cfg, "", "", cfg)
