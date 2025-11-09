"""Export to various formats."""

import logging
from pathlib import Path

import tablib

logger = logging.getLogger(__name__)


def _parse_metadata_to_list(metadata_dict: dict) -> list[str]:
    """Parse metadata dictionary to a list representation.

    Each key value is like this:
    key: [{"subkey1": "value1", "subkey2": "value2"}, {...}]

    Args:
        metadata_dict (dict): The metadata dictionary to parse.

    Returns:
        list[str]: The string representation of the metadata. Format: (key - id - value)
    """
    metadata_list = []
    for key, value in metadata_dict.items():
        for item in value:
            metadata_list.append(
                f"({key} - {item.get('id', '')} - {item.get('value', '')})"
            )
    return metadata_list


def _parse_seed_group_to_list(seed_group_dict: list[dict]) -> list[str]:
    """Parse seed group dictionary to a list representation.

    Each key value is like this:
    seed_groups: [{"account": "account1", "collections": ["col1", "col2"], "id": "id1", "name": "name1", "visibility": "public"}, {...}]

    Args:
        seed_group_dict (dict): The seed group dictionary to parse.

    Returns:
        list[str]: The string representation of the seed group. Format: (account - collections - id - name - visibility)
    """
    seed_group_list = []
    for item in seed_group_dict:
        # Turn collections list into a comma-separated string first
        collections = ", ".join(str(c) for c in item.get("collections", []))

        seed_group_list.append(
            f"({item.get('account', '')} - {collections} - {item.get('id', '')} - {item.get('name', '')} - {item.get('visibility', '')})"
        )
    return seed_group_list


def export_seed_to_spreadsheet(
    data: list[dict] | dict,
    file_dir: Path | str,
    file_name: str,
    file_format: str = "xlsx",
) -> None:
    """Export seed data to a spreadsheet file.

    Note:
        Can only use with seed data (returns from e.g., api.get_seeds(), api.get_seed_list(), etc.).

    Example:
        ``` Python
        # Get seed data from Archive-It API
        seed_data = api.get_seeds(collection_id=12345)

        # Export seed data to XLSX file
        export_seed_to_spreadsheet(
            data=seed_data,
            file_dir="output",
            file_name="seeds.xlsx",
            file_format="xlsx"
        )
        ```

    Args:
        data (list of dict): The data to export.
        file_dir (Path | str): The directory to save the output file.
        file_name (Path | str): The name of the output file.
        file_format (str): The format of the output file ('xlsx' or 'csv').
    """
    # Turn single dict into a list of one dict
    if isinstance(data, dict):
        data = [data]
    dataset = tablib.Dataset()

    # Create output path with correct suffix
    output_path = (
        Path(file_dir).joinpath(file_name).with_suffix(f".{file_format.lower()}")
    )

    # Check if the path exists, create if not
    if output_path.exists():
        logger.warning(
            f"File already exists: {str(Path(file_dir).joinpath(file_name))}. It will be overwritten."
        )
    else:
        Path(file_dir).mkdir(parents=True, exist_ok=True)

    if data:
        headers = data[0].keys()
        dataset.headers = headers
        for row in data:
            # Parse metadata field if it exists
            if row.get("metadata") and row.get("metadata") != {}:
                row["metadata"] = " | ".join(_parse_metadata_to_list(row["metadata"]))
            # Parse seed_groups field if it exists
            if row.get("seed_groups") and row.get("seed_groups") != []:
                row["seed_groups"] = " | ".join(
                    _parse_seed_group_to_list(row["seed_groups"])
                )
            dataset.append([row[h] for h in headers])

    # Binary formats (xlsx) need 'wb' mode, text formats (csv) need 'w' mode
    mode = "wb" if file_format in {"xlsx", "xls"} else "w"

    with output_path.open(mode) as f:
        f.write(dataset.export(file_format))
