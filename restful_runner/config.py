from functools import lru_cache
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseSettings


_DEFAULT_CONFIG_PATH = "restful_runner.json"


@lru_cache
def get_config_file_path() -> Path:
    path_str = os.environ.get("RESTFUL_RUNNER_CONFIG", _DEFAULT_CONFIG_PATH)
    return Path(path_str)


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    config_path = get_config_file_path()
    if config_path.is_file():
        return json.loads(config_path.read_text(encoding))

    return {}


class ApplicationSettings(BaseSettings):
    db_url: str = "sqlite:////ansible/restful_runner.db"
    max_executor_threads: int = 1
    private_data_dir: str = "/ansible"
    project_dir: Optional[str] = None
    artifact_dir: Optional[str] = None
    ansible_quiet: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

        @classmethod
        def customise_sources(
            cls,
            init_settings,
            env_settings,
            file_secret_settings,
        ):
            return (
                init_settings,
                env_settings,
                json_config_settings_source,
                file_secret_settings,
            )


_settings = ApplicationSettings()


def get_app_settings() -> ApplicationSettings:
    return _settings
