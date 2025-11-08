"""
Unit tests for core schemas module.

Tests all data models, validation, and serialization functionality.
"""

import pytest
from datetime import datetime
from uuid import UUID
from typing import Dict, Any

from evolvishub_text_classification_llm.core.schemas import (
    ProviderType, ProviderConfig, WorkflowConfig, WorkflowType,
    ClassificationInput, ClassificationResult, BatchProcessingResult
)
from evolvishub_text_classification_llm.core.exceptions import ValidationError


class TestProviderType:
    """Test ProviderType enum."""
    
    def test_provider_types(self):
        """Test all provider types are available."""
        assert ProviderType.OPENAI == "openai"
        assert ProviderType.ANTHROPIC == "anthropic"
        assert ProviderType.GOOGLE == "google"
        assert ProviderType.COHERE == "cohere"
        assert ProviderType.AZURE_OPENAI == "azure_openai"
        assert ProviderType.AWS_BEDROCK == "aws_bedrock"
        assert ProviderType.HUGGINGFACE == "huggingface"
        assert ProviderType.OLLAMA == "ollama"
    
    def test_provider_type_values(self):
        """Test provider type string values."""
        provider_values = [p.value for p in ProviderType]
        expected = [
            "openai", "anthropic", "google", "cohere",
            "azure_openai", "aws_bedrock", "huggingface", "ollama"
        ]
        assert set(provider_values) == set(expected)


class TestProviderConfig:
    """Test ProviderConfig model."""
    
    def test_valid_openai_config(self):
        """Test valid OpenAI provider configuration."""
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            api_key="test-key",
            temperature=0.1,
            max_tokens=500
        )
        
        assert config.provider_type == ProviderType.OPENAI
        assert config.model == "gpt-4"
        assert config.api_key == "test-key"
        assert config.temperature == 0.1
        assert config.max_tokens == 500
        assert config.timeout_seconds == 30  # default
    
    def test_valid_huggingface_config(self):
        """Test valid HuggingFace provider configuration."""
        config = ProviderConfig(
            provider_type=ProviderType.HUGGINGFACE,
            model="microsoft/DialoGPT-medium",
            device="cuda",
            quantization=True,
            cache_dir="./models"
        )
        
        assert config.provider_type == ProviderType.HUGGINGFACE
        assert config.model == "microsoft/DialoGPT-medium"
        assert config.device == "cuda"
        assert config.quantization is True
        assert config.cache_dir == "./models"
    
    def test_invalid_temperature(self):
        """Test invalid temperature validation."""
        with pytest.raises(ValidationError):
            ProviderConfig(
                provider_type=ProviderType.OPENAI,
                model="gpt-4",
                temperature=2.0  # Invalid: > 1.0
            )
    
    def test_invalid_max_tokens(self):
        """Test invalid max_tokens validation."""
        with pytest.raises(ValidationError):
            ProviderConfig(
                provider_type=ProviderType.OPENAI,
                model="gpt-4",
                max_tokens=0  # Invalid: <= 0
            )
    
    def test_config_serialization(self):
        """Test configuration serialization."""
        config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        config_dict = config.model_dump()
        assert config_dict["provider_type"] == "openai"
        assert config_dict["model"] == "gpt-4"
        assert config_dict["api_key"] == "test-key"
    
    def test_config_deserialization(self):
        """Test configuration deserialization."""
        config_dict = {
            "provider_type": "anthropic",
            "model": "claude-3-sonnet",
            "api_key": "test-key",
            "temperature": 0.2
        }
        
        config = ProviderConfig(**config_dict)
        assert config.provider_type == ProviderType.ANTHROPIC
        assert config.model == "claude-3-sonnet"
        assert config.temperature == 0.2


class TestWorkflowConfig:
    """Test WorkflowConfig model."""
    
    def test_valid_workflow_config(self):
        """Test valid workflow configuration."""
        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        config = WorkflowConfig(
            name="test_workflow",
            workflow_type=WorkflowType.CLASSIFICATION,
            primary_provider=provider_config,
            categories=["positive", "negative", "neutral"]
        )
        
        assert config.name == "test_workflow"
        assert config.workflow_type == WorkflowType.CLASSIFICATION
        assert config.primary_provider == provider_config
        assert config.categories == ["positive", "negative", "neutral"]
    
    def test_workflow_with_fallback_providers(self):
        """Test workflow with fallback providers."""
        primary = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        fallback = ProviderConfig(
            provider_type=ProviderType.ANTHROPIC,
            model="claude-3-sonnet",
            api_key="test-key-2"
        )
        
        config = WorkflowConfig(
            name="test_workflow",
            primary_provider=primary,
            fallback_providers=[fallback],
            enable_fallback=True
        )
        
        assert len(config.fallback_providers) == 1
        assert config.fallback_providers[0] == fallback
        assert config.enable_fallback is True
    
    def test_invalid_confidence_threshold(self):
        """Test invalid confidence threshold validation."""
        provider_config = ProviderConfig(
            provider_type=ProviderType.OPENAI,
            model="gpt-4",
            api_key="test-key"
        )
        
        with pytest.raises(ValidationError):
            WorkflowConfig(
                name="test_workflow",
                primary_provider=provider_config,
                min_confidence_threshold=1.5  # Invalid: > 1.0
            )


class TestClassificationInput:
    """Test ClassificationInput model."""
    
    def test_valid_input(self):
        """Test valid classification input."""
        input_data = ClassificationInput(
            text="This is a test message",
            metadata={"source": "test", "priority": "high"}
        )
        
        assert input_data.text == "This is a test message"
        assert input_data.metadata["source"] == "test"
        assert input_data.metadata["priority"] == "high"
        assert isinstance(input_data.id, UUID)
        assert isinstance(input_data.timestamp, datetime)
    
    def test_input_with_custom_id(self):
        """Test input with custom ID."""
        custom_id = UUID("12345678-1234-5678-9012-123456789012")
        input_data = ClassificationInput(
            id=custom_id,
            text="Test message"
        )
        
        assert input_data.id == custom_id
    
    def test_empty_text_validation(self):
        """Test empty text validation."""
        with pytest.raises(ValidationError):
            ClassificationInput(text="")
    
    def test_text_length_validation(self):
        """Test text length validation."""
        long_text = "x" * 100001  # Exceeds default max length
        
        with pytest.raises(ValidationError):
            ClassificationInput(text=long_text)


class TestClassificationResult:
    """Test ClassificationResult model."""
    
    def test_valid_result(self):
        """Test valid classification result."""
        result = ClassificationResult(
            input_id="test-id",
            primary_category="positive",
            categories={"positive": 0.9, "negative": 0.1},
            confidence=0.9,
            processing_time_ms=1500.0,
            model_version="gpt-4",
            provider="openai"
        )
        
        assert result.input_id == "test-id"
        assert result.primary_category == "positive"
        assert result.categories["positive"] == 0.9
        assert result.confidence == 0.9
        assert result.processing_time_ms == 1500.0
        assert result.model_version == "gpt-4"
        assert result.provider == "openai"
    
    def test_result_with_optional_fields(self):
        """Test result with optional fields."""
        result = ClassificationResult(
            input_id="test-id",
            primary_category="positive",
            categories={"positive": 0.9},
            confidence=0.9,
            sentiment={"polarity": 0.8, "subjectivity": 0.6},
            entities=["product", "service"],
            keywords=["great", "excellent"],
            reasoning="High positive sentiment detected",
            uncertainty_flags=["low_confidence_secondary"]
        )
        
        assert result.sentiment["polarity"] == 0.8
        assert result.entities == ["product", "service"]
        assert result.keywords == ["great", "excellent"]
        assert result.reasoning == "High positive sentiment detected"
        assert "low_confidence_secondary" in result.uncertainty_flags
    
    def test_invalid_confidence(self):
        """Test invalid confidence validation."""
        with pytest.raises(ValidationError):
            ClassificationResult(
                input_id="test-id",
                primary_category="positive",
                categories={"positive": 0.9},
                confidence=1.5  # Invalid: > 1.0
            )


class TestBatchProcessingResult:
    """Test BatchProcessingResult model."""
    
    def test_valid_batch_result(self):
        """Test valid batch processing result."""
        results = [
            ClassificationResult(
                input_id="1",
                primary_category="positive",
                categories={"positive": 0.9},
                confidence=0.9
            ),
            ClassificationResult(
                input_id="2",
                primary_category="negative",
                categories={"negative": 0.8},
                confidence=0.8
            )
        ]
        
        batch_result = BatchProcessingResult(
            total_items=2,
            successful_items=2,
            failed_items=0,
            results=results,
            errors=[],
            total_processing_time_ms=3000.0,
            average_processing_time_ms=1500.0,
            throughput_items_per_second=0.67,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        assert batch_result.total_items == 2
        assert batch_result.successful_items == 2
        assert batch_result.failed_items == 0
        assert len(batch_result.results) == 2
        assert batch_result.success_rate == 1.0
    
    def test_batch_result_with_errors(self):
        """Test batch result with errors."""
        batch_result = BatchProcessingResult(
            total_items=3,
            successful_items=2,
            failed_items=1,
            results=[],
            errors=[{"input_id": "3", "error": "Processing failed"}],
            total_processing_time_ms=3000.0,
            average_processing_time_ms=1500.0,
            throughput_items_per_second=1.0,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        assert batch_result.total_items == 3
        assert batch_result.successful_items == 2
        assert batch_result.failed_items == 1
        assert len(batch_result.errors) == 1
        assert batch_result.success_rate == 2/3
    
    def test_batch_statistics(self):
        """Test batch result statistics calculation."""
        batch_result = BatchProcessingResult(
            total_items=100,
            successful_items=95,
            failed_items=5,
            results=[],
            errors=[],
            total_processing_time_ms=60000.0,  # 1 minute
            average_processing_time_ms=600.0,
            throughput_items_per_second=1.67,
            started_at=datetime.utcnow(),
            completed_at=datetime.utcnow()
        )
        
        stats = batch_result.get_statistics()
        assert stats["success_rate"] == 0.95
        assert stats["error_rate"] == 0.05
        assert stats["total_items"] == 100
        assert stats["throughput_items_per_second"] == 1.67
