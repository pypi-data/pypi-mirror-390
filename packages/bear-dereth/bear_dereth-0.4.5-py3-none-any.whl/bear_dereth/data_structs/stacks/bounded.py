"""A bounded stack implementation with overflow strategies."""

from __future__ import annotations

from typing import Literal, LiteralString

from funcy_bear.ops.math.general import neg
from funcy_bear.ops.math.infinity import INFINITE
from funcy_bear.tools import SimpleStack

OverflowStrat = Literal["strict", "silent", "drop_oldest", "drop_newest"]
OverflowChoices: tuple[LiteralString, ...] = ("strict", "silent", "drop_oldest", "drop_newest")


class BoundedStack[T](SimpleStack[T]):
    """A stack with a maximum size."""

    def __init__(
        self,
        max_size: int = INFINITE,
        data: T | None = None,
        *,
        overflow: OverflowStrat = "silent",
        resize: bool = False,
    ) -> None:
        """Initialize a bounded stack with a maximum size."""
        super().__init__(data)
        self.max_size: int = max_size
        self.overflow: OverflowStrat = overflow if overflow in OverflowChoices else "silent"
        self.push_attr: LiteralString = f"_push_{self.overflow}"
        self.resize: bool = resize
        if self.size > self.max_size:
            self.stack = self.stack[-self.max_size :]

    def _push_strict(self, item: T) -> None:
        """Push an item onto the stack, raising an error if the stack is full."""
        if self.is_full:
            raise OverflowError("Stack overflow: maximum size reached")
        super().push(item)

    def _push_silent(self, item: T) -> None:
        """Push an item onto the stack, ignoring if the stack is full."""
        if not self.is_full:
            super().push(item)

    def _push_drop_newest(self, item: T) -> None:
        """Push an item onto the stack, removing the newest item if the stack is full."""
        if self.is_full:
            self.stack.pop()
        super().push(item)

    def _push_drop_oldest(self, item: T) -> None:
        """Push an item onto the stack, removing the oldest item if the stack is full."""
        if self.is_full:
            self.stack.pop(0)
        super().push(item)

    def push(self, item: T) -> None:
        """Push an item onto the stack. If the stack exceeds max_size, remove the oldest item."""
        getattr(self, self.push_attr)(item)

    def extend(self, items: list[T]) -> None:
        """Extend the stack with a list of items, respecting the maximum size."""
        for item in items:
            self.push(item)
        if self.resize and self.size > self.max_size:
            self.stack = self.stack[-self.max_size :]

    def resize_stack(
        self,
        new_size: int,
        *,
        strict: bool = False,
        keep_oldest: bool | None = None,
        keep_newest: bool | None = None,
    ) -> None:
        """Resize the stack to a new maximum size."""
        if not self.resize:
            raise RuntimeError("Stack resizing is not enabled for this stack.")
        if new_size <= 0:
            raise ValueError("new_size must be greater than 0")
        if new_size == self.max_size:
            return
        self.max_size = new_size
        if self.size > self.max_size:
            if self.overflow == "strict" or strict:
                raise OverflowError("Stack overflow: maximum size reached after resize")
            if keep_oldest is not None or self.overflow == "drop_newest":
                self.stack = self.stack[: self.max_size]
            elif keep_newest is not None or self.overflow == "drop_oldest":
                self.stack = self.stack[neg(self.max_size) :]
            else:  # drop_oldest by default
                self.stack = self.stack[neg(self.max_size) :]

    @property
    def is_full(self) -> bool:
        """Check if the stack is full."""
        return self.size >= self.max_size

    @property
    def capacity(self) -> int:
        """Get the maximum size of the stack."""
        return self.max_size

    @property
    def space_left(self) -> int:
        """Get the remaining space in the stack."""
        return self.max_size - self.size
