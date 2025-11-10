"""Configuration schemas using Pydantic."""

from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class CoreConfig(BaseModel):
    """Core bus configuration."""

    max_subscriptions: int = Field(
        default=10000, ge=1, description="Maximum number of subscriptions allowed"
    )
    dispatch_timeout: float = Field(default=30.0, gt=0, description="Dispatch timeout in seconds")
    handler_timeout: float = Field(
        default=10.0, gt=0, description="Individual handler timeout in seconds"
    )
    enable_error_isolation: bool = Field(
        default=True, description="Isolate handler errors to prevent bus crashes"
    )
    enable_parallel_dispatch: bool = Field(
        default=True, description="Enable parallel handler execution"
    )
    max_concurrent_handlers: int = Field(
        default=100, ge=1, description="Maximum concurrent handler executions"
    )


class SemanticConfig(BaseModel):
    """Semantic routing configuration."""

    enabled: bool = Field(default=False, description="Enable semantic routing")
    model_name: str = Field(
        default="all-MiniLM-L6-v2", description="Sentence transformer model name"
    )
    embedding_dim: int = Field(default=384, ge=1, description="Embedding dimension")
    default_threshold: float = Field(
        default=0.75, ge=0.0, le=1.0, description="Default similarity threshold"
    )
    cache_size: int = Field(default=1000, ge=0, description="Embedding cache size (0 = no cache)")
    cache_ttl: int = Field(default=3600, ge=0, description="Cache TTL in seconds (0 = no expiry)")


class ContextConfig(BaseModel):
    """Context engine configuration."""

    enabled: bool = Field(default=False, description="Enable context engine")
    max_context_size: int = Field(
        default=1000, ge=1, description="Maximum context entries per scope"
    )
    enable_dsl_filters: bool = Field(default=True, description="Enable DSL filter expressions")


class TemporalConfig(BaseModel):
    """Temporal store configuration."""

    enabled: bool = Field(default=False, description="Enable event persistence")
    store_path: Path = Field(
        default=Path("./temporal_store"), description="Path to temporal store database"
    )
    wal_enabled: bool = Field(default=True, description="Enable write-ahead logging")
    max_events: int = Field(
        default=1_000_000, ge=0, description="Maximum events to store (0 = unlimited)"
    )
    auto_cleanup: bool = Field(default=True, description="Automatically cleanup old events")
    retention_days: int = Field(default=30, ge=1, description="Event retention period in days")


class MemoryConfig(BaseModel):
    """Memory integration configuration."""

    enabled: bool = Field(default=False, description="Enable memory integration")
    adapter: str = Field(default="qdrant", description="Memory adapter (qdrant, lancedb)")
    connection_string: str = Field(
        default="http://localhost:6333", description="Memory store connection string"
    )
    collection_name: str = Field(default="neurobus_events", description="Collection/table name")
    auto_store: bool = Field(default=True, description="Automatically store events in memory")


class LLMConfig(BaseModel):
    """LLM integration configuration."""

    enabled: bool = Field(default=False, description="Enable LLM hooks")
    provider: str = Field(
        default="anthropic", description="LLM provider (anthropic, openai, ollama)"
    )
    model: str = Field(default="claude-sonnet-4", description="Model name")
    api_key: str = Field(default="", description="API key for provider")
    timeout: float = Field(default=30.0, gt=0, description="LLM request timeout")


class MonitoringConfig(BaseModel):
    """Monitoring configuration."""

    enabled: bool = Field(default=False, description="Enable monitoring")
    prometheus_enabled: bool = Field(default=False, description="Enable Prometheus metrics")
    prometheus_port: int = Field(
        default=9090, ge=1024, le=65535, description="Prometheus metrics port"
    )
    tracing_enabled: bool = Field(default=False, description="Enable OpenTelemetry tracing")
    logging_level: str = Field(default="INFO", description="Logging level")
    structured_logging: bool = Field(default=True, description="Use structured JSON logging")

    @field_validator("logging_level")
    @classmethod
    def validate_logging_level(cls, v: str) -> str:
        """Validate logging level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid logging level. Must be one of: {valid_levels}")
        return v_upper


class DistributedConfig(BaseModel):
    """Distributed clustering configuration."""

    enabled: bool = Field(default=False, description="Enable distributed clustering")
    redis_url: str = Field(default="redis://localhost:6379", description="Redis connection URL")
    node_id: str | None = Field(
        default=None, description="Node identifier (auto-generated if None)"
    )
    enable_deduplication: bool = Field(default=True, description="Enable event deduplication")
    dedup_window: int = Field(default=60, ge=1, description="Deduplication window in seconds")
    heartbeat_interval: int = Field(default=5, ge=1, description="Heartbeat interval in seconds")
    node_timeout: int = Field(default=15, ge=1, description="Node timeout in seconds")


class NeuroBusConfig(BaseModel):
    """Complete NeuroBUS configuration."""

    # Component configs
    core: CoreConfig = Field(default_factory=CoreConfig)
    semantic: SemanticConfig = Field(default_factory=SemanticConfig)
    context: ContextConfig = Field(default_factory=ContextConfig)
    temporal: TemporalConfig = Field(default_factory=TemporalConfig)
    memory: MemoryConfig = Field(default_factory=MemoryConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    distributed: DistributedConfig = Field(default_factory=DistributedConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)

    # Global settings
    environment: str = Field(
        default="development", description="Environment (development, production, testing)"
    )
    debug: bool = Field(default=False, description="Enable debug mode")

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization validation."""
        # Auto-enable debug logging in debug mode
        if self.debug and self.monitoring.logging_level != "DEBUG":
            self.monitoring.logging_level = "DEBUG"

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "NeuroBusConfig":
        """
        Create config from dictionary.

        Args:
            data: Configuration dictionary

        Returns:
            NeuroBusConfig instance
        """
        return cls(**data)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert config to dictionary.

        Returns:
            Configuration dictionary
        """
        return self.model_dump()
