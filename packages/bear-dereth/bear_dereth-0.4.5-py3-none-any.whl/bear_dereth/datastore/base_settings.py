"""Base settings model for Pydantic models used in settings storage."""

from __future__ import annotations

from pydantic import BaseModel

from bear_dereth.datastore.columns import Columns
from bear_dereth.models.helpers import extract_field_attrs


class BaseSettingsModel(BaseModel):
    """Pydantic model for settings storage."""

    @classmethod
    def field_keys(cls) -> list[str]:
        """Get the list of field names."""
        return list(cls.model_fields.keys())

    @classmethod
    def field_values(cls) -> list[object]:
        """Get the list of field values."""
        return list(cls.model_fields.values())

    @classmethod
    def fields(cls) -> list[tuple[str, object]]:
        """Get the list of field items as (name, field) tuples."""
        return list(cls.model_fields.items())

    @classmethod
    def get_columns(cls) -> list[Columns]:
        """Get the list of columns for the settings model."""
        attrs: dict[str, Columns] = extract_field_attrs(cls, Columns)
        return list(attrs.values())
