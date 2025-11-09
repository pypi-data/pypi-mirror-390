"""Configuration and settings management"""

import functools
import json
import os
import pathlib

import yaml
from pydantic import FilePath
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

from oocli.data import DataStore, Environment

CONFIG_PATH = pathlib.Path.home() / ".config" / "o-o"
CONFIG_FILE = CONFIG_PATH / "settings.yaml"

DEFAULT_HOST = "https://o-o.tools"


class Settings(BaseSettings):
    """o-o settings

    Settings are loaded from both an `.ooconfig` file in the current working
    directory and from `$HOME/.config/o-o/settings.yaml`. Preference is given
    to settings in `.ooconfig`.
    """

    host: str
    sshkey: FilePath
    project: str
    token: str
    datastores: dict[str, DataStore]
    environments: dict[str, Environment]
    sourcecode: bool = False

    model_config = SettingsConfigDict(yaml_file=[CONFIG_FILE, ".ooconfig"])

    @property
    def apiurl(self):
        return f"{self.host}/api/v0"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (YamlConfigSettingsSource(settings_cls),)


@functools.cache
def settings() -> Settings:
    """Cached interface to settings"""
    return Settings()


def get_setting(setting: str, value: str | None):
    """Get a configured setting, or if value is None, return the default"""
    configurations = getattr(settings(), setting)
    if value is None:
        if len(configurations) == 1:
            return next(iter(configurations.values()))
        try:
            return next(e for e in configurations.values() if e.default)
        except StopIteration:
            raise RuntimeError(
                f"no default configured, must select provide one of {list(configurations.keys())}"
            ) from None
    if value not in configurations:
        raise RuntimeError(f"'{value}' is not one of {list(configurations.keys())}")
    return configurations[value]


def write(**kwargs):
    """Write settings to config file location"""
    if CONFIG_FILE.exists():
        kwargs = yaml.safe_load(CONFIG_FILE.read_text()) | kwargs
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(yaml.dump(kwargs))


@functools.cache
def gcp_credentials():
    """Retreive Google Cloud credentials"""
    credentials_file = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", None)
    if credentials_file is None:
        raise RuntimeError(
            "GOOGLE_APPLICATION_CREDENTIALS environment variable not set"
        )
    credentials_file = pathlib.Path(credentials_file)
    if not credentials_file.exists():
        raise RuntimeError(
            f"Google application credentials file not found ({credentials_file.as_posix()}). "
        )
    return json.loads(credentials_file.read_text())


@functools.cache
def scaleway_credentials():
    """Retreive Scaleway credentials"""
    required_variables = [
        "SCW_ACCESS_KEY",
        "SCW_SECRET_KEY",
        "SCW_DEFAULT_ORGANIZATION_ID",
    ]
    missing_variables = [v for v in required_variables if v not in os.environ]
    if missing_variables:
        raise RuntimeError(
            f"Scaleway environment variables not set: {', '.join(missing_variables)}"
        )

    return {v: os.environ[v] for v in required_variables}
