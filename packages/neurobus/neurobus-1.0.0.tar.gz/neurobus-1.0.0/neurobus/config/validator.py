"""Configuration validation utilities."""

from pathlib import Path

from neurobus.config.schema import NeuroBusConfig
from neurobus.exceptions.core import ConfigurationError


def validate_config(config: NeuroBusConfig) -> None:
    """
    Validate configuration for consistency and compatibility.

    Args:
        config: Configuration to validate

    Raises:
        ConfigurationError: If configuration is invalid
    """
    # Validate semantic config
    if config.semantic.enabled:
        if config.semantic.embedding_dim <= 0:
            raise ConfigurationError("semantic.embedding_dim", "Must be positive")

        if not config.semantic.model_name:
            raise ConfigurationError(
                "semantic.model_name", "Model name required when semantic routing enabled"
            )

    # Validate temporal config
    if config.temporal.enabled:
        store_path = Path(config.temporal.store_path)

        # Check if parent directory exists
        if not store_path.parent.exists():
            raise ConfigurationError(
                "temporal.store_path", f"Parent directory does not exist: {store_path.parent}"
            )

        if config.temporal.retention_days < 1:
            raise ConfigurationError("temporal.retention_days", "Must be at least 1 day")

    # Validate memory config
    if config.memory.enabled:
        if not config.memory.adapter:
            raise ConfigurationError(
                "memory.adapter", "Adapter required when memory integration enabled"
            )

        valid_adapters = ["qdrant", "lancedb"]
        if config.memory.adapter not in valid_adapters:
            raise ConfigurationError("memory.adapter", f"Must be one of: {valid_adapters}")

        if not config.memory.connection_string:
            raise ConfigurationError(
                "memory.connection_string", "Connection string required when memory enabled"
            )

    # Validate LLM config
    if config.llm.enabled:
        if not config.llm.provider:
            raise ConfigurationError("llm.provider", "Provider required when LLM hooks enabled")

        valid_providers = ["anthropic", "openai", "ollama"]
        if config.llm.provider not in valid_providers:
            raise ConfigurationError("llm.provider", f"Must be one of: {valid_providers}")

        # API key required for cloud providers
        if config.llm.provider in ["anthropic", "openai"] and not config.llm.api_key:
            raise ConfigurationError(
                "llm.api_key", f"API key required for provider: {config.llm.provider}"
            )

    # Validate monitoring config
    if config.monitoring.prometheus_enabled:
        port = config.monitoring.prometheus_port
        if not (1024 <= port <= 65535):
            raise ConfigurationError(
                "monitoring.prometheus_port", f"Port must be between 1024 and 65535, got {port}"
            )

    # Warn about incompatible settings
    if config.semantic.enabled and config.semantic.cache_size == 0:
        # Just a warning, not an error
        pass

    if config.core.max_concurrent_handlers < 10:
        # Warn about potential performance issues
        pass


def check_dependencies(config: NeuroBusConfig) -> list[str]:
    """
    Check which optional dependencies are required for the config.

    Args:
        config: Configuration to check

    Returns:
        List of missing required dependencies
    """
    missing = []

    if config.semantic.enabled:
        try:
            import sentence_transformers  # noqa
        except ImportError:
            missing.append("sentence-transformers")

    if config.memory.enabled:
        if config.memory.adapter == "qdrant":
            try:
                import qdrant_client  # noqa
            except ImportError:
                missing.append("qdrant-client")
        elif config.memory.adapter == "lancedb":
            try:
                import lancedb  # noqa
            except ImportError:
                missing.append("lancedb")

    if config.llm.enabled:
        if config.llm.provider == "anthropic":
            try:
                import anthropic  # noqa
            except ImportError:
                missing.append("anthropic")
        elif config.llm.provider == "openai":
            try:
                import openai  # noqa
            except ImportError:
                missing.append("openai")

    if config.monitoring.prometheus_enabled:
        try:
            import prometheus_client  # noqa
        except ImportError:
            missing.append("prometheus-client")

    if config.monitoring.tracing_enabled:
        try:
            import opentelemetry  # noqa
        except ImportError:
            missing.append("opentelemetry-api")

    return missing
