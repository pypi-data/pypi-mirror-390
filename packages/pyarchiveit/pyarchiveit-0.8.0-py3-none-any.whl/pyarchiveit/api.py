"""A module for interacting with the Archive-it API."""

import logging
from typing import Any

from httpx import Response
from pydantic import ValidationError

from pyarchiveit.model_validator import ModelValidator

from .exceptions import InvalidAuthError
from .httpx_client import HTTPXClient
from .models import SeedCreate, SeedKeys, SeedUpdate

logger = logging.getLogger(__name__)


class ArchiveItAPI:
    """A client for interacting with the Archive-it API."""

    def __init__(
        self,
        account_name: str,
        account_password: str,
        base_url: str = "https://partner.archive-it.org/api/",
        default_timeout: float | None = None,
    ) -> None:
        """Initialize the ArchiveItAPI client with authentication and base URL.

        Args:
            account_name (str): The account name for authentication.
            account_password (str): The account password for authentication.
            base_url (str): The base URL for the API endpoints. Defaults to Archive-it API base URL.
            default_timeout (float | None): Default timeout in seconds. Defaults to None. Use None for no timeout.

        """
        # validate authentication upon initialization
        self.SUCCESS_STATUS_CODES = range(200, 300)
        self.httpx_client = HTTPXClient(
            base_url=base_url,
            auth=(account_name, account_password),
            follow_redirects=True,
            timeout=default_timeout,
        )
        self._validate_auth()

    def __enter__(self) -> "ArchiveItAPI":
        """Enter context manager."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object | None,
    ) -> bool:
        """Exit context manager and close the HTTP client."""
        self.close()
        return False

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        self.httpx_client.close()

    def _request(self, method: str, endpoint: str, **kwargs: dict | bool) -> Response:
        """Make an HTTP request using the HTTPXClient. Mainly for internal/Debug use.

        Args:
            method (str): HTTP method (get, post, patch, delete, etc.)
            endpoint (str): API endpoint
            **kwargs (dict): Additional keyword arguments to pass to the request.

        Returns:
            httpx.Response: The HTTP response

        """
        return self.httpx_client.request(method, endpoint, **kwargs)

    def _validate_auth(self) -> None:
        """Validate authentication credentials."""
        response = self.httpx_client.get("auth")

        if response.status_code in {401, 403}:
            msg = "Invalid authentication credentials."
            raise InvalidAuthError(msg)

        if response.json().get("id") is None:
            msg = "Authentication failed."
            raise InvalidAuthError(msg)

        logger.info("Authentication credentials are valid.")

    def get_seed_by_id(
        self,
        seed_id: str | int,
    ) -> dict:
        """Get a seed by its ID.

        Args:
            seed_id (str | int): The ID of the seed to retrieve.

        Returns:
            dict: The validated seed data returned by the API.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
            httpx.TimeoutException: If the request times out.
            ValidationError: If the API returns invalid seed data.

        """
        logger.info(f"Fetching seed ID: {seed_id}")

        response = self.httpx_client.get(f"seed/{seed_id}")

        seed_data = response.json()

        return ModelValidator.validate(
            SeedKeys, seed_data, f"seed {seed_id}"
        ).model_dump()

    def get_seed_list(
        self,
        collection_id: str | int | list[str | int],
        limit: int = -1,
        sort: str | None = None,
        pluck: str | None = None,
        format: str = "json",
        additional_query: dict | None = None,
    ) -> list:
        r"""Get seeds for a given collection ID or list of collection IDs.

        Args:
            collection_id (str | int | list[str | int]): Collection ID or list of Collection IDs.
            limit (int): Maximum number of seeds to retrieve per collection. Defaults to -1 (no limit).
            sort (str | None): Sort order based on the result. Negative values (-) indicate ascending order. Defaults to None.<br><br>See the available fields in the API documentation (Data Models > Seed).<br><br>Example values: "id", "-id", "last_updated_date", "-last_updated_date".
            pluck (str | None): Specific field to extract from each seed object (e.g. "url", "id" ). Defaults to None (returns full seed objects).
            format (str): The format of the response (json or xml). Defaults to "json".
            additional_query (dict): Additional query parameters to include in the request.<br><br> <value> Can either be a string or list. A list means to query for multiple values for that parameter (OR statement).<br><br>Format: {"param_name": <value>} e.g. {"last_updated_by": "PersonA"} or {"last_updated_by": ["PersonA", "PersonB"]}.

        Returns:
            list[SeedKeys] | list: If pluck is None, returns list of validated seed objects. If pluck is specified, returns list of the plucked field values.

        Raises:
            httpx.HTTPStatusError: If the API request fails.
            httpx.TimeoutException: If the request times out.
            ValidationError: If the API returns invalid seed data.
            ValueError: If the `sort` parameter is invalid.

        """
        # Pydantic validate sort parameter is a valid field
        if sort:
            sort_field = sort.lstrip("-")
            if sort_field not in SeedKeys.model_fields:
                msg = f"Invalid sort field: {sort_field}. Must be one of: {list(SeedKeys.model_fields.keys())}"
                logger.error(msg)
                raise ValueError(msg)

        # Validate pluck parameter is a valid field
        if pluck and pluck not in SeedKeys.model_fields:
            msg = f"Invalid pluck field: {pluck}. Must be one of: {list(SeedKeys.model_fields.keys())}"
            logger.error(msg)
            raise ValueError(msg)

        logger.info(f"Fetching seeds for collection ID(s): {str(collection_id)}")

        # Handle multiple collection IDs
        collection_id_dict = {}
        if isinstance(collection_id, list):
            collection_ids_str = ",".join(str(cid) for cid in collection_id)
            collection_id = collection_ids_str
            collection_id_dict = {"collection__in": collection_ids_str}
        else:
            collection_id_dict = {"collection": str(collection_id)}

        # Build params dict, only including non-None optional parameters
        params = {
            **collection_id_dict,
            "limit": limit,
            "format": format,
            **(sort and {"sort": sort} or {}),
            **(pluck and {"pluck": pluck} or {}),
            **(additional_query or {}),
        }

        response = self.httpx_client.get("seed", params=params)

        data = response.json()

        if pluck:
            return data  # Return list of plucked field values

        return ModelValidator.validate_list(SeedKeys, data, "all seeds", source="api")

    def get_seed_with_metadata(
        self,
        metadata_field: str | None = None,
        metadata_value: str | None = None,
        limit: int = -1,
        pluck: str | None = None,
    ) -> list:
        """Get seeds that match a specific metadata field and value.

        Args:
            metadata_field (str | None): The metadata field to search (e.g., "Title", "Author").
            metadata_value (str | None): The value to search for within the specified metadata field.
            limit (int): Maximum number of seeds to retrieve. Defaults to -1 (no limit).
            pluck (str | None): Specific field to extract from each seed object (e.g. "collection"). Defaults to None (returns full seed objects).

        """
        logger.info(f"Getting seeds with metadata: {metadata_field} = {metadata_value}")

        # First, search for seed IDs matching the metadata
        seed_ids = self.search_seed_metadata(
            metadata_field=metadata_field,
            metadata_value=metadata_value,
            limit=limit,
            pluck="seed",
        )

        # Next, make the request to get the seed details
        return [self.get_seed_by_id(seed_id) for seed_id in seed_ids]

    def search_seed_metadata(
        self,
        metadata_field: str | list | None = None,
        metadata_value: str | list | None = None,
        limit: int = -1,
        pluck: str | None = None,
    ) -> list:
        """Search seeds by metadata field and value.

        Note:
            It is not necessary to search with the metadata_field to search for the value. If you just want to look up a value across all metadata fields, simply pass the value to metadata_value and leave metadata_field as `None`.

        Args:
            metadata_field (str | list | None): The metadata field to search (e.g., "Title", "Author"). If a list is provided, searches within any of the fields.
            metadata_value (str | list | None): The value to search for within the specified metadata field. If a list is provided, searches for any of the values.
            limit (int): Maximum number of seeds to retrieve. Defaults to -1 (no limit).
            pluck (str | None): Specific field to extract from each seed object (e.g. "seed", "name_control"). Defaults to None (returns full seed objects).

        Returns:
            list: A list of seeds matching the search criteria.
        """
        logger.info(f"Searching seeds by metadata: {metadata_field} = {metadata_value}")

        # TODO: add model for the seed metadata search response
        if pluck and pluck not in {"seed", "name_control", "id", "name", "value"}:
            msg = f"Invalid pluck field: {pluck}. Must be one of: {list(SeedKeys.model_fields.keys())}"
            logger.error(msg)
            raise ValueError(msg)

        # Build params dict, only including non-None optional parameters
        params: dict[str, Any] = {"limit": limit}
        if metadata_field:
            params["name"] = metadata_field
        if metadata_value:
            params["value"] = metadata_value
        if pluck:
            params["pluck"] = pluck

        response = self.httpx_client.get("seed_metadata", params=params)

        seeds = response.json()
        logger.info(
            f"Found {len(seeds)} seeds matching metadata: {metadata_field} = {metadata_value}"
        )

        # TODO: Validate seed data
        return seeds

    def update_seed_metadata(
        self,
        seed_id: str | int,
        metadata: dict,
    ) -> dict:
        """Update metadata for a specific seed.

        Args:
            seed_id (str | int): The ID of the seed to update.
            metadata (dict): The metadata to update for the seed.

        Raises:
            ValidationError: If the metadata structure is invalid.

        """
        logger.info(f"Updating metadata for seed ID: {seed_id}")

        # Validate metadata structure using Pydantic
        try:
            seed_update = SeedUpdate(metadata=metadata)
        except ValidationError as e:
            logger.error(f"Invalid metadata structure for seed ID {seed_id}: {e}")
            raise

        response = self.httpx_client.patch(
            f"seed/{seed_id}",
            data=seed_update.model_dump(exclude_none=True, mode="python"),
        )

        return response.json()

    def create_seed(
        self,
        url: str,
        collection_id: str | int,
        crawl_definition_id: str | int,
        other_params: dict | None = None,
        metadata: dict | None = None,
    ) -> dict:
        """Create a new seed in a specified collection with given crawl definition.

        Args:
            url (str): The URL of the seed to create.
            collection_id (str | int): The ID of the collection to add the seed to.
            crawl_definition_id (str | int): The ID of the crawl definition to associate with the seed.
            other_params (dict | None): Additional parameters for the seed creation.
            metadata (dict | None): Metadata to set for the seed after creation.

        Returns:
            dict: The validated created seed data returned by the API.

        Raises:
            ValidationError: If the input data or metadata structure is invalid.

        """
        logger.info(f"Creating new seed in collection ID: {collection_id}")

        # Handle metadata from other_params
        if other_params and "metadata" in other_params:
            other_params_metadata = other_params.pop("metadata")
            # Combine with metadata parameter if provided
            if metadata:
                metadata.update(other_params_metadata)
            else:
                metadata = other_params_metadata

        # Validate input using Pydantic
        try:
            seed_create = SeedCreate(
                url=url,
                collection=collection_id,
                crawl_definition=crawl_definition_id,
            )
        except ValidationError as e:
            logger.error(
                f"Invalid seed creation data for collection ID {collection_id}: {e}"
            )
            raise

        # Convert to dict for API request
        payload: dict = seed_create.model_dump(
            exclude_none=True, by_alias=True, mode="python"
        )

        logger.debug(f"Seed creation payload: {payload}")

        # Add any additional params
        if other_params:
            payload.update(other_params)

        response = self.httpx_client.post(
            "seed",
            data=payload,
        )
        seed_data = response.json()
        logger.info(f"Successfully created seed in collection ID: {collection_id}")

        # If metadata is provided, update it after seed creation
        if metadata:
            seed_id = seed_data.get("id")
            if seed_id:
                logger.info(f"Updating metadata for newly created seed ID: {seed_id}")
                self.update_seed_metadata(seed_id=seed_id, metadata=metadata)
                # Refresh seed_data to include updated metadata
                seed_data["metadata"] = metadata
            else:
                logger.warning(
                    "Seed created but no ID returned, cannot update metadata"
                )

        return ModelValidator.validate(
            SeedKeys, seed_data, f"created seed in collection {collection_id}"
        ).model_dump()

    def delete_seed(
        self,
        seed_id: str | int,
    ) -> dict:
        """Delete a seed by its ID.

        Args:
            seed_id (str | int): The ID of the seed to delete.

        Returns:
            dict: The validated seed data from the API after deletion. The 'deleted' flag should be True.

        Raises:
            ValidationError: If the API returns invalid seed data.

        """
        logger.info(f"Deleting seed ID: {seed_id}")

        response = self.httpx_client.patch(
            f"seed/{seed_id}",
            data={"deleted": True},
        )  # The API uses PATCH 'deleted' flag to delete seeds

        logger.info(f"Successfully deleted seed ID: {seed_id}")

        seed_data = response.json()

        # Validate and return the response
        return ModelValidator.validate(
            SeedKeys, seed_data, f"deleted seed {seed_id}"
        ).model_dump()
