"""Models for endpoints in Archive-it API."""

from typing import Any, ClassVar

from pydantic import BaseModel, Field, model_validator
from pydantic_core.core_schema import ValidationInfo


class MetadataValue(BaseModel):
    """A single metadata value item."""

    value: str | int | float = Field(..., description="The metadata value")
    id: str | None = Field(None, description="ID for the metadata value")
    model_config = {
        "extra": "forbid",
        "strict": True,  # Prevent type coercion (e.g., bool to int)
    }


class _SeedValidationMixin(BaseModel):
    """Internal mixin providing shared validation logic for all Seed models.

    This class should not be instantiated directly. It only provides
    the forbidden fields validation that is shared across all seed models.
    """

    # Class variable for forbidden fields (not an instance field)
    _forbidden_fields: ClassVar[set[str]] = {
        "id",
        "created_by",
        "created_date",
        "last_updated_by",
        "http_response_code",
        "last_checked_http_response_code",
        "active",
        "valid",
        "seed_type",
        "last_updated_date",
        "canonical_url",
        "login_username",
        "login_password",
    }

    @model_validator(mode="before")
    @classmethod
    def block_forbidden_fields(cls, data: Any, info: ValidationInfo) -> Any:
        """Reject forbidden fields if no system context is set."""
        if not isinstance(data, dict):
            return data
        allowed = bool((info.context or {}).get("allow_protected"))
        if not allowed:
            bad = cls._forbidden_fields.intersection(data)
            if bad:
                msg = f"Forbidden fields in user input: {', '.join(bad)}"
                raise ValueError(msg)
        return data


class Seed(_SeedValidationMixin):
    """Model representing a complete Seed object from Archive-it API.

    This model is used for API responses and contains all possible seed fields.
    Use this when receiving seed data from the API.
    """

    # Required fields (API always returns these)
    id: int = Field(..., description="Unique identifier for the seed")
    url: str = Field(..., description="URL of the seed")
    collection: int = Field(..., description="Collection ID the seed belongs to")
    crawl_definition: int = Field(
        ..., description="Crawl definition ID the seed belongs to"
    )
    active: bool = Field(..., description="Indicates if the seed is active")
    deleted: bool = Field(..., description="Indicates if the seed is deleted")
    last_updated_date: str = Field(
        ..., description="Date when the seed was last updated"
    )
    canonical_url: str = Field(..., description="Canonical URL of the seed")
    created_by: str | None = Field(..., description="User who created the seed")
    created_date: str | None = Field(..., description="Date when the seed was created")
    last_updated_by: str | None = Field(
        ..., description="User who last updated the seed"
    )
    publicly_visible: bool | None = Field(
        ..., description="Indicates if the seed is publicly visible"
    )
    http_response_code: int | None = Field(..., description="HTTP response code")
    valid: bool | None = Field(..., description="Indicates if the seed is valid")
    seed_type: str | None = Field(..., description="Type of the seed")
    login_username: str | None = Field(..., description="Login username for the seed")
    login_password: str | None = Field(..., description="Login password for the seed")
    metadata: dict | None = Field(..., description="Metadata for the seed")
    seed_groups: list | None = Field(
        ..., description="List of seed groups the seed belongs to"
    )

    model_config = {
        "extra": "allow",  # Allow extra fields from API responses
    }

    @classmethod
    def from_api(cls, payload: dict[str, Any]) -> "Seed":
        """Validate API response data; all fields allowed."""
        return cls.model_validate(payload, context={"allow_protected": True})

    @classmethod
    def from_system(cls, payload: dict[str, Any]) -> "Seed":
        """Validate system input; forbidden fields allowed. Alias for from_api()."""
        return cls.from_api(payload)

    @classmethod
    def from_user(cls, payload: dict[str, Any]) -> "Seed":
        """Validate user input; forbidden fields rejected."""
        return cls.model_validate(payload)


# Aliases for backward compatibility and semantic clarity
SeedResponse = Seed
SeedKeys = Seed


class SeedCreate(_SeedValidationMixin):
    """Model for creating a new seed (user input).

    Only exposes fields that are required/allowed for seed creation.
    The validation mixin automatically blocks protected fields.
    """

    # Required fields for creation
    url: str = Field(..., description="URL of the seed to create")
    collection: str | int = Field(..., description="Collection ID to add the seed to")
    crawl_definition: str | int = Field(
        ..., description="Crawl definition ID for the seed"
    )

    model_config = {
        "extra": "forbid",  # Forbid any fields not explicitly defined
    }


class SeedUpdate(_SeedValidationMixin):
    """Model for updating a seed (user input).

    Only exposes fields that users are permitted to update.
    The validation mixin automatically blocks protected fields.
    """

    # Only updateable fields
    metadata: dict[str, list[MetadataValue]] | None = Field(
        default=None, description="Metadata to update"
    )
    deleted: bool | None = Field(default=None, description="Mark seed as deleted")

    model_config = {
        "extra": "forbid",  # Forbid any extra fields
    }
