"""Base file handler protocol and minimal implementation."""

from __future__ import annotations

from contextlib import suppress
from typing import TYPE_CHECKING, Self

from funcy_bear.files.base_file_handler import BaseFileHandler as BasicFileHandler

if TYPE_CHECKING:
    from pydantic import BaseModel


class BaseFileHandler[T](BasicFileHandler):
    """Minimal base for file-backed handlers.

    Owns: path/mode/encoding, lazy-open/close, properties, basic IO helpers,
    and lock hooks you can override. Knows nothing about data format.
    """

    def from_pydantic(self, model: BaseModel, exclude_none: bool = False, **kwargs) -> T:
        """Convert Pydantic model to YAML-compatible dictionary.

        Args:
            model: Pydantic model instance
            exclude_none: Exclude None values from output
            **kwargs: Additional model_dump arguments

        Returns:
            Dictionary representation suitable for YAML serialization
        """
        return model.model_dump(mode="json", exclude_none=exclude_none, **kwargs)  # type: ignore[return-value]

    def to_pydantic(self, model_class: type[BaseModel]) -> BaseModel:
        """Convert YAML data to Pydantic model.

        Args:
            model_class: Pydantic model class to create

        Returns:
            Validated Pydantic model instance

        Raises:
            ValueError: If data cannot be converted
        """
        data: T = self.read()
        try:
            return model_class.model_validate(data)
        except Exception as e:
            raise ValueError(f"Cannot convert data to {model_class.__name__}: {e}") from e

    def __enter__(self) -> Self:
        if self.closed:
            self.handle(open_file=True)
        return self

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        self.close()

    def __del__(self) -> None:
        with suppress(Exception):
            self.close()
