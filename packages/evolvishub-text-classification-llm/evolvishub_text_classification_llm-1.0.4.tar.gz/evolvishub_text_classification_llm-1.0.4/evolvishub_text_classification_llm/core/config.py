"""
Configuration system for the text classification library.

This module provides comprehensive configuration management with support
for environment variables, configuration files (YAML/JSON/TOML), and
programmatic configuration.
"""

import os
import json
import yaml
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator

from .schemas import ProviderConfig, WorkflowConfig, ProviderType
from .exceptions import ConfigurationError


class CacheConfig(BaseModel):
    """Configuration for caching system."""
    
    enabled: bool = Field(True, description="Enable caching")
    cache_type: str = Field("memory", description="Cache type (memory, redis, disk)")
    
    # Memory cache settings
    max_memory_items: int = Field(1000, description="Maximum items in memory cache")
    memory_ttl_seconds: int = Field(3600, description="Memory cache TTL")
    
    # Redis cache settings
    redis_url: Optional[str] = Field(None, description="Redis connection URL")
    redis_db: int = Field(0, description="Redis database number")
    redis_ttl_seconds: int = Field(7200, description="Redis cache TTL")
    
    # Disk cache settings
    disk_cache_dir: Optional[str] = Field(None, description="Disk cache directory")
    disk_max_size_mb: int = Field(1000, description="Maximum disk cache size in MB")
    disk_ttl_seconds: int = Field(86400, description="Disk cache TTL")
    
    # Cache behavior
    enable_deduplication: bool = Field(True, description="Enable response deduplication")
    similarity_threshold: float = Field(0.95, description="Similarity threshold for deduplication")
    cache_key_prefix: str = Field("tcllm", description="Cache key prefix")


class MonitoringConfig(BaseModel):
    """Configuration for monitoring and observability."""
    
    enabled: bool = Field(True, description="Enable monitoring")
    
    # Metrics
    enable_metrics: bool = Field(True, description="Enable metrics collection")
    metrics_port: int = Field(9090, description="Prometheus metrics port")
    metrics_path: str = Field("/metrics", description="Metrics endpoint path")
    
    # Logging
    log_level: str = Field("INFO", description="Logging level")
    log_format: str = Field("structured", description="Log format (structured, plain)")
    log_file: Optional[str] = Field(None, description="Log file path")
    enable_correlation_id: bool = Field(True, description="Enable correlation ID tracking")
    
    # Health checks
    health_check_interval: int = Field(30, description="Health check interval in seconds")
    health_check_timeout: int = Field(10, description="Health check timeout in seconds")
    
    # Performance tracking
    enable_performance_tracking: bool = Field(True, description="Enable performance tracking")
    slow_request_threshold_ms: float = Field(5000.0, description="Slow request threshold")
    
    # Cost tracking
    enable_cost_tracking: bool = Field(True, description="Enable cost tracking")
    cost_alert_threshold: float = Field(100.0, description="Cost alert threshold in USD")


class SecurityConfig(BaseModel):
    """Configuration for security features."""
    
    # Input validation
    enable_input_sanitization: bool = Field(True, description="Enable input sanitization")
    max_input_length: int = Field(100000, description="Maximum input text length")
    blocked_patterns: List[str] = Field(default_factory=list, description="Blocked text patterns")
    
    # PII detection
    enable_pii_detection: bool = Field(True, description="Enable PII detection")
    pii_redaction_mode: str = Field("mask", description="PII redaction mode (mask, remove, hash)")
    
    # Rate limiting
    enable_rate_limiting: bool = Field(True, description="Enable rate limiting")
    requests_per_minute: int = Field(100, description="Requests per minute limit")
    burst_limit: int = Field(20, description="Burst request limit")
    
    # API security
    require_api_key: bool = Field(False, description="Require API key authentication")
    api_key_header: str = Field("X-API-Key", description="API key header name")
    allowed_origins: List[str] = Field(default_factory=list, description="Allowed CORS origins")
    
    # Audit logging
    enable_audit_logging: bool = Field(True, description="Enable audit logging")
    audit_log_file: Optional[str] = Field(None, description="Audit log file path")


class PerformanceConfig(BaseModel):
    """Configuration for performance optimization."""
    
    # Concurrency
    max_concurrent_requests: int = Field(50, description="Maximum concurrent requests")
    request_timeout_seconds: int = Field(30, description="Request timeout")
    batch_timeout_seconds: int = Field(300, description="Batch processing timeout")
    
    # Memory management
    max_memory_usage_mb: int = Field(4000, description="Maximum memory usage in MB")
    enable_memory_monitoring: bool = Field(True, description="Enable memory monitoring")
    gc_threshold: float = Field(0.8, description="Garbage collection threshold")
    
    # Provider optimization
    enable_provider_fallback: bool = Field(True, description="Enable provider fallback")
    fallback_delay_seconds: float = Field(1.0, description="Delay before fallback")
    enable_cost_optimization: bool = Field(True, description="Enable cost optimization")
    
    # Batch processing
    default_batch_size: int = Field(100, description="Default batch size")
    max_batch_size: int = Field(1000, description="Maximum batch size")
    batch_processing_mode: str = Field("parallel", description="Batch processing mode")


class LibraryConfig(BaseModel):
    """Main configuration class for the text classification library."""
    
    # Core settings
    library_name: str = Field("evolvishub-text-classification-llm", description="Library name")
    version: str = Field("1.0.0", description="Library version")
    environment: str = Field("development", description="Environment (development, staging, production)")
    
    # Default provider settings
    default_provider: str = Field("openai", description="Default LLM provider")
    default_model: str = Field("gpt-3.5-turbo", description="Default model")
    
    # Component configurations
    cache: CacheConfig = Field(default_factory=CacheConfig, description="Cache configuration")
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig, description="Monitoring configuration")
    security: SecurityConfig = Field(default_factory=SecurityConfig, description="Security configuration")
    performance: PerformanceConfig = Field(default_factory=PerformanceConfig, description="Performance configuration")
    
    # Provider configurations
    providers: Dict[str, ProviderConfig] = Field(default_factory=dict, description="Provider configurations")
    
    # Workflow configurations
    workflows: Dict[str, WorkflowConfig] = Field(default_factory=dict, description="Workflow configurations")
    
    # Custom configuration
    custom: Dict[str, Any] = Field(default_factory=dict, description="Custom configuration parameters")
    
    @validator('environment')
    def validate_environment(cls, v):
        """Validate environment value."""
        valid_environments = ['development', 'staging', 'production', 'test']
        if v not in valid_environments:
            raise ValueError(f"Environment must be one of {valid_environments}")
        return v
    
    @validator('default_provider')
    def validate_default_provider(cls, v):
        """Validate default provider."""
        valid_providers = [provider.value for provider in ProviderType]
        if v not in valid_providers:
            raise ValueError(f"Default provider must be one of {valid_providers}")
        return v
    
    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> 'LibraryConfig':
        """
        Load configuration from file.
        
        Args:
            config_path: Path to configuration file (YAML, JSON, or TOML)
            
        Returns:
            LibraryConfig instance
            
        Raises:
            ConfigurationError: If file cannot be loaded or parsed
        """
        config_path = Path(config_path)
        
        if not config_path.exists():
            raise ConfigurationError(
                f"Configuration file not found: {config_path}",
                config_file=str(config_path)
            )
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                if config_path.suffix.lower() in ['.yaml', '.yml']:
                    config_data = yaml.safe_load(f)
                elif config_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                elif config_path.suffix.lower() == '.toml':
                    try:
                        import tomli
                        config_data = tomli.load(f)
                    except ImportError:
                        raise ConfigurationError(
                            "TOML support requires 'tomli' package. Install with: pip install tomli",
                            config_file=str(config_path)
                        )
                else:
                    raise ConfigurationError(
                        f"Unsupported configuration file format: {config_path.suffix}",
                        config_file=str(config_path)
                    )
            
            # Expand environment variables
            config_data = cls._expand_env_vars(config_data)
            
            return cls(**config_data)
            
        except Exception as e:
            if isinstance(e, ConfigurationError):
                raise
            raise ConfigurationError(
                f"Failed to parse configuration file: {e}",
                config_file=str(config_path),
                cause=e
            )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'LibraryConfig':
        """
        Create configuration from dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            LibraryConfig instance
        """
        # Expand environment variables
        config_dict = cls._expand_env_vars(config_dict)
        return cls(**config_dict)
    
    @classmethod
    def from_env(cls, prefix: str = "TCLLM_") -> 'LibraryConfig':
        """
        Create configuration from environment variables.
        
        Args:
            prefix: Environment variable prefix
            
        Returns:
            LibraryConfig instance
        """
        config_dict = {}
        
        # Map environment variables to configuration
        env_mappings = {
            f"{prefix}ENVIRONMENT": "environment",
            f"{prefix}DEFAULT_PROVIDER": "default_provider",
            f"{prefix}DEFAULT_MODEL": "default_model",
            f"{prefix}CACHE_ENABLED": "cache.enabled",
            f"{prefix}CACHE_TYPE": "cache.cache_type",
            f"{prefix}REDIS_URL": "cache.redis_url",
            f"{prefix}LOG_LEVEL": "monitoring.log_level",
            f"{prefix}METRICS_ENABLED": "monitoring.enable_metrics",
            f"{prefix}MAX_CONCURRENT": "performance.max_concurrent_requests",
            f"{prefix}REQUEST_TIMEOUT": "performance.request_timeout_seconds",
        }
        
        for env_var, config_path in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                cls._set_nested_value(config_dict, config_path, value)
        
        return cls.from_dict(config_dict)
    
    @staticmethod
    def _expand_env_vars(data: Any) -> Any:
        """Recursively expand environment variables in configuration data."""
        if isinstance(data, dict):
            return {key: LibraryConfig._expand_env_vars(value) for key, value in data.items()}
        elif isinstance(data, list):
            return [LibraryConfig._expand_env_vars(item) for item in data]
        elif isinstance(data, str) and data.startswith("${") and data.endswith("}"):
            env_var = data[2:-1]
            default_value = None
            if ":" in env_var:
                env_var, default_value = env_var.split(":", 1)
            return os.getenv(env_var, default_value)
        else:
            return data
    
    @staticmethod
    def _set_nested_value(data: Dict[str, Any], path: str, value: Any):
        """Set nested dictionary value using dot notation."""
        keys = path.split('.')
        current = data
        
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Convert string values to appropriate types
        if isinstance(value, str):
            if value.lower() in ['true', 'false']:
                value = value.lower() == 'true'
            elif value.isdigit():
                value = int(value)
            elif '.' in value and value.replace('.', '').isdigit():
                value = float(value)
        
        current[keys[-1]] = value
    
    def get_provider_config(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get configuration for a specific provider."""
        return self.providers.get(provider_name)
    
    def get_workflow_config(self, workflow_name: str) -> Optional[WorkflowConfig]:
        """Get configuration for a specific workflow."""
        return self.workflows.get(workflow_name)
    
    def add_provider(self, name: str, config: ProviderConfig):
        """Add a provider configuration."""
        self.providers[name] = config
    
    def add_workflow(self, name: str, config: WorkflowConfig):
        """Add a workflow configuration."""
        self.workflows[name] = config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return self.dict()
    
    def to_yaml(self) -> str:
        """Convert configuration to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False)
    
    def to_json(self) -> str:
        """Convert configuration to JSON string."""
        return json.dumps(self.to_dict(), indent=2)
    
    def save_to_file(self, file_path: Union[str, Path], format: str = "yaml"):
        """
        Save configuration to file.
        
        Args:
            file_path: Path to save configuration
            format: File format (yaml, json)
        """
        file_path = Path(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            if format.lower() == 'yaml':
                yaml.dump(self.to_dict(), f, default_flow_style=False)
            elif format.lower() == 'json':
                json.dump(self.to_dict(), f, indent=2)
            else:
                raise ConfigurationError(f"Unsupported format: {format}")
    
    def validate(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            True if configuration is valid
            
        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Validate provider configurations
        for name, provider_config in self.providers.items():
            if not isinstance(provider_config, ProviderConfig):
                raise ConfigurationError(
                    f"Invalid provider configuration for '{name}'",
                    config_key=f"providers.{name}"
                )
        
        # Validate workflow configurations
        for name, workflow_config in self.workflows.items():
            if not isinstance(workflow_config, WorkflowConfig):
                raise ConfigurationError(
                    f"Invalid workflow configuration for '{name}'",
                    config_key=f"workflows.{name}"
                )
        
        return True
    
    def cleanup(self):
        """Cleanup configuration resources."""
        # Clear sensitive data
        for provider_config in self.providers.values():
            if hasattr(provider_config, 'api_key'):
                provider_config.api_key = None
