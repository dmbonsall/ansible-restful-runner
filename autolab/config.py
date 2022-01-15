from functools import lru_cache
import json
import logging
import logging.config
import os
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseSettings


_DEFAULT_CONFIG_PATH = "/etc/autolab.json"


@lru_cache
def get_config_file_name() -> Path:
    path_str = os.environ.get("AUTOLAB_CONFIG", _DEFAULT_CONFIG_PATH)
    return Path(path_str)


def json_config_settings_source(settings: BaseSettings) -> Dict[str, Any]:
    encoding = settings.__config__.env_file_encoding
    return json.loads(Path(get_config_file_name()).read_text(encoding))


class ApplicationSettings(BaseSettings):
    create_vm_private_data_dir: str = "./ansible/pve-one-touch"
    config_backup_private_data_dir: str = "./ansible/config-backup"
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


@lru_cache
def get_app_settings():
    return ApplicationSettings()


# Copied from uvicorn
TRACE_LOG_LEVEL: int = 5
LOGGING_CONFIG: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(module)s %(message)s",
            "use_colors": None,
        }
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        }
    },
    "loggers": {
        "autolab": {"handlers": ["default"], "level": "DEBUG"},
    }
}


logging.addLevelName(TRACE_LOG_LEVEL, "TRACE")
logging.config.dictConfig(LOGGING_CONFIG)


@lru_cache
def get_logger():
    return logging.getLogger("autolab")
