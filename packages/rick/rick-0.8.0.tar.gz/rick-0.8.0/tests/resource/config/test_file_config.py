import json
import tempfile
import pytest
from pathlib import Path
from rick.resource.config import (
    FileConfigError,
    JsonFileConfig,
    TomlFileConfig,
    HybridFileConfig,
    json_config_file,
    toml_config_file,
    config_file,
)


# Test configuration classes
class JsonConfigWithDefaults(JsonFileConfig):
    """Test JSON config with default values"""

    db_host = "localhost"
    db_port = 5432
    api_key = None
    debug = False
    max_connections = 10


class JsonConfigWithValidators(JsonFileConfig):
    """Test JSON config with validators"""

    db_host = "localhost"
    db_port = 5432
    api_key = None

    def validate_database(self, data: dict):
        if data.get("db_port", 0) <= 0:
            raise ValueError("Database port must be positive")

        if not data.get("db_host"):
            raise ValueError("Database host is required")

    def validate_api_key(self, data: dict):
        api_key = data.get("api_key")
        if api_key and len(api_key) < 10:
            raise ValueError("API key must be at least 10 characters")


class TomlConfigWithDefaults(TomlFileConfig):
    """Test TOML config with default values"""

    app_name = "MyApp"
    port = 8000
    debug = False
    features = {"caching": True}


class TomlConfigWithValidators(TomlFileConfig):
    """Test TOML config with validators"""

    port = 8000
    log_level = "INFO"

    def validate_port(self, data: dict):
        port = data.get("port", 0)
        if not (1 <= port <= 65535):
            raise ValueError("Port must be between 1 and 65535")

    def validate_log_level(self, data: dict):
        level = data.get("log_level", "INFO")
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if level not in valid_levels:
            raise ValueError(f"Invalid log level: {level}")


class HybridConfigWithDefaults(HybridFileConfig):
    """Test hybrid config with default values"""

    service_name = "api"
    timeout = 30
    enabled = True


# Test data
valid_json_data = {
    "db_host": "production-server",
    "db_port": 3306,
    "api_key": "valid_api_key_1234567890",
    "debug": True,
    "max_connections": 50,
}

valid_toml_data = """
app_name = "ProductionApp"
port = 9000
debug = true

[features]
caching = false
logging = true
"""

invalid_json_data = '{"invalid": json syntax}'

invalid_toml_data = """
invalid toml syntax
[unclosed section
"""


@pytest.fixture
def temp_json_file():
    """Create temporary JSON config file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(valid_json_data, f)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_toml_file():
    """Create temporary TOML config file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(valid_toml_data)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_invalid_json_file():
    """Create temporary invalid JSON file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(invalid_json_data)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def temp_invalid_toml_file():
    """Create temporary invalid TOML file"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(invalid_toml_data)
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


# JSON Configuration Tests
def test_json_config_with_defaults_file_exists(temp_json_file):
    """Test JSON config loading with file data overriding defaults"""
    config = JsonConfigWithDefaults(temp_json_file)
    result = config.build()

    # File values should override defaults
    assert result.get("db_host") == "production-server"
    assert result.get("db_port") == 3306
    assert result.get("api_key") == "valid_api_key_1234567890"
    assert result.get("debug") == True
    assert result.get("max_connections") == 50


def test_json_config_with_defaults_file_missing():
    """Test JSON config with missing file raises appropriate error"""
    config = JsonConfigWithDefaults("nonexistent.json")

    with pytest.raises(FileConfigError, match="JSON config file not found"):
        config.build()


def test_json_config_with_defaults_only():
    """Test JSON config falls back to defaults when file is empty"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({}, f)  # Empty JSON object
        temp_path = Path(f.name)

    try:
        config = JsonConfigWithDefaults(temp_path)
        result = config.build()

        # Should use default values
        assert result.get("db_host") == "localhost"
        assert result.get("db_port") == 5432
        assert result.get("api_key") is None
        assert result.get("debug") == False
        assert result.get("max_connections") == 10
    finally:
        temp_path.unlink()


def test_json_config_invalid_json(temp_invalid_json_file):
    """Test JSON config with invalid JSON raises error"""
    config = JsonConfigWithDefaults(temp_invalid_json_file)

    with pytest.raises(FileConfigError, match="Invalid JSON"):
        config.build()


def test_json_config_with_validators_success(temp_json_file):
    """Test JSON config with validators passing"""
    config = JsonConfigWithValidators(temp_json_file)
    result = config.build()

    assert result.get("db_host") == "production-server"
    assert result.get("db_port") == 3306
    assert result.get("api_key") == "valid_api_key_1234567890"


def test_json_config_with_validators_failure():
    """Test JSON config with validators failing"""
    # Test API key validator first (validators run in alphabetical order)
    invalid_data = {
        "db_host": "valid-host",  # Valid host
        "db_port": 3306,  # Valid port
        "api_key": "short",  # Short API key should fail first
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(invalid_data, f)
        temp_path = Path(f.name)

    try:
        config = JsonConfigWithValidators(temp_path)

        with pytest.raises(ValueError, match="API key must be at least 10 characters"):
            config.build()
    finally:
        temp_path.unlink()

    # Test database host validator
    invalid_data2 = {
        "db_host": "",  # Empty host should fail
        "db_port": 3306,  # Valid port
        "api_key": "valid_api_key_1234567890",  # Valid API key
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(invalid_data2, f)
        temp_path = Path(f.name)

    try:
        config = JsonConfigWithValidators(temp_path)

        with pytest.raises(ValueError, match="Database host is required"):
            config.build()
    finally:
        temp_path.unlink()


def test_json_config_with_override_data(temp_json_file):
    """Test JSON config with runtime override data"""
    config = JsonConfigWithDefaults(temp_json_file)
    override_data = {"db_port": 9999, "custom_field": "override_value"}

    result = config.build(override_data)

    # Override should take precedence
    assert result.get("db_port") == 9999
    assert result.get("custom_field") == "override_value"
    # Other file values should remain
    assert result.get("db_host") == "production-server"


# TOML Configuration Tests
def test_toml_config_with_defaults_file_exists(temp_toml_file):
    """Test TOML config loading with file data overriding defaults"""
    config = TomlConfigWithDefaults(temp_toml_file)
    result = config.build()

    # File values should override defaults
    assert result.get("app_name") == "ProductionApp"
    assert result.get("port") == 9000
    assert result.get("debug") == True
    # Nested sections should be loaded (as ShallowContainer)
    features = result.get("features")
    assert features.get("caching") == False
    assert features.get("logging") == True


def test_toml_config_with_defaults_file_missing():
    """Test TOML config with missing file raises appropriate error"""
    config = TomlConfigWithDefaults("nonexistent.toml")

    with pytest.raises(FileConfigError, match="TOML config file not found"):
        config.build()


def test_toml_config_invalid_toml(temp_invalid_toml_file):
    """Test TOML config with invalid TOML raises error"""
    config = TomlConfigWithDefaults(temp_invalid_toml_file)

    with pytest.raises(FileConfigError, match="Error reading TOML config file"):
        config.build()


def test_toml_config_with_validators_success():
    """Test TOML config with validators passing"""
    valid_toml = """
port = 8080
log_level = "DEBUG"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(valid_toml)
        temp_path = Path(f.name)

    try:
        config = TomlConfigWithValidators(temp_path)
        result = config.build()

        assert result.get("port") == 8080
        assert result.get("log_level") == "DEBUG"
    finally:
        temp_path.unlink()


def test_toml_config_with_validators_failure():
    """Test TOML config with validators failing"""
    # Test log level validator first (validators run in alphabetical order)
    invalid_toml = """
port = 8080
log_level = "INVALID"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(invalid_toml)
        temp_path = Path(f.name)

    try:
        config = TomlConfigWithValidators(temp_path)

        with pytest.raises(ValueError, match="Invalid log level: INVALID"):
            config.build()
    finally:
        temp_path.unlink()

    # Test port validator
    invalid_toml2 = """
port = 70000
log_level = "INFO"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".toml", delete=False) as f:
        f.write(invalid_toml2)
        temp_path = Path(f.name)

    try:
        config = TomlConfigWithValidators(temp_path)

        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            config.build()
    finally:
        temp_path.unlink()


# Hybrid Configuration Tests
def test_hybrid_config_json_file(temp_json_file):
    """Test hybrid config auto-detecting JSON format"""
    config = HybridConfigWithDefaults(temp_json_file)
    result = config.build()

    # Should successfully load JSON data
    assert result.get("service_name") == "api"  # default
    # JSON file doesn't have these fields, so should keep defaults
    assert result.get("timeout") == 30
    assert result.get("enabled") == True


def test_hybrid_config_toml_file(temp_toml_file):
    """Test hybrid config auto-detecting TOML format"""
    config = HybridConfigWithDefaults(temp_toml_file)
    result = config.build()

    # Should successfully load TOML data
    assert result.get("service_name") == "api"  # default (not in TOML)
    assert result.get("timeout") == 30  # default
    assert result.get("enabled") == True  # default


def test_hybrid_config_unsupported_extension():
    """Test hybrid config with unsupported file extension"""
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
        temp_path = Path(f.name)

    try:
        config = HybridConfigWithDefaults(temp_path)

        with pytest.raises(FileConfigError, match="Unsupported file format: .yaml"):
            config.build()
    finally:
        temp_path.unlink()


# Convenience Function Tests
def test_json_config_file_function(temp_json_file):
    """Test json_config_file convenience function"""
    result = json_config_file(temp_json_file)

    assert result.get("db_host") == "production-server"
    assert result.get("db_port") == 3306
    assert result.get("api_key") == "valid_api_key_1234567890"


def test_toml_config_file_function(temp_toml_file):
    """Test toml_config_file convenience function"""
    result = toml_config_file(temp_toml_file)

    assert result.get("app_name") == "ProductionApp"
    assert result.get("port") == 9000
    assert result.get("debug") == True


def test_config_file_function_json(temp_json_file):
    """Test config_file convenience function with JSON"""
    result = config_file(temp_json_file)

    assert result.get("db_host") == "production-server"
    assert result.get("db_port") == 3306


def test_config_file_function_toml(temp_toml_file):
    """Test config_file convenience function with TOML"""
    result = config_file(temp_toml_file)

    assert result.get("app_name") == "ProductionApp"
    assert result.get("port") == 9000


# Reload functionality tests
def test_config_reload(temp_json_file):
    """Test config reload functionality"""
    config = JsonConfigWithDefaults(temp_json_file)

    # Initial load
    result1 = config.build()
    assert result1.get("db_host") == "production-server"

    # Modify file
    new_data = {"db_host": "updated-server", "db_port": 4444}
    with open(temp_json_file, "w") as f:
        json.dump(new_data, f)

    # Reload should pick up changes
    result2 = config.reload()
    assert result2.get("db_host") == "updated-server"
    assert result2.get("db_port") == 4444


# Error handling tests
def test_file_permission_error():
    """Test handling of file permission errors"""
    # Create a file we can't read (simplified test)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump({"test": "data"}, f)
        temp_path = Path(f.name)

    try:
        # Make file unreadable (this might not work on all systems)
        temp_path.chmod(0o000)

        config = JsonConfigWithDefaults(temp_path)

        with pytest.raises(FileConfigError):
            config.build()
    finally:
        # Restore permissions and cleanup
        temp_path.chmod(0o644)
        temp_path.unlink()


def test_config_with_mixed_validators():
    """Test config with multiple validators that interact"""

    class ComplexConfig(JsonFileConfig):
        user_id = 1
        user_name = "default"
        user_role = "user"

        def validate_user_id(self, data: dict):
            user_id = data.get("user_id", 0)
            if user_id <= 0:
                raise ValueError("User ID must be positive")

        def validate_user_consistency(self, data: dict):
            user_id = data.get("user_id", 0)
            user_role = data.get("user_role", "user")

            # Admin users must have ID >= 100
            if user_role == "admin" and user_id < 100:
                raise ValueError("Admin users must have ID >= 100")

    # Test valid admin user
    valid_admin_data = {"user_id": 150, "user_name": "admin_user", "user_role": "admin"}

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(valid_admin_data, f)
        temp_path = Path(f.name)

    try:
        config = ComplexConfig(temp_path)
        result = config.build()

        assert result.get("user_id") == 150
        assert result.get("user_role") == "admin"
    finally:
        temp_path.unlink()

    # Test invalid admin user (ID too low)
    invalid_admin_data = {
        "user_id": 50,
        "user_name": "admin_user",
        "user_role": "admin",
    }

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(invalid_admin_data, f)
        temp_path = Path(f.name)

    try:
        config = ComplexConfig(temp_path)

        with pytest.raises(ValueError, match="Admin users must have ID >= 100"):
            config.build()
    finally:
        temp_path.unlink()
