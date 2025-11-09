"""
Core data schemas for the text classification library.

This module defines the fundamental data structures used throughout the library,
including input/output schemas, configuration models, and result containers.
"""

from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from dataclasses import dataclass, field
from pydantic import BaseModel, Field, validator


class ProcessingStatus(str, Enum):
    """Status of processing operations."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProviderType(str, Enum):
    """Supported LLM provider types (10+ providers in v1.0.0)."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    COHERE = "cohere"
    MISTRAL = "mistral"          
    REPLICATE = "replicate"
    AZURE_OPENAI = "azure_openai"
    AWS_BEDROCK = "aws_bedrock"
    HUGGINGFACE = "huggingface"
    OLLAMA = "ollama"
    CUSTOM = "custom"


class WorkflowType(str, Enum):
    """Types of classification workflows."""
    CLASSIFICATION = "classification"
    SENTIMENT_ANALYSIS = "sentiment_analysis"
    ENTITY_EXTRACTION = "entity_extraction"
    SUMMARIZATION = "summarization"
    CUSTOM = "custom"


@dataclass
class ClassificationInput:
    """
    Standardized input for text classification.

    This schema provides a consistent interface between different data sources
    and the classification engine, enabling the system to work with various
    business data types.
    """
    text: str
    id: UUID = field(default_factory=uuid4)
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def __post_init__(self):
        """Validate input after initialization."""
        if not self.text or not self.text.strip():
            raise ValueError("Text content cannot be empty")
        
        if not isinstance(self.metadata, dict):
            raise ValueError("Metadata must be a dictionary")
        
        # Ensure ID is UUID type
        if isinstance(self.id, str):
            self.id = UUID(self.id)


class ClassificationResult(BaseModel):
    """
    Standardized output from text classification.
    
    This schema provides a consistent response format that can be extended
    for domain-specific use cases while maintaining core compatibility.
    """
    input_id: UUID = Field(..., description="Reference to the original input ID")
    
    # Core classification results
    primary_category: Optional[str] = Field(None, description="Primary classification category")
    categories: Dict[str, float] = Field(default_factory=dict, description="All categories with confidence scores")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Overall confidence score")
    
    # Additional analysis
    sentiment: Optional[Dict[str, Any]] = Field(None, description="Sentiment analysis results")
    entities: List[Dict[str, Any]] = Field(default_factory=list, description="Extracted entities")
    keywords: List[str] = Field(default_factory=list, description="Key terms identified")
    
    # Processing metadata
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")
    model_version: str = Field(..., description="Model/provider version used")
    provider: str = Field(..., description="LLM provider used")
    retry_count: int = Field(0, description="Number of retry attempts")
    
    # Quality indicators
    reasoning: Optional[str] = Field(None, description="Model's reasoning (if available)")
    uncertainty_flags: List[str] = Field(default_factory=list, description="Uncertainty indicators")
    
    # Timestamps and tracking
    created_at: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = Field(None, description="Request correlation ID")
    
    # Extensible metadata
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional result metadata")
    
    @validator('confidence')
    def validate_confidence(cls, v):
        """Ensure confidence is within valid range."""
        return max(0.0, min(1.0, v))
    
    def get_top_categories(self, n: int = 3) -> List[tuple]:
        """Get top N categories by confidence score."""
        sorted_categories = sorted(
            self.categories.items(), 
            key=lambda x: x[1], 
            reverse=True
        )
        return sorted_categories[:n]
    
    def is_high_confidence(self, threshold: float = 0.8) -> bool:
        """Check if result meets high confidence threshold."""
        return self.confidence >= threshold
    
    def has_uncertainty(self) -> bool:
        """Check if result has uncertainty flags."""
        return len(self.uncertainty_flags) > 0


class BatchProcessingResult(BaseModel):
    """Results from batch processing operations."""
    
    batch_id: UUID = Field(default_factory=uuid4, description="Unique batch identifier")
    total_items: int = Field(..., description="Total number of items processed")
    successful_items: int = Field(..., description="Number of successfully processed items")
    failed_items: int = Field(..., description="Number of failed items")
    
    # Individual results
    results: List[ClassificationResult] = Field(default_factory=list, description="Individual classification results")
    errors: List[Dict[str, Any]] = Field(default_factory=list, description="Processing errors")
    
    # Performance metrics
    total_processing_time_ms: float = Field(..., description="Total batch processing time")
    average_processing_time_ms: float = Field(..., description="Average time per item")
    throughput_items_per_second: float = Field(..., description="Processing throughput")
    
    # Resource usage
    peak_memory_mb: Optional[float] = Field(None, description="Peak memory usage during processing")
    cpu_usage_percent: Optional[float] = Field(None, description="Average CPU usage")
    
    # Provider statistics
    provider_usage: Dict[str, int] = Field(default_factory=dict, description="Usage count per provider")
    cache_hit_rate: float = Field(0.0, description="Cache hit rate percentage")
    
    # Quality metrics
    average_confidence: float = Field(0.0, description="Average confidence across all results")
    high_confidence_count: int = Field(0, description="Number of high-confidence results")
    
    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(None)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_items == 0:
            return 0.0
        return (self.successful_items / self.total_items) * 100
    
    @property
    def duration_seconds(self) -> float:
        """Calculate total duration in seconds."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return 0.0
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive batch statistics."""
        return {
            "batch_id": str(self.batch_id),
            "total_items": self.total_items,
            "success_rate": self.success_rate,
            "average_processing_time_ms": self.average_processing_time_ms,
            "throughput_items_per_second": self.throughput_items_per_second,
            "cache_hit_rate": self.cache_hit_rate,
            "average_confidence": self.average_confidence,
            "provider_usage": self.provider_usage,
            "duration_seconds": self.duration_seconds
        }


class ProviderConfig(BaseModel):
    """Configuration for LLM providers."""
    
    provider_type: ProviderType = Field(..., description="Type of LLM provider")
    model: str = Field(..., description="Model identifier")
    
    # Authentication
    api_key: Optional[str] = Field(None, description="API key for cloud providers")
    api_base: Optional[str] = Field(None, description="Custom API base URL")
    organization: Optional[str] = Field(None, description="Organization ID")
    
    # Model parameters
    temperature: float = Field(0.1, ge=0.0, le=2.0, description="Sampling temperature")
    max_tokens: int = Field(500, ge=1, description="Maximum tokens to generate")
    top_p: float = Field(0.9, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    top_k: int = Field(50, ge=1, description="Top-k sampling parameter")
    
    # Performance settings
    timeout_seconds: int = Field(30, ge=1, description="Request timeout")
    max_retries: int = Field(3, ge=0, description="Maximum retry attempts")
    retry_delay_seconds: float = Field(1.0, ge=0.0, description="Delay between retries")
    
    # Local model settings (for HuggingFace, Ollama, etc.)
    device: str = Field("auto", description="Device for local models")
    quantization: bool = Field(True, description="Enable model quantization")
    cache_dir: Optional[str] = Field(None, description="Model cache directory")
    
    # Rate limiting
    requests_per_minute: Optional[int] = Field(None, description="Rate limit for requests")
    tokens_per_minute: Optional[int] = Field(None, description="Rate limit for tokens")
    
    # Cost optimization
    cost_per_token: Optional[float] = Field(None, description="Cost per token for optimization")
    priority: int = Field(1, description="Provider priority (1=highest)")
    
    # Additional configuration
    extra_params: Dict[str, Any] = Field(default_factory=dict, description="Provider-specific parameters")


class WorkflowConfig(BaseModel):
    """Configuration for classification workflows."""
    
    workflow_type: WorkflowType = Field(WorkflowType.CLASSIFICATION, description="Type of workflow")
    name: str = Field(..., description="Workflow name")
    description: Optional[str] = Field(None, description="Workflow description")
    
    # Provider configuration
    primary_provider: ProviderConfig = Field(..., description="Primary LLM provider")
    fallback_providers: List[ProviderConfig] = Field(default_factory=list, description="Fallback providers")
    
    # Workflow behavior
    enable_fallback: bool = Field(True, description="Enable provider fallback")
    enable_caching: bool = Field(True, description="Enable response caching")
    enable_validation: bool = Field(True, description="Enable response validation")
    
    # Quality thresholds
    min_confidence_threshold: float = Field(0.5, description="Minimum confidence threshold")
    high_confidence_threshold: float = Field(0.8, description="High confidence threshold")
    
    # Processing limits
    max_text_length: int = Field(10000, description="Maximum input text length")
    batch_size: int = Field(100, description="Default batch size")
    max_concurrent: int = Field(10, description="Maximum concurrent requests")
    
    # Prompt configuration
    system_prompt: Optional[str] = Field(None, description="System prompt template")
    user_prompt_template: str = Field("{text}", description="User prompt template")
    response_format: str = Field("json", description="Expected response format")
    
    # Categories and labels
    categories: List[str] = Field(default_factory=list, description="Classification categories")
    category_descriptions: Dict[str, str] = Field(default_factory=dict, description="Category descriptions")
    
    # Monitoring and logging
    enable_monitoring: bool = Field(True, description="Enable monitoring")
    log_level: str = Field("INFO", description="Logging level")
    correlation_id_header: str = Field("X-Correlation-ID", description="Correlation ID header")
    
    # Extensible configuration
    custom_config: Dict[str, Any] = Field(default_factory=dict, description="Custom configuration parameters")
    
    def get_provider_by_priority(self) -> List[ProviderConfig]:
        """Get all providers sorted by priority."""
        all_providers = [self.primary_provider] + self.fallback_providers
        return sorted(all_providers, key=lambda p: p.priority)
    
    def validate_categories(self) -> bool:
        """Validate that categories are properly configured."""
        return len(self.categories) > 0
