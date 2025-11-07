import os
import pytest
from rick.resource.config import EnvironmentConfig, StrOrFile
from rick.base import ShallowContainer
from pathlib import Path


class Config(EnvironmentConfig):
    DB_HOST = "localhost"
    DB_USER = StrOrFile("username")
    DB_PASSWORD = StrOrFile("password")


fixture_config_wrap = [
    [  # absolute path
        Config,
        {
            "DB_USER": "myuser",
            "DB_PASSWORD": str(
                Path(__file__).parent.resolve() / Path("test_password.txt")
            ),
        },
        {"db_host": "localhost", "db_user": "myuser", "db_password": "abc123"},
    ],
    [  # relative path
        Config,
        {
            "DB_USER": "myuser",
            "DB_PASSWORD": "./tests/resource/config/test_password.txt",
        },
        {"db_host": "localhost", "db_user": "myuser", "db_password": "abc123"},
    ],
]


@pytest.mark.parametrize("cls, env_vars, expected_result", fixture_config_wrap)
def test_EnvConfig_wrap(cls, env_vars: dict, expected_result: dict):
    obj = cls()

    # now set env variables
    for name, value in env_vars.items():
        os.environ[name] = str(value)

    # build cfg with overriden values
    cfg = obj.build()
    # verify overriden values match expected values
    for name, value in env_vars.items():
        value = cfg.get(name.lower())
        if isinstance(value, ShallowContainer):
            value = value.asdict()
        assert value == expected_result[name.lower()]
