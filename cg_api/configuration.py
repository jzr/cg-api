import configparser
import os
import pathlib
from dataclasses import dataclass

ENV_NAMES = {
    "BASE_URL": "CLOUDGUARD_URL",
    "KEY": "CLOUDGUARD_ID",
    "SECRET": "CLOUDGUARD_SECRET",
    "PROFILE": "CLOUDGUARD_PROFILE",
}

DEFAULT_CONFIG_FILE = "~/.cloudguard/credentials"


@dataclass
class Config:
    BASE_URL: str
    KEY: str
    SECRET: str


class ConfigProvider:
    def load(self) -> Config:
        return True


class EnvironmentConfigProvider(ConfigProvider):
    def __init__(self):
        pass

    def load(self) -> Config:
        base_url = os.environ.get(ENV_NAMES["BASE_URL"])
        key = os.environ.get(ENV_NAMES["KEY"])
        secret = os.environ.get(ENV_NAMES["SECRET"])
        if base_url and key and secret:
            return Config(base_url, key, secret)


class FileConfigProvider:
    def __init__(self, config_file: str = None, profile_name: str = None) -> None:
        if config_file:
            self.config_file = config_file
        else:
            self.config_file = (
                os.environ.get("CLOUDGUARD_SHARED_CREDENTIALS_FILE")
                or DEFAULT_CONFIG_FILE
            )

        self.config_parser = configparser.ConfigParser()

        if profile_name:
            self.profile_name = profile_name
        else:
            self.profile_name = os.environ.get(ENV_NAMES["PROFILE"], "default")

    def load(self) -> Config:
        try:
            self.config_parser.read(pathlib.Path(self.config_file).expanduser())
        except FileNotFoundError:
            return None

        if not self.config_parser.has_section(self.profile_name):
            raise configparser.NoSectionError(self.profile_name)

        base_url = self.config_parser[self.profile_name].get(
            ENV_NAMES["BASE_URL"]
        ) or self.config_parser["default"].get(ENV_NAMES["BASE_URL"])

        key = self.config_parser[self.profile_name][ENV_NAMES["KEY"]]
        secret = self.config_parser[self.profile_name][ENV_NAMES["SECRET"]]

        if base_url and key and secret:
            return Config(base_url, key, secret)


class RandomConfigProvider(ConfigProvider):
    def __init__(self):
        import secrets
        import uuid
        import random
        import string

        self.base_url = f"https://{''.join(random.choice(string.ascii_lowercase) for _ in range(12)) }.{random.choice(['com','net','io'])}/v{random.randint(0,1337)}"
        self.key = str(uuid.uuid4())
        self.secret = "".join(
            secrets.choice(string.ascii_lowercase + string.digits) for _ in range(24)
        )

    def load(self) -> Config:
        return Config(self.base_url, self.key, self.secret)


DEFAULT_PROVIDERS = [
    EnvironmentConfigProvider,
    FileConfigProvider,
]


def load_default(providers: Config = DEFAULT_PROVIDERS):
    for provider in providers:
        config = provider().load()
        if config:
            return config

    raise RuntimeError(
        f"Failed to load configuration. Tried: {', '.join(p.__name__ for p in providers)}"
    )


def list_profiles(config_file: str = None):
    if not config_file:
        config_file = DEFAULT_CONFIG_FILE
    config = configparser.ConfigParser()
    config.read(pathlib.Path(config_file).expanduser())

    return config.sections()
