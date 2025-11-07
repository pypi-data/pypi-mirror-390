import abc
import json
import os
from rick.base import ShallowContainer
from typing import Any, List
from abc import abstractmethod, ABC
from pathlib import Path


class WrapType(ABC):
    """
    Base encapsulation class
    """

    @abc.abstractmethod
    def unwrap(self):
        pass


class StrOrFile(WrapType):
    """
    Encapsulation class for Strings to be processed either as values or as path to files holding values

    The value is unrwapped as a string by default; however it will be unwrapped as file content if the string value
    starts with '/' or './'
    """

    def __init__(self, value: str, silent=False):
        """
        Constructor
        :param value: value to wrap
        :param silent: if True, no exception is raised if file doesn't exist, and value is returned instead
        """
        self.value = value
        self.silent = silent

    def unwrap(self):
        """
        Unwraps value
        If value starts with '/' or value starts with './', assume it is a file and try to read it;
        If file doesnt exist, raise ValueError() to make sure error is noted, unless self.silent==True
        :return: str
        """
        if self.value is None:
            return ""

        if self.value.startswith(os.sep) or self.value.startswith(os.curdir + os.sep):
            path = Path(self.value)
            if path.exists() and path.is_file():
                try:
                    with open(path) as f:
                        return f.read().strip()
                except Exception as e:
                    raise ValueError(
                        "StrOrFile: error reading file '{}' - {}".format(
                            self.value, str(e)
                        )
                    )
            else:
                if self.silent:
                    # return value as-is, raise no exception
                    return self.value
                raise ValueError("StrOrFile: invalid file path '{}'".format(self.value))
        return self.value


class EnvironmentConfig:
    """
    Base class for environment-based config

    Config attributes must be named uppercase; These attribute names will be translated to lowercase
    on the ShallowContainer; The uppercase names are used to override values from existing environment variables

    Example:
        EXISTING OS ENV VARS: [DB_NAME="some_db", DB_HOST="abc"]

        class MyConfig(EnvironmentConfig):
            DB_NAME = 'mydb'
            DB_HOST = 'localhost'
            DB_USERNAME = 'username'
            DB_PASSWORD = 'password'

        cfg = MyConfig().build()
        assert cfg['db_name'] == 'some_db'
        assert cfg['db_host'] == 'abc'
        assert cfg['db_username'] == 'abc'
    """

    list_separator = ","

    def build(self, prefix="") -> ShallowContainer:
        """
        Assemble a final ShallowContainer based on the env vars
        Note: The env vars also override the object values
        :param prefix: optional prefix name for env vars
        :return: ShallowContainer
        """
        data = {}
        for name in dir(self):
            if name.isupper():
                value = getattr(self, name)
                if not callable(value):
                    value = self._parse_value(prefix + name, value)
                    setattr(self, name, value)
                    if isinstance(value, WrapType):
                        data[name.lower()] = value.unwrap()
                    else:
                        data[name.lower()] = value

        # run optional validators
        self._run_validators(data)

        return ShallowContainer(data)

    def _run_validators(self, data: dict):
        """
        Call optional validator functions

        A validator function must have a name starting with validate_ and should raise exceptions if validation fails

        :param data:
        :return:
        """
        for attr_name in dir(self):
            if attr_name.startswith("validate_"):
                method = getattr(self, attr_name)
                if callable(method):
                    method(data)

    def _parse_value(self, env_var_name, existing_value) -> Any:
        """
        Simple mapper to extract environment variables based on type

        :param env_var_name: env var to process
        :param existing_value: existing default value
        :return: overridden value of correct existing_value type, if env var exists; existing_value otherwise
        """
        value = os.environ.get(env_var_name)
        if value is None:
            return existing_value

        # if default value of attribute is none, always assume string
        if existing_value is None:
            return value

        mapper = getattr(self, "_{}_conv".format(type(existing_value).__name__))
        if not mapper:
            raise ValueError(
                "Invalid data type detected when parsing environment variable '{}'".format(
                    env_var_name
                )
            )
        return mapper(value)

    def _str_conv(self, v) -> str:
        """
        String mapper
        :param v:
        :return: str
        """
        return str(v)

    def _int_conv(self, v) -> int:
        """
        Int mapper
        :param v:
        :return: int
        """
        return int(v)

    def _list_conv(self, v) -> List:
        """
        List mapper
        :param v: a string containing multiple string values, separated by self.list_separator
        :return: List
        """
        if not type(v) is str:
            raise ValueError(
                "Invalid data type to extract list: expecting str, got '{}'".format(
                    type(v).__name__
                )
            )
        return str(v).split(self.list_separator)

    def _dict_conv(self, v) -> dict:
        """
        Dict mapper
        :param v: a json string containing an object (dict)
        :return: dict
        """
        if not type(v) is str:
            raise ValueError(
                "Invalid data type to extract dict: expecting str, got '{}'".format(
                    type(v).__name__
                )
            )
        try:
            return json.loads(v)
        except Exception as e:
            raise ValueError("Error when parsing JSON: {}".format(e))

    def _bool_conv(self, v) -> bool:
        """
        Bool converter
        :param v:
        :return: bool
        """
        return v in [1, "1", "true", "TRUE", "True", "T", "t"]

    def _StrOrFile_conv(self, v) -> StrOrFile:
        """
        StrOrFile mapper
        :param v: a string
        :return: StrOrFile
        """
        if not type(v) is str:
            raise ValueError(
                "StrOrFile requires a str to be wrapped; found '{}'  instead".format(
                    type(v).__name__
                )
            )
        return StrOrFile(v)
