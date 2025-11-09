"""
Unit tests for configuration system.

Tests configuration loading, validation, and environment variable expansion.
"""

import pytest
import os
import tempfile
import yaml
import json
from pathlib import Path
from unittest.mock import patch

from evolvishub_text_classification_llm.core.config import (
    LibraryConfig, CacheConfig, MonitoringConfig, SecurityConfig, PerformanceConfig
)
from evolvishub_text_classification_llm.core.schemas import ProviderConfig, ProviderType
from evolvishub_text_classification_llm.core.exceptions import ConfigurationError


class TestCacheConfig:
    """Test CacheConfig model."""
    
    def test_default_cache_config(self):
        """Test default cache configuration."""
        config = CacheConfig()
        
        assert config.enabled is True
        assert config.cache_type == "memory"
        assert config.max_memory_items == 1000
        assert config.memory_ttl_seconds == 3600
        assert config.enable_deduplication is True
        assert config.similarity_threshold == 0.95
    
    def test_redis_cache_config(self):
        """Test Redis cache configuration."""
        config = CacheConfig(
            cache_type="redis",
            redis_url="redis://localhost:6379",
            redis_db=1,
            redis_ttl_seconds=7200
        )
        
        assert config.cache_type == "redis"
        assert config.redis_url == "redis://localhost:6379"
        assert config.redis_db == 1
        assert config.redis_ttl_seconds == 7200
    
    def test_disk_cache_config(self):
        """Test disk cache configuration."""
        config = CacheConfig(
            cache_type="disk",
            disk_cache_dir="/tmp/cache",
            disk_max_size_mb=2000,
            disk_ttl_seconds=86400
        )
        
        assert config.cache_type == "disk"
        assert config.disk_cache_dir == "/tmp/cache"
        assert config.disk_max_size_mb == 2000
        assert config.disk_ttl_seconds == 86400


class TestMonitoringConfig:
    """Test MonitoringConfig model."""
    
    def test_default_monitoring_config(self):
        """Test default monitoring configuration."""
        config = MonitoringConfig()
        
        assert config.enabled is True
        assert config.enable_metrics is True
        assert config.metrics_port == 9090
        assert config.log_level == "INFO"
        assert config.log_format == "structured"
        assert config.enable_correlation_id is True
        assert config.enable_performance_tracking is True
    
    def test_custom_monitoring_config(self):
        """Test custom monitoring configuration."""
        config = MonitoringConfig(
            log_level="DEBUG",
            log_format="plain",
            log_file="/var/log/app.log",
            metrics_port=9091,
            health_check_interval=60,
            slow_request_threshold_ms=10000.0
        )
        
        assert config.log_level == "DEBUG"
        assert config.log_format == "plain"
        assert config.log_file == "/var/log/app.log"
        assert config.metrics_port == 9091
        assert config.health_check_interval == 60
        assert config.slow_request_threshold_ms == 10000.0


class TestSecurityConfig:
    """Test SecurityConfig model."""
    
    def test_default_security_config(self):
        """Test default security configuration."""
        config = SecurityConfig()
        
        assert config.enable_input_sanitization is True
        assert config.max_input_length == 100000
        assert config.enable_pii_detection is True
        assert config.pii_redaction_mode == "mask"
        assert config.enable_rate_limiting is True
        assert config.requests_per_minute == 100
    
    def test_custom_security_config(self):
        """Test custom security configuration."""
        config = SecurityConfig(
            max_input_length=50000,
            blocked_patterns=["spam", "abuse"],
            pii_redaction_mode="remove",
            requests_per_minute=200,
            require_api_key=True,
            api_key_header="Authorization"
        )
        
        assert config.max_input_length == 50000
        assert config.blocked_patterns == ["spam", "abuse"]
        assert config.pii_redaction_mode == "remove"
        assert config.requests_per_minute == 200
        assert config.require_api_key is True
        assert config.api_key_header == "Authorization"


class TestPerformanceConfig:
    """Test PerformanceConfig model."""
    
    def test_default_performance_config(self):
        """Test default performance configuration."""
        config = PerformanceConfig()
        
        assert config.max_concurrent_requests == 50
        assert config.request_timeout_seconds == 30
        assert config.max_memory_usage_mb == 4000
        assert config.enable_provider_fallback is True
        assert config.default_batch_size == 100
        assert config.max_batch_size == 1000
    
    def test_custom_performance_config(self):
        """Test custom performance configuration."""
        config = PerformanceConfig(
            max_concurrent_requests=100,
            request_timeout_seconds=60,
            max_memory_usage_mb=8000,
            default_batch_size=200,
            batch_processing_mode="sequential"
        )
        
        assert config.max_concurrent_requests == 100
        assert config.request_timeout_seconds == 60
        assert config.max_memory_usage_mb == 8000
        assert config.default_batch_size == 200
        assert config.batch_processing_mode == "sequential"


class TestLibraryConfig:
    """Test LibraryConfig model."""
    
    def test_default_library_config(self):
        """Test default library configuration."""
        config = LibraryConfig()
        
        assert config.library_name == "evolvishub-text-classification-llm"
        assert config.version == "1.0.0"
        assert config.environment == "development"
        assert config.default_provider == "openai"
        assert config.default_model == "gpt-3.5-turbo"
        assert isinstance(config.cache, CacheConfig)
        assert isinstance(config.monitoring, MonitoringConfig)
        assert isinstance(config.security, SecurityConfig)
        assert isinstance(config.performance, PerformanceConfig)
    
    def test_custom_library_config(self):
        """Test custom library configuration."""
        cache_config = CacheConfig(cache_type="redis")
        monitoring_config = MonitoringConfig(log_level="DEBUG")
        
        config = LibraryConfig(
            library_name="custom-classifier",
            environment="production",
            default_provider="anthropic",
            cache=cache_config,
            monitoring=monitoring_config
        )
        
        assert config.library_name == "custom-classifier"
        assert config.environment == "production"
        assert config.default_provider == "anthropic"
        assert config.cache.cache_type == "redis"
        assert config.monitoring.log_level == "DEBUG"
    
    def test_environment_validation(self):
        """Test environment validation."""
        # Valid environments
        for env in ["development", "staging", "production", "test"]:
            config = LibraryConfig(environment=env)
            assert config.environment == env
        
        # Invalid environment
        with pytest.raises(ValueError):
            LibraryConfig(environment="invalid")
    
    def test_provider_validation(self):
        """Test default provider validation."""
        # Valid providers
        for provider in ProviderType:
            config = LibraryConfig(default_provider=provider.value)
            assert config.default_provider == provider.value
        
        # Invalid provider
        with pytest.raises(ValueError):
            LibraryConfig(default_provider="invalid_provider")


class TestConfigurationLoading:
    """Test configuration loading from files and environment."""
    
    def test_load_from_yaml_file(self):
        """Test loading configuration from YAML file."""
        config_data = {
            "library_name": "test-classifier",
            "environment": "test",
            "default_provider": "anthropic",
            "cache": {
                "enabled": True,
                "cache_type": "redis",
                "redis_url": "redis://localhost:6379"
            },
            "providers": {
                "anthropic": {
                    "provider_type": "anthropic",
                    "model": "claude-3-sonnet",
                    "api_key": "test-key"
                }
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            config = LibraryConfig.from_file(config_path)
            
            assert config.library_name == "test-classifier"
            assert config.environment == "test"
            assert config.default_provider == "anthropic"
            assert config.cache.cache_type == "redis"
            assert "anthropic" in config.providers
        finally:
            os.unlink(config_path)
    
    def test_load_from_json_file(self):
        """Test loading configuration from JSON file."""
        config_data = {
            "library_name": "test-classifier",
            "environment": "test",
            "monitoring": {
                "log_level": "DEBUG",
                "enable_metrics": False
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(config_data, f)
            config_path = f.name
        
        try:
            config = LibraryConfig.from_file(config_path)
            
            assert config.library_name == "test-classifier"
            assert config.monitoring.log_level == "DEBUG"
            assert config.monitoring.enable_metrics is False
        finally:
            os.unlink(config_path)
    
    def test_load_nonexistent_file(self):
        """Test loading from nonexistent file."""
        with pytest.raises(ConfigurationError) as exc_info:
            LibraryConfig.from_file("nonexistent.yaml")
        
        assert "Configuration file not found" in str(exc_info.value)
    
    def test_load_invalid_yaml(self):
        """Test loading invalid YAML file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            config_path = f.name
        
        try:
            with pytest.raises(ConfigurationError) as exc_info:
                LibraryConfig.from_file(config_path)
            
            assert "Failed to parse configuration file" in str(exc_info.value)
        finally:
            os.unlink(config_path)
    
    def test_from_dict(self):
        """Test creating configuration from dictionary."""
        config_dict = {
            "library_name": "dict-classifier",
            "environment": "test",
            "default_provider": "openai",
            "cache": {
                "cache_type": "memory",
                "max_memory_items": 500
            }
        }
        
        config = LibraryConfig.from_dict(config_dict)
        
        assert config.library_name == "dict-classifier"
        assert config.environment == "test"
        assert config.cache.max_memory_items == 500
    
    @patch.dict(os.environ, {
        "TCLLM_ENVIRONMENT": "production",
        "TCLLM_DEFAULT_PROVIDER": "anthropic",
        "TCLLM_CACHE_ENABLED": "false",
        "TCLLM_LOG_LEVEL": "ERROR",
        "TCLLM_MAX_CONCURRENT": "75"
    })
    def test_from_env(self):
        """Test creating configuration from environment variables."""
        config = LibraryConfig.from_env()
        
        assert config.environment == "production"
        assert config.default_provider == "anthropic"
        # Note: Environment variable mapping would need to be implemented
        # This test shows the expected interface
    
    def test_environment_variable_expansion(self):
        """Test environment variable expansion in configuration."""
        with patch.dict(os.environ, {"TEST_API_KEY": "secret-key-123"}):
            config_data = {
                "providers": {
                    "openai": {
                        "provider_type": "openai",
                        "model": "gpt-4",
                        "api_key": "${TEST_API_KEY}"
                    }
                }
            }
            
            expanded = LibraryConfig._expand_env_vars(config_data)
            
            assert expanded["providers"]["openai"]["api_key"] == "secret-key-123"
    
    def test_environment_variable_with_default(self):
        """Test environment variable expansion with default value."""
        config_data = {
            "cache": {
                "redis_url": "${REDIS_URL:redis://localhost:6379}"
            }
        }
        
        expanded = LibraryConfig._expand_env_vars(config_data)
        
        assert expanded["cache"]["redis_url"] == "redis://localhost:6379"
    
    def test_nested_value_setting(self):
        """Test setting nested dictionary values."""
        data = {}
        LibraryConfig._set_nested_value(data, "cache.redis_url", "redis://test:6379")
        LibraryConfig._set_nested_value(data, "monitoring.log_level", "DEBUG")
        
        assert data["cache"]["redis_url"] == "redis://test:6379"
        assert data["monitoring"]["log_level"] == "DEBUG"
    
    def test_type_conversion(self):
        """Test automatic type conversion for environment variables."""
        data = {}
        LibraryConfig._set_nested_value(data, "cache.enabled", "true")
        LibraryConfig._set_nested_value(data, "cache.max_items", "1000")
        LibraryConfig._set_nested_value(data, "cache.ttl", "3600.5")
        
        assert data["cache"]["enabled"] is True
        assert data["cache"]["max_items"] == 1000
        assert data["cache"]["ttl"] == 3600.5


class TestConfigurationMethods:
    """Test configuration utility methods."""
    
    def test_get_provider_config(self):
        """Test getting provider configuration."""
        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        config = LibraryConfig()
        config.add_provider("openai", provider_config)
        
        retrieved = config.get_provider_config("openai")
        assert retrieved == provider_config
        
        # Test nonexistent provider
        assert config.get_provider_config("nonexistent") is None
    
    def test_to_dict(self):
        """Test converting configuration to dictionary."""
        config = LibraryConfig(
            library_name="test-lib",
            environment="test"
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["library_name"] == "test-lib"
        assert config_dict["environment"] == "test"
        assert "cache" in config_dict
        assert "monitoring" in config_dict
    
    def test_to_yaml(self):
        """Test converting configuration to YAML."""
        config = LibraryConfig(library_name="test-lib")
        yaml_str = config.to_yaml()
        
        assert "library_name: test-lib" in yaml_str
        assert "cache:" in yaml_str
        assert "monitoring:" in yaml_str
    
    def test_to_json(self):
        """Test converting configuration to JSON."""
        config = LibraryConfig(library_name="test-lib")
        json_str = config.to_json()
        
        parsed = json.loads(json_str)
        assert parsed["library_name"] == "test-lib"
        assert "cache" in parsed
        assert "monitoring" in parsed
    
    def test_save_to_file(self):
        """Test saving configuration to file."""
        config = LibraryConfig(library_name="test-lib")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            config_path = f.name
        
        try:
            config.save_to_file(config_path, format="yaml")
            
            # Verify file was created and contains expected content
            with open(config_path, 'r') as f:
                content = f.read()
                assert "library_name: test-lib" in content
        finally:
            os.unlink(config_path)
    
    def test_validate(self):
        """Test configuration validation."""
        config = LibraryConfig()
        
        # Valid configuration should pass
        assert config.validate() is True
        
        # Add invalid provider config
        config.providers["invalid"] = "not a provider config"
        
        with pytest.raises(ConfigurationError):
            config.validate()
    
    def test_cleanup(self):
        """Test configuration cleanup."""
        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            api_key="secret-key"
        )
        
        config = LibraryConfig()
        config.add_provider("openai", provider_config)
        
        # Verify API key is present
        assert config.providers["openai"].api_key == "secret-key"
        
        # Cleanup should remove sensitive data
        config.cleanup()
        
        # API key should be cleared
        assert config.providers["openai"].api_key is None
