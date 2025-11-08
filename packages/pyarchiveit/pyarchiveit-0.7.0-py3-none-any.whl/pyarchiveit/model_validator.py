"""Validation utilities with standardized error handling."""

import logging
from typing import Any, Literal, TypeVar

from pydantic import BaseModel, ValidationError

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class ModelValidator:
    """Wrapper for Pydantic validation with standardized error handling."""

    @staticmethod
    def validate(
        model: type[T],
        data: dict[str, Any],
        context: str = "",
        source: Literal["system", "user", "api"] = "system",
    ) -> T:
        """Validate data against a Pydantic model.

        Args:
            model: The Pydantic model class to validate against
            data: The data to validate
            context: Context string for error logging (e.g., "seed ID 123")
            source: Source of the data - "system"/"api" (allows protected fields),
                   "user" (rejects protected fields). Defaults to "system".

        Returns:
            Validated model instance

        Raises:
            ValidationError: If validation fails
        """
        try:
            # Use the appropriate validation method based on source
            if source == "user":
                # User input - forbidden fields are rejected
                if hasattr(model, "from_user"):
                    return model.from_user(data)  # type: ignore[attr-defined]
                return model.model_validate(data)
            if source in {"system", "api"}:
                # System/API data - forbidden fields are allowed
                if hasattr(model, "from_system"):
                    return model.from_system(data)  # type: ignore[attr-defined]
                if hasattr(model, "from_api"):
                    return model.from_api(data)  # type: ignore[attr-defined]
                return model.model_validate(data, context={"allow_protected": True})
            # Fallback to standard validation
            return model.model_validate(data)
        except ValidationError as e:
            error_msg = f"Validation error for {model.__name__}"
            if context:
                error_msg += f" ({context})"
            logger.error(f"{error_msg}: {e}")
            raise

    @staticmethod
    def validate_list(
        model: type[T],
        data_list: list[dict[str, Any]],
        context: str = "",
        source: Literal["system", "user", "api"] = "system",
    ) -> list[T]:
        """Validate a list of data against a Pydantic model.

        Args:
            model: The Pydantic model class to validate against
            data_list: List of data to validate
            context: Context string for error logging
            source: Source of the data - "system"/"api" or "user". Defaults to "system".

        Returns:
            list[Validated model instances]: List of validated model instances

        Raises:
            ValidationError: If any validation fails
        """
        validated = []
        for idx, data in enumerate(data_list):
            item_context = f"{context} [item {idx}]" if context else f"item {idx}"
            validated.append(
                ModelValidator.validate(model, data, item_context, source).model_dump()
            )
        return validated
