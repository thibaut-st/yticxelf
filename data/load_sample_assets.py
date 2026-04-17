import json
import sys
from pathlib import Path

from data.db import DATABASE_URL, Base, make_engine, make_session_factory
from models.asset import AssetModel

SAMPLE_ASSETS_PATH = Path(__file__).resolve().parent / "sample_assets.json"


def recreate_db_with_sample_assets() -> int:
    """Reset the SQLite database and load the sample asset JSON file."""
    # Delete the existing database file if it exists.
    database_path = Path(DATABASE_URL.removeprefix("sqlite:///"))
    if database_path.exists():
        database_path.unlink()

    # Create a new database
    engine = make_engine(DATABASE_URL)
    session_factory = make_session_factory(engine)

    # Load the sample asset JSON file
    sample_assets = json.loads(SAMPLE_ASSETS_PATH.read_text(encoding="utf-8"))

    # Create the database tables and insert sample assets
    try:
        Base.metadata.create_all(engine)

        with session_factory() as session:
            session.add_all(AssetModel(**asset_data) for asset_data in sample_assets)
            session.commit()
    finally:
        engine.dispose()

    return len(sample_assets)


def main() -> None:
    """Load the JSON sample asset dataset into SQLite."""
    loaded_count = recreate_db_with_sample_assets()
    sys.stdout.write(f"Loaded {loaded_count} sample assets into {DATABASE_URL}.\n")


if __name__ == "__main__":
    main()
