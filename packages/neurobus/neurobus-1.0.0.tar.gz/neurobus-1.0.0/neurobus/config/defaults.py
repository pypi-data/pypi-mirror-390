"""Default configuration values."""

from neurobus.config.schema import NeuroBusConfig

# Default development configuration
DEFAULT_DEV_CONFIG = NeuroBusConfig(
    environment="development",
    debug=True,
)

# Default production configuration
DEFAULT_PROD_CONFIG = NeuroBusConfig(
    environment="production",
    debug=False,
    core={
        "max_subscriptions": 50000,
        "dispatch_timeout": 60.0,
        "handler_timeout": 30.0,
        "max_concurrent_handlers": 500,
    },
    monitoring={
        "enabled": True,
        "prometheus_enabled": True,
        "logging_level": "INFO",
        "structured_logging": True,
    },
)

# Default testing configuration
DEFAULT_TEST_CONFIG = NeuroBusConfig(
    environment="testing",
    debug=False,
    monitoring={
        "enabled": False,
        "logging_level": "WARNING",
    },
)


def get_default_config(environment: str = "development") -> NeuroBusConfig:
    """
    Get default configuration for environment.

    Args:
        environment: Environment name (development, production, testing)

    Returns:
        Default configuration for environment

    Raises:
        ValueError: If environment is not recognized
    """
    configs = {
        "development": DEFAULT_DEV_CONFIG,
        "production": DEFAULT_PROD_CONFIG,
        "testing": DEFAULT_TEST_CONFIG,
    }

    if environment not in configs:
        raise ValueError(
            f"Unknown environment: {environment}. " f"Must be one of: {list(configs.keys())}"
        )

    return configs[environment]
