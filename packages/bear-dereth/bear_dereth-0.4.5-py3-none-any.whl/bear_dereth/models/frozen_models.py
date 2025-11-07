"""Utilities for making objects immutable and hashable."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar, Self, overload

from pydantic import BaseModel, ConfigDict, Field

from bear_dereth.data_structs.freezing import FrozenDict, freeze

if TYPE_CHECKING:
    from funcy_bear.api import LitFalse, LitTrue


class FrozenModel(BaseModel):
    """A frozen Pydantic model that is immutable and hashable."""

    model_config = ConfigDict(arbitrary_types_allowed=True)
    cacheable: bool = Field(default=True, exclude=True)

    def get_hash(self) -> int:
        """Get the hash of the model based on its frozen representation."""
        return hash(self.model_dump())

    @classmethod
    def not_cacheable(cls) -> Self:
        """Mark this hash value as not cacheable."""
        return cls(cacheable=False)

    @property
    def frozen(self) -> FrozenDict:
        """Get a frozen representation of the model."""
        return self.model_dump(frozen=True)

    def frozen_dump(self) -> FrozenDict:
        """Dump the model to a frozen dictionary."""
        return self.model_dump(frozen=True)

    @overload
    def model_dump(self, frozen: LitTrue = True, *args, **kwargs) -> FrozenDict: ...

    @overload
    def model_dump(self, frozen: LitFalse = False, *args, **kwargs) -> dict: ...

    def model_dump(self, frozen: bool = True, *args, **kwargs) -> dict | FrozenDict:  # type: ignore[override]
        """Dump the model to a dictionary or frozen dictionary.

        Args:
            frozen (bool, optional): Whether to return a frozen dictionary. Defaults to False.
            *args: Additional positional arguments for Pydantic's model_dump.
            **kwargs: Additional keyword arguments for Pydantic's model_dump.

        Returns:
            dict | FrozenDict: The model as a dictionary or frozen dictionary.
        """
        if not frozen:
            return super().model_dump(*args, **kwargs)
        return freeze(super().model_dump(*args, **kwargs))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FrozenModel):
            return NotImplemented
        return self.frozen == other.frozen

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, FrozenModel):
            return NotImplemented
        return self.frozen != other.frozen

    def __hash__(self) -> int:
        if not self.cacheable:
            raise TypeError("This HashValue is not cacheable")
        return self.get_hash()


class BaseNotCacheable(BaseModel):
    """A singleton representing a non-cacheable value."""

    _instance: ClassVar[Self | None] = None

    model_config = ConfigDict(frozen=True)
    cacheable: bool = Field(default=False, exclude=True, frozen=True)

    def __new__(cls) -> Self:
        """Ensure only one instance of BaseNotCacheable exists."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            super(BaseNotCacheable, cls._instance).__init__()
        return cls._instance

    def __init__(self) -> None:
        """Cannot reinitialize the singleton."""

    def __hash__(self) -> int:
        raise TypeError("This object is not cacheable")


class BaseHashValue(FrozenModel):
    """A simple frozen model to hold a hash value for query caching."""

    value: list[Any] | None = None

    def combine(self, other: BaseHashValue, **kwargs) -> BaseHashValue:
        """Combine multiple hash values into one."""
        return BaseHashValue(value=[self, other], **kwargs)

    def __hash__(self) -> int:
        if not self.cacheable:
            raise TypeError("This HashValue is not cacheable")
        return super().__hash__()


class NotCacheable(BaseHashValue, BaseNotCacheable):
    """A singleton representing a non-cacheable hash value, contains a frozen cacheable=False flag."""

    def __init__(self) -> None:
        """Cannot reinitialize the singleton."""

    def __hash__(self) -> int:
        raise TypeError("This HashValue is not cacheable")
