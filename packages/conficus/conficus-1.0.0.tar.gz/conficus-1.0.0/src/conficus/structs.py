import typing as t
from collections import OrderedDict
from .exceptions import ConfigError


class ConfigDict(OrderedDict):
    """
    ConfigDict is an override of standard dictionary
    to allow dot-named access to nested dictionary
    values.

    The standard nested call:

        config['parent']['child']

    can also be accessed as:

        config['parent.child']

    """

    # def __init__(self, *args, **kwargs):
    # super().__init__(*args, **kwargs)

    def get(self, key: str, default=None) -> t.Any:
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key: str) -> t.Any:
        if "." not in key:
            return super().__getitem__(key)
        segments = key.split(".")
        end = self
        for seg in segments:
            end = super(ConfigDict, end).__getitem__(seg)
        return end

    def __setitem__(self, key: str, value: t.Any):
        if isinstance(value, dict) and not isinstance(value, ConfigDict):
            value = ConfigDict(value)
        super().__setitem__(key, value)

    def __contains__(self, key: object) -> bool:
        if not isinstance(key, str):
            return super().__contains__(key)

        if "." not in key:
            return super().__contains__(key)
        segments = key.split(".")
        end = self
        contains = False
        for seg in segments:
            contains = super(ConfigDict, end).__contains__(seg)
            if not contains:
                return contains
            end = super(ConfigDict, end).__getitem__(seg)
        return contains

    def copy(self) -> "ConfigDict":
        "od.copy() -> a shallow copy of od"
        return self.__class__(self)


class ListNode:
    """Double Linked List Node"""

    name: str
    content: t.Any
    previous: "ListNode | None"
    next: "ListNode | None"

    def __init__(self, name: str, content: t.Any):
        self.name = name
        self.content = content
        self.previous = None
        self.next = None

    def __repr__(self) -> str:
        return '<ListNode "{}">'.format(self.name)

    def get_tail(self) -> "ListNode":
        node = self
        while node.next:
            node = node.next
        return node

    def get_root(self) -> "ListNode":
        node = self
        while node.previous:
            node = node.previous
        return node

    @property
    def is_root(self) -> bool:
        return self.previous is None and self.next is not None

    @property
    def is_tail(self) -> bool:
        return self.next is None and self.previous is not None

    @property
    def unlinked(self) -> bool:
        return self.previous is None and self.next is None

    def append(self, node: "ListNode") -> "ListNode":
        _next = self.next
        if _next:
            _next.previous = node
        self.next = node
        self.next.previous = self
        self.next.next = _next
        return node

    def prepend(self, node: "ListNode") -> "ListNode":
        _previous = self.previous
        if _previous:
            _previous.next = node
        self.previous = node
        self.previous.next = self
        self.previous.previous = _previous
        return node

    def replace(self, node: "ListNode") -> "ListNode":
        self.name = node.name
        self.content = node.content
        return self

    def remove(self) -> None:
        if self.is_root:
            if self.next:
                self.next.previous = None
        elif self.is_tail:
            if self.previous:
                self.previous.next = None
        elif not self.unlinked:
            if self.next:
                self.next.previous = self.previous
            if self.previous:
                self.previous.next = self.next
        self.previous = None
        self.next = None

    def __eq__(self, node: object) -> bool:
        if isinstance(node, self.__class__):
            return self.name == node.name and self.content == node.content
        return False  # pragma: no cover


class DoubleLinkedDict:
    """
    Double Linked List

    """

    root: ListNode | None

    def __init__(self, *args):
        self.root = None
        for name, content in args:
            self.append(name, content)

    @property
    def tail(self) -> ListNode | None:
        if self.root:
            return self.root.get_tail()
        return None

    def __len__(self) -> int:
        count = 0
        for _ in self:  # noqa
            count += 1
        return count

    def __getitem__(self, index: str) -> ListNode | None:
        for node in self:
            if node and node.name == index:
                return node
        return None

    def __setitem__(self, name: str, value: ListNode):
        self.append(name, value)

    def __contains__(self, name: str) -> bool:
        for node in self:
            if node and node.name == name:
                return True
        return False

    def replace(self, node_name: str, content: t.Any):
        if node_name not in self:
            raise ConfigError(f"List does not contain '{node_name}'.")
        node = self[node_name]
        if node:
            node.content = content

    def append(self, name: str, content: t.Any):
        node = ListNode(name, content)

        if not self.root:
            self.root = node
        else:
            self.root.get_tail().append(node)

    def prepend(self, name: str, content: t.Any):
        node = ListNode(name, content)
        if self.root:
            self.root.prepend(node)
        self.root = node

    def insert_before(self, node_name: str, name: str, content: t.Any):
        node = self[node_name]
        new_node = ListNode(name, content)
        if node:
            node.prepend(new_node)
        if self.root is node:
            self.root = new_node

    def insert_after(self, node_name: str, name: str, content: t.Any):
        node = self[node_name]
        new_node = ListNode(name, content)
        if node:
            node.append(new_node)

    def __iter__(self) -> t.Iterator[ListNode | None]:
        node = self.root
        while node:
            yield node
            node = node.next

    def iter_names(self) -> t.Iterator[str | None]:
        for node in self:
            if node:
                yield node.name

    def iter_values(self) -> t.Iterator[t.Any]:
        for node in self:
            if node:
                yield node.content
