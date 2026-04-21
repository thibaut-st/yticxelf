import json
from pathlib import Path

from models import AssetModel


def get_sample_data(file_name: str) -> list[AssetModel]:
    """
    Get sample data from a JSON file as a list of AssetModel objects.

    :param file_name: The name of the JSON file.
    :return: A list of AssetModel objects extracted from the JSON file.
    """
    sample_path = Path(__file__).resolve().parent.parent / "data" / file_name
    sample_assets = json.loads(sample_path.read_text(encoding="utf-8"))
    return [AssetModel(**asset_data) for asset_data in sample_assets]
