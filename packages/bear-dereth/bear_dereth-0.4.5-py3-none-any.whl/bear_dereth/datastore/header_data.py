"""A module defining the HeaderData model for database header metadata."""

from __future__ import annotations

from typing import Any

from pydantic import Field, computed_field

from bear_dereth.datastore.common import UNIFIED_DATA_VERSION
from bear_dereth.models.frozen_models import FrozenDict, freeze
from bear_dereth.models.general import ExtraIgnoreModel


class HeaderData(ExtraIgnoreModel):
    """Database header metadata."""

    version: str = UNIFIED_DATA_VERSION  # TODO: This should be dynamic
    tables: list[str] = Field(default_factory=list)

    @computed_field
    def count(self) -> int:
        """Get the count of tables in the header."""
        return len(self.tables)

    def items(self) -> list[tuple[str, Any]]:
        """Return items for the header."""
        return list(self.model_dump(exclude_none=True).items())

    def add(self, table_name: str) -> None:
        """Add a table name to the header if not already present.

        Args:
            table_name: Name of the table to add.
        """
        if table_name not in self.tables:
            self.tables.append(table_name)

    def remove(self, table_name: str) -> None:
        """Remove a table name from the header if it exists.

        Args:
            table_name: Name of the table to remove.
        """
        if table_name in self.tables:
            self.tables.remove(table_name)

    def __hash__(self) -> int:
        """Get the hash of the header based on its version and tables."""
        return hash(f"HeaderData-{self.version}-{hash(tuple(sorted(self.tables)))}")

    def frozen_dump(self) -> FrozenDict:
        """Return a frozen representation of the header."""
        return freeze(self.model_dump(exclude_none=True))
