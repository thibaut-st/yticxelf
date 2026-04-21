import json
import sys
from pathlib import Path

from core.config import settings
from data.db import DATABASE_PATH, DATABASE_URL, Base, make_engine, make_session_factory
from models import AssetModel

SAMPLE_ASSETS_PATH = Path(__file__).resolve().parent / settings.sample_assets_file


def recreate_db_with_sample_assets() -> int:
    """Reset the SQLite database and load the sample asset JSON file."""
    # Delete the existing database file if it exists.
    DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()

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
