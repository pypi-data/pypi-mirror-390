"""Configuration loading utilities."""

import os
from pathlib import Path
from typing import Any

import yaml

from neurobus.config.defaults import get_default_config
from neurobus.config.schema import NeuroBusConfig
from neurobus.exceptions.core import ConfigurationError


def load_from_yaml(path: Path | str) -> NeuroBusConfig:
    """
    Load configuration from YAML file.

    Args:
        path: Path to YAML configuration file

    Returns:
        Loaded configuration

    Raises:
        ConfigurationError: If file cannot be loaded or parsed
    """
    path = Path(path)

    if not path.exists():
        raise ConfigurationError(str(path), f"Configuration file not found: {path}")

    try:
        with open(path) as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        raise ConfigurationError(str(path), f"Failed to parse YAML: {e}")
    except OSError as e:
        raise ConfigurationError(str(path), f"Failed to read file: {e}")

    if data is None:
        data = {}

    try:
        return NeuroBusConfig.from_dict(data)
    except Exception as e:
        raise ConfigurationError(str(path), f"Invalid configuration: {e}")


def load_from_env() -> dict[str, Any]:
    """
    Load configuration overrides from environment variables.

    Environment variables should be prefixed with NEUROBUS_ and use
    double underscores for nesting, e.g.:
    - NEUROBUS_CORE__MAX_SUBSCRIPTIONS=5000
    - NEUROBUS_SEMANTIC__ENABLED=true

    Returns:
        Dictionary of configuration overrides
    """
    config: dict[str, Any] = {}
    prefix = "NEUROBUS_"

    for key, value in os.environ.items():
        if not key.startswith(prefix):
            continue

        # Remove prefix and parse nested keys
        key_path = key[len(prefix) :].lower().split("__")

        # Navigate/create nested dict structure
        current = config
        for part in key_path[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]

        # Set the value with type conversion
        current[key_path[-1]] = _parse_env_value(value)

    return config


def _parse_env_value(value: str) -> Any:
    """
    Parse environment variable value to appropriate type.

    Args:
        value: String value from environment

    Returns:
        Parsed value (bool, int, float, or str)
    """
    # Boolean
    if value.lower() in ("true", "yes", "1", "on"):
        return True
    if value.lower() in ("false", "no", "0", "off"):
        return False

    # Integer
    try:
        return int(value)
    except ValueError:
        pass

    # Float
    try:
        return float(value)
    except ValueError:
        pass

    # String (default)
    return value


def merge_configs(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    """
    Deep merge configuration dictionaries.

    Args:
        base: Base configuration
        override: Overriding configuration

    Returns:
        Merged configuration
    """
    result = base.copy()

    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_configs(result[key], value)
        else:
            result[key] = value

    return result


def load_config(
    config_path: Path | str | None = None,
    environment: str | None = None,
    use_env: bool = True,
) -> NeuroBusConfig:
    """
    Load configuration with cascading overrides.

    Priority (highest to lowest):
    1. Environment variables (if use_env=True)
    2. Config file (if config_path provided)
    3. Default config for environment

    Args:
        config_path: Optional path to YAML config file
        environment: Environment name (development, production, testing)
        use_env: Whether to load environment variable overrides

    Returns:
        Loaded and merged configuration
    """
    # Start with default config
    env = environment or os.environ.get("NEUROBUS_ENV", "development")
    config_dict = get_default_config(env).to_dict()

    # Override with config file if provided
    if config_path:
        file_config = load_from_yaml(config_path)
        config_dict = merge_configs(config_dict, file_config.to_dict())

    # Override with environment variables
    if use_env:
        env_config = load_from_env()
        if env_config:
            config_dict = merge_configs(config_dict, env_config)

    return NeuroBusConfig.from_dict(config_dict)
