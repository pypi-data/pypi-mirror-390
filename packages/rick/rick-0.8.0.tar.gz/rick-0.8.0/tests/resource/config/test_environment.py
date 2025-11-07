import os
import pytest
from rick.resource.config import EnvironmentConfig
from rick.base import ShallowContainer


class ConfigTest1(EnvironmentConfig):
    OPTION_1 = None
    OPTION_2 = "x"
    OPTION_3 = "xyz"


class ConfigTest2(EnvironmentConfig):
    FOO_LIST = []
    FOO_INT = 1
    FOO_STR = None
    FOO_DICT = {}


fixture_configtest_prefix = [
    (ConfigTest1, {"PREFIX_OPTION_1": "abc", "PREFIX_OPTION_2": "def"})
]

fixtures = [
    [  # simple override
        ConfigTest1,
        {"OPTION_1": "abc", "OPTION_2": "def"},
        {"option_1": "abc", "option_2": "def", "option_3": "xyz"},
        "",  # no prefix
    ],
    [  # simple override
        ConfigTest1,
        {"PREFIX_OPTION_1": "abc", "PREFIX_OPTION_2": "def"},
        {"option_1": "abc", "option_2": "def", "option_3": "xyz"},
        "PREFIX_",  # no prefix
    ],
    [  # multiple types
        ConfigTest2,
        {  # env vars
            "FOO_LIST": "abc,def",
            "FOO_INT": "5",
            "FOO_STR": "joe",
            "FOO_DICT": '{"key":"value"}',
        },  # expected result
        {
            "foo_list": ["abc", "def"],
            "foo_int": 5,
            "foo_str": "joe",
            "foo_dict": {"key": "value"},
        },
        "",  # no prefix
    ],
]


@pytest.mark.parametrize("cls,env_vars, expected_result, prefix", fixtures)
def test_EnvConfig_types(cls, env_vars: dict, expected_result: dict, prefix: str):
    obj = cls()

    # first, check that build() processes correctly without any set env variables
    cfg = obj.build(prefix)
    for name in dir(obj):
        if name.isupper():
            value = cfg.get(name.lower())
            if isinstance(value, ShallowContainer):
                # unrap dict from ShallowContainer
                value = value.asdict()
            assert value == getattr(obj, name)

    # now set env variables
    for name, value in env_vars.items():
        os.environ[name] = str(value)

    # re-build cfg with overriden values
    cfg = obj.build()
    # verify overriden values match expected values
    for name in expected_result.keys():
        value = cfg.get(name)
        if isinstance(value, ShallowContainer):
            value = value.asdict()
        assert value == expected_result[name]


# Test classes for validator functionality
class ConfigWithValidators(EnvironmentConfig):
    """Test config class with validators"""

    DB_HOST = "localhost"
    DB_PORT = 5432
    API_KEY = None
    MAX_CONNECTIONS = 10

    def validate_database_config(self, data: dict):
        """Validate database configuration"""
        if data.get("db_host") == "invalid_host":
            raise ValueError("Invalid database host")

        if data.get("db_port", 0) <= 0:
            raise ValueError("Database port must be positive")

    def validate_api_key(self, data: dict):
        """Validate API key is present and valid"""
        api_key = data.get("api_key")
        if api_key is None or len(api_key) < 10:
            raise ValueError("API key must be at least 10 characters long")

    def validate_max_connections(self, data: dict):
        """Validate max connections is reasonable"""
        max_conn = data.get("max_connections", 0)
        if max_conn > 100:
            raise ValueError("Max connections cannot exceed 100")


class ConfigWithMultipleValidators(EnvironmentConfig):
    """Test config with multiple validators"""

    USERNAME = "admin"
    PASSWORD = "secret"
    ROLE = "user"

    def validate_credentials(self, data: dict):
        """Validate username and password"""
        username = data.get("username", "")
        password = data.get("password", "")

        if len(username) < 3:
            raise ValueError("Username must be at least 3 characters")
        if len(password) < 6:
            raise ValueError("Password must be at least 6 characters")

    def validate_role(self, data: dict):
        """Validate role is allowed"""
        role = data.get("role", "")
        allowed_roles = ["admin", "user", "guest"]
        if role not in allowed_roles:
            raise ValueError(f"Role must be one of: {', '.join(allowed_roles)}")


class ConfigWithNoValidators(EnvironmentConfig):
    """Test config without validators"""

    SIMPLE_VALUE = "test"
    ANOTHER_VALUE = 42


class ConfigWithNonCallableValidator(EnvironmentConfig):
    """Test config with non-callable validate_ attribute"""

    TEST_VALUE = "test"
    validate_not_callable = "this is not a function"


# Test fixtures for validator functionality
validator_fixtures = [
    # Valid configuration - should pass all validators
    [
        ConfigWithValidators,
        {
            "DB_HOST": "prod-server",
            "DB_PORT": "3306",
            "API_KEY": "valid_api_key_123",
            "MAX_CONNECTIONS": "50",
        },
        {
            "db_host": "prod-server",
            "db_port": 3306,
            "api_key": "valid_api_key_123",
            "max_connections": 50,
        },
    ],
    # Multiple validators - all valid
    [
        ConfigWithMultipleValidators,
        {"USERNAME": "testuser", "PASSWORD": "secure_password", "ROLE": "admin"},
        {"username": "testuser", "password": "secure_password", "role": "admin"},
    ],
]

validator_error_fixtures = [
    # Invalid database host (but need valid API key to get to database validator)
    [
        ConfigWithValidators,
        {"DB_HOST": "invalid_host", "API_KEY": "valid_api_key_123"},
        ValueError,
        "Invalid database host",
    ],
    # Invalid database port (zero) (need valid API key)
    [
        ConfigWithValidators,
        {"DB_PORT": "0", "API_KEY": "valid_api_key_123"},
        ValueError,
        "Database port must be positive",
    ],
    # Invalid database port (negative) (need valid API key)
    [
        ConfigWithValidators,
        {"DB_PORT": "-1", "API_KEY": "valid_api_key_123"},
        ValueError,
        "Database port must be positive",
    ],
    # Short API key
    [
        ConfigWithValidators,
        {"API_KEY": "short"},
        ValueError,
        "API key must be at least 10 characters long",
    ],
    # Too many connections (need valid API key)
    [
        ConfigWithValidators,
        {"MAX_CONNECTIONS": "150", "API_KEY": "valid_api_key_123"},
        ValueError,
        "Max connections cannot exceed 100",
    ],
    # Short username
    [
        ConfigWithMultipleValidators,
        {"USERNAME": "ab"},
        ValueError,
        "Username must be at least 3 characters",
    ],
    # Short password
    [
        ConfigWithMultipleValidators,
        {"PASSWORD": "12345"},
        ValueError,
        "Password must be at least 6 characters",
    ],
    # Invalid role
    [
        ConfigWithMultipleValidators,
        {"ROLE": "superuser"},
        ValueError,
        "Role must be one of: admin, user, guest",
    ],
]


@pytest.mark.parametrize("cls,env_vars,expected_result", validator_fixtures)
def test_environment_config_validators_success(
    cls, env_vars: dict, expected_result: dict
):
    """Test that valid configurations pass all validators"""
    obj = cls()

    # Set environment variables
    for name, value in env_vars.items():
        os.environ[name] = str(value)

    try:
        # Build config - should not raise any exceptions
        cfg = obj.build()

        # Check that values match expected results
        for name, expected_value in expected_result.items():
            actual_value = cfg.get(name)
            assert actual_value == expected_value

    finally:
        # Clean up environment variables
        for name in env_vars.keys():
            if name in os.environ:
                del os.environ[name]


@pytest.mark.parametrize(
    "cls,env_vars,expected_exception,expected_message", validator_error_fixtures
)
def test_environment_config_validators_failure(
    cls, env_vars: dict, expected_exception, expected_message: str
):
    """Test that invalid configurations raise appropriate exceptions"""
    obj = cls()

    # Set environment variables
    for name, value in env_vars.items():
        os.environ[name] = str(value)

    try:
        # Build config - should raise expected exception
        with pytest.raises(expected_exception, match=expected_message):
            obj.build()

    finally:
        # Clean up environment variables
        for name in env_vars.keys():
            if name in os.environ:
                del os.environ[name]


def test_environment_config_no_validators():
    """Test that configs without validators work normally"""
    obj = ConfigWithNoValidators()

    # Should build successfully without any validators
    cfg = obj.build()

    assert cfg.get("simple_value") == "test"
    assert cfg.get("another_value") == 42


def test_environment_config_non_callable_validator():
    """Test that non-callable validate_ attributes are ignored"""
    obj = ConfigWithNonCallableValidator()

    # Should build successfully, ignoring non-callable validate_ attribute
    cfg = obj.build()

    assert cfg.get("test_value") == "test"


def test_environment_config_multiple_validators_all_pass():
    """Test multiple validators all passing"""
    obj = ConfigWithMultipleValidators()

    # Set valid values for all validators
    os.environ["USERNAME"] = "validuser"
    os.environ["PASSWORD"] = "validpassword123"
    os.environ["ROLE"] = "admin"

    try:
        cfg = obj.build()

        assert cfg.get("username") == "validuser"
        assert cfg.get("password") == "validpassword123"
        assert cfg.get("role") == "admin"

    finally:
        for key in ["USERNAME", "PASSWORD", "ROLE"]:
            if key in os.environ:
                del os.environ[key]


def test_environment_config_multiple_validators_first_fails():
    """Test that if first validator fails, exception is raised immediately"""
    obj = ConfigWithMultipleValidators()

    # Set invalid username (will fail first validator)
    os.environ["USERNAME"] = "ab"  # Too short
    os.environ["PASSWORD"] = "validpassword123"
    os.environ["ROLE"] = "admin"

    try:
        with pytest.raises(ValueError, match="Username must be at least 3 characters"):
            obj.build()

    finally:
        for key in ["USERNAME", "PASSWORD", "ROLE"]:
            if key in os.environ:
                del os.environ[key]


def test_environment_config_validator_with_default_values():
    """Test validators work with default values (no env vars set)"""
    obj = ConfigWithValidators()

    # Default API_KEY is None, which should fail validation
    with pytest.raises(ValueError, match="API key must be at least 10 characters long"):
        obj.build()


def test_environment_config_validator_method_naming():
    """Test that only methods starting with 'validate_' are called"""

    class ConfigWithMixedMethods(EnvironmentConfig):
        TEST_VALUE = "test"

        def validate_this_should_run(self, data: dict):
            # This should be called
            if data.get("test_value") == "fail":
                raise ValueError("Validation failed")

        def other_method(self, data: dict):
            # This should NOT be called
            raise ValueError("This should not run")

        def _validate_private(self, data: dict):
            # This should NOT be called (starts with underscore)
            raise ValueError("Private method should not run")

    obj = ConfigWithMixedMethods()

    # Should build successfully - only validate_this_should_run is called
    cfg = obj.build()
    assert cfg.get("test_value") == "test"

    # Now test that the validator actually works
    os.environ["TEST_VALUE"] = "fail"
    try:
        with pytest.raises(ValueError, match="Validation failed"):
            obj.build()
    finally:
        if "TEST_VALUE" in os.environ:
            del os.environ["TEST_VALUE"]


def test_environment_config_validator_execution_order():
    """Test that validators are executed in the order they appear in dir()"""

    execution_order = []

    class ConfigWithOrderedValidators(EnvironmentConfig):
        TEST_VALUE = "test"

        def validate_a_first(self, data: dict):
            execution_order.append("a")

        def validate_b_second(self, data: dict):
            execution_order.append("b")

        def validate_c_third(self, data: dict):
            execution_order.append("c")

    obj = ConfigWithOrderedValidators()
    cfg = obj.build()

    # Check that validators were called in alphabetical order (dir() order)
    assert execution_order == ["a", "b", "c"]
