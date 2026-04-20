from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

type AlgorithmType = Literal["bf", "dp", "scip"]

BASE_DIR = Path(__file__).resolve().parent
DOT_ENV_PATH = BASE_DIR.parent / ".env"


class Settings(BaseSettings):
    """Application settings, load the environment variables."""

    optimization_algorithm: AlgorithmType

    model_config = SettingsConfigDict(env_file=DOT_ENV_PATH)


settings = Settings()  # type: ignore[call-arg]
