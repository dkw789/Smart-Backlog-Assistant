"""Centralized configuration management for Smart Backlog Assistant."""

from typing import List, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # Logging Configuration
    log_level: str = Field(default="INFO", description="Logging level")
    log_file: str = Field(default="backlog_assistant.log", description="Log file path")

    # AI Service Configuration
    openai_api_key: Optional[str] = Field(default=None, description="OpenAI API key")
    anthropic_api_key: Optional[str] = Field(
        default=None, description="Anthropic API key"
    )
    default_ai_service: str = Field(
        default="anthropic", description="Default AI service to use"
    )

    # AI Request Configuration
    max_retries: int = Field(
        default=3, description="Maximum retry attempts for AI requests"
    )
    timeout_seconds: int = Field(default=30, description="Request timeout in seconds")
    max_tokens: int = Field(default=2000, description="Maximum tokens for AI responses")
    temperature: float = Field(default=0.7, description="AI response temperature")
    
    # AI Model Configuration
    openai_model: str = Field(default="gpt-4", description="OpenAI model to use")
    anthropic_model: str = Field(default="claude-3-haiku-20240307", description="Anthropic model to use")
    qwen_model: str = Field(default="qwen3.5:cloud", description="Qwen model to use")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, description="API server port")
    api_secret_key: str = Field(default="your-secret-key-change-in-production", description="API JWT secret key")
    api_cors_origins: List[str] = Field(default=["*"], description="CORS allowed origins")
    api_rate_limit: str = Field(default="100/minute", description="API rate limit")
    api_max_file_size: int = Field(default=10 * 1024 * 1024, description="Max upload file size in bytes")

    # Circuit Breaker Configuration
    circuit_breaker_failure_threshold: int = Field(
        default=5, description="Circuit breaker failure threshold"
    )
    circuit_breaker_recovery_timeout: float = Field(
        default=60.0, description="Circuit breaker recovery timeout"
    )
    circuit_breaker_success_threshold: int = Field(
        default=3, description="Circuit breaker success threshold"
    )

    # Cache Configuration
    cache_ttl_seconds: int = Field(
        default=3600, description="Default cache TTL in seconds"
    )
    cache_max_size: int = Field(default=1000, description="Maximum cache size")
    enable_caching: bool = Field(default=True, description="Enable caching")

    # File Processing Configuration
    max_file_size_mb: int = Field(default=50, description="Maximum file size in MB")
    supported_file_extensions: List[str] = Field(
        default=[".txt", ".md", ".pdf", ".docx", ".json"],
        description="Supported file extensions",
    )

    # Sprint Planning Configuration
    default_sprint_capacity: int = Field(
        default=40, description="Default sprint capacity in story points"
    )

    # Development Configuration
    debug_mode: bool = Field(default=False, description="Enable debug mode")
    use_mock_providers: bool = Field(
        default=False, description="Use mock providers for testing"
    )

    def get_ai_service_config(self) -> dict:
        """Get AI service configuration."""
        return {
            "openai_api_key": self.openai_api_key,
            "anthropic_api_key": self.anthropic_api_key,
            "default_service": self.default_ai_service,
            "max_retries": self.max_retries,
            "timeout_seconds": self.timeout_seconds,
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
        }

    def get_circuit_breaker_config(self) -> dict:
        """Get circuit breaker configuration."""
        return {
            "failure_threshold": self.circuit_breaker_failure_threshold,
            "recovery_timeout": self.circuit_breaker_recovery_timeout,
            "success_threshold": self.circuit_breaker_success_threshold,
        }

    def get_cache_config(self) -> dict:
        """Get cache configuration."""
        return {
            "ttl_seconds": self.cache_ttl_seconds,
            "max_size": self.cache_max_size,
            "enabled": self.enable_caching,
        }

    def validate_ai_services(self) -> bool:
        """Validate that at least one AI service is configured."""
        return bool(self.openai_api_key or self.anthropic_api_key)


# Global configuration instance
config = AppConfig()
