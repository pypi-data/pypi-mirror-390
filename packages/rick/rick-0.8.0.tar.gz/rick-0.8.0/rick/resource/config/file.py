import json
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, Union

from rick.base import ShallowContainer

# TOML support - handle different Python versions
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        tomllib = None


class FileConfigError(Exception):
    """Exception raised for file configuration errors"""

    pass


class BaseFileConfig(ABC):
    """
    Base class for file-based configuration with validator support

    Similar to EnvironmentConfig but loads configuration from files (JSON/TOML)
    instead of environment variables.

    Example:
        class MyConfig(JsonFileConfig):
            # Default values
            db_host = 'localhost'
            db_port = 5432
            api_key = None

            def validate_database(self, data: dict):
                if data.get('db_port', 0) <= 0:
                    raise ValueError("Database port must be positive")

            def validate_api_key(self, data: dict):
                api_key = data.get('api_key')
                if not api_key or len(api_key) < 10:
                    raise ValueError("API key must be at least 10 characters")

        # Usage
        config = MyConfig("config.json").build()
        assert config.db_host == "localhost"  # from file or default
    """

    def __init__(self, file_path: Union[str, Path]):
        """
        Initialize with config file path

        :param file_path: Path to the configuration file
        """
        self.file_path = Path(file_path)
        self._loaded_data = None

    @abstractmethod
    def _load_file(self) -> Dict[str, Any]:
        """
        Load and parse the configuration file

        :return: Dictionary containing the parsed configuration
        :raises FileConfigError: If file cannot be loaded or parsed
        """
        pass

    def build(self, override_data: Optional[Dict[str, Any]] = None) -> ShallowContainer:
        """
        Build the final configuration by merging defaults, file data, and overrides

        :param override_data: Optional dictionary to override specific values
        :return: ShallowContainer with the final configuration
        """
        # Start with default values from class attributes
        data = {}
        for name in dir(self):
            if not name.startswith("_") and not callable(getattr(self, name)):
                # Skip methods and private attributes
                attr_value = getattr(self, name)
                if not callable(attr_value):
                    data[name] = attr_value

        # Load and merge file data
        try:
            file_data = self._load_file()
            data.update(file_data)
        except Exception as e:
            raise FileConfigError(f"Error loading config file '{self.file_path}': {e}")

        # Apply any override data
        if override_data:
            data.update(override_data)

        # Run validators
        self._run_validators(data)

        return ShallowContainer(data)

    def _run_validators(self, data: Dict[str, Any]):
        """
        Call optional validator functions

        A validator function must have a name starting with validate_ and should
        raise exceptions if validation fails

        :param data: Configuration data to validate
        """
        for attr_name in dir(self):
            if attr_name.startswith("validate_"):
                method = getattr(self, attr_name)
                if callable(method):
                    method(data)

    def reload(self) -> ShallowContainer:
        """
        Reload configuration from file

        :return: Fresh ShallowContainer with reloaded configuration
        """
        self._loaded_data = None
        return self.build()


class JsonFileConfig(BaseFileConfig):
    """
    JSON file-based configuration class

    Loads configuration from JSON files with support for default values,
    validation, and runtime overrides.

    Example JSON file (config.json):
    {
        "db_host": "production-server",
        "db_port": 3306,
        "api_key": "prod_api_key_12345678901234567890",
        "features": {
            "enable_caching": true,
            "max_connections": 100
        }
    }

    Example usage:
        class DatabaseConfig(JsonFileConfig):
            # Defaults
            db_host = "localhost"
            db_port = 5432
            api_key = None

            def validate_connection(self, data):
                if not data.get('db_host'):
                    raise ValueError("Database host is required")

        config = DatabaseConfig("config.json").build()
    """

    def _load_file(self) -> Dict[str, Any]:
        """Load JSON configuration file"""
        if not self.file_path.exists():
            raise FileConfigError(f"JSON config file not found: {self.file_path}")

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise FileConfigError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise FileConfigError(f"Error reading JSON config file: {e}")


class TomlFileConfig(BaseFileConfig):
    """
    TOML file-based configuration class

    Loads configuration from TOML files with support for default values,
    validation, and runtime overrides.

    Requires Python 3.11+ (built-in tomllib) or tomli package for older versions.

    Example TOML file (config.toml):
    db_host = "production-server"
    db_port = 3306
    api_key = "prod_api_key_12345678901234567890"

    [features]
    enable_caching = true
    max_connections = 100

    [logging]
    level = "INFO"
    format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    Example usage:
        class AppConfig(TomlFileConfig):
            # Defaults
            db_host = "localhost"
            db_port = 5432
            api_key = None

            def validate_logging(self, data):
                level = data.get('logging', {}).get('level', 'INFO')
                valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
                if level not in valid_levels:
                    raise ValueError(f"Invalid log level: {level}")

        config = AppConfig("config.toml").build()
    """

    def _load_file(self) -> Dict[str, Any]:
        """Load TOML configuration file"""
        if tomllib is None:
            raise FileConfigError(
                "TOML support requires Python 3.11+ or 'tomli' package. "
                "Install with: pip install tomli"
            )

        if not self.file_path.exists():
            raise FileConfigError(f"TOML config file not found: {self.file_path}")

        try:
            with open(self.file_path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            raise FileConfigError(f"Error reading TOML config file: {e}")


class HybridFileConfig(BaseFileConfig):
    """
    Hybrid configuration class that auto-detects file format

    Automatically determines whether to use JSON or TOML parsing based on file extension.
    Supports .json, .toml, and .tml extensions.

    Example usage:
        class MyConfig(HybridFileConfig):
            debug = False
            port = 8000

            def validate_port(self, data):
                port = data.get('port', 0)
                if not (1 <= port <= 65535):
                    raise ValueError("Port must be between 1 and 65535")

        # Works with either format
        config1 = MyConfig("config.json").build()
        config2 = MyConfig("config.toml").build()
    """

    def _load_file(self) -> Dict[str, Any]:
        """Load configuration file, auto-detecting format from extension"""
        if not self.file_path.exists():
            raise FileConfigError(f"Config file not found: {self.file_path}")

        suffix = self.file_path.suffix.lower()

        if suffix == ".json":
            return self._load_json()
        elif suffix in [".toml", ".tml"]:
            return self._load_toml()
        else:
            raise FileConfigError(
                f"Unsupported file format: {suffix}. "
                "Supported formats: .json, .toml, .tml"
            )

    def _load_json(self) -> Dict[str, Any]:
        """Load JSON file"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            raise FileConfigError(f"Invalid JSON: {e}")
        except Exception as e:
            raise FileConfigError(f"Error reading JSON file: {e}")

    def _load_toml(self) -> Dict[str, Any]:
        """Load TOML file"""
        if tomllib is None:
            raise FileConfigError(
                "TOML support requires Python 3.11+ or 'tomli' package. "
                "Install with: pip install tomli"
            )

        try:
            with open(self.file_path, "rb") as f:
                return tomllib.load(f)
        except Exception as e:
            raise FileConfigError(f"Error reading TOML file: {e}")


# Convenience functions for quick file loading (similar to existing json_file)
def json_config_file(filename: Union[str, Path]) -> ShallowContainer:
    """
    Simple JSON config file loader (enhanced version of existing json_file)

    :param filename: Path to JSON configuration file
    :return: ShallowContainer with loaded configuration
    :raises FileConfigError: If file cannot be loaded
    """

    class SimpleJsonConfig(JsonFileConfig):
        pass

    return SimpleJsonConfig(filename).build()


def toml_config_file(filename: Union[str, Path]) -> ShallowContainer:
    """
    Simple TOML config file loader

    :param filename: Path to TOML configuration file
    :return: ShallowContainer with loaded configuration
    :raises FileConfigError: If file cannot be loaded
    """

    class SimpleTomlConfig(TomlFileConfig):
        pass

    return SimpleTomlConfig(filename).build()


def config_file(filename: Union[str, Path]) -> ShallowContainer:
    """
    Auto-detecting config file loader

    :param filename: Path to configuration file (JSON or TOML)
    :return: ShallowContainer with loaded configuration
    :raises FileConfigError: If file cannot be loaded
    """

    class SimpleHybridConfig(HybridFileConfig):
        pass

    return SimpleHybridConfig(filename).build()
