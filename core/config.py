from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict

type AlgorithmType = Literal["bf", "scip"]


class Settings(BaseSettings):
    """Application settings, load the environment variables."""

    optimization_algorithm: AlgorithmType

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()  # type: ignore[call-arg]
