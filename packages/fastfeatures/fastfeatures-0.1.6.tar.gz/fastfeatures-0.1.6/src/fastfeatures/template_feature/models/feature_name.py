"""This module defines the data models for the FeatureName feature."""
from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
from sqlmodel import SQLModel, Field, Column, func


class FeatureNameBase(SQLModel):
    """Base model for FeatureName that contains shared fields."""
    pass


class FeatureName(FeatureNameBase, table=True):
    """Represents the FeatureName table in the database."""
    id: int | None = Field(primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime | None = Field(default_factory=lambda: datetime.now(timezone.utc))
    # This is an example field. Replace this with their actual feature fields.
    value: str | None = None

class FeatureNameCreate(FeatureNameBase):
    """Schema for creating a new FeatureName.

    This schema is used in the create endpoint.
    """
    # This is an example field. Replace this with their actual feature fields.
    value: str | None = None


class FeatureNameUpdate(SQLModel):
    """Schema for updating an existing FeatureName.

    This schema is used in the update endpoint.
    """
    # This is an example field. Replace this with their actual feature fields.
    value: str | None = None


class FeatureNameLoad(FeatureNameBase):
    """Schema for loading a FeatureName.

    This schema is used in the load and list endpoints.
    """
    id: int
    created_at: datetime
    updated_at: datetime
    # This is an example field. Replace this with their actual feature fields.
    value: str | None
