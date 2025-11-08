# pylint: disable=unused-argument
import typing as t
from .structs import ConfigDict


class ReadOnlyDict(ConfigDict):
    readonly: bool

    def __init__(self, src: ConfigDict):
        super().__init__(src)
        self.readonly = True

    def __setitem__(self, key: str, item: t.Any):
        if hasattr(self, "readonly"):
            raise TypeError("Key `{}` is read only!".format(key))
        if isinstance(item, ConfigDict):
            item = ReadOnlyDict(item)
        return super().__setitem__(key, item)

    def __delitem__(self, key: str):
        raise TypeError("Cannot update ReadOnlyDict.")

    def clear(self):
        raise TypeError("Cannot update ReadOnlyDict.")

    def pop(self, key: object, default: t.Any = None) -> t.Any:
        raise TypeError("Cannot update ReadOnlyDict.")

    def popitem(self, last: bool = True) -> t.Tuple[object, t.Any]:
        raise TypeError("Cannot update ReadOnlyDict.")

    def update(self, *args, **kwargs) -> None:
        raise TypeError("Cannot update ReadOnlyDict.")  # pragma: no cover

    def setdefault(self, key: str, default: t.Any = None) -> t.Any:
        raise TypeError("Cannot update ReadOnlyDict.")  # pragma: no cover

    def __copy__(self) -> "ReadOnlyDict":
        """We can only create a new ReadOnlyDict
        via initialization, so to make a copy we
        need to revert to ConfigDict and then
        create a new ReadOnlyDict from it.

        """
        new_copy = ConfigDict(self)
        return ReadOnlyDict(new_copy)
