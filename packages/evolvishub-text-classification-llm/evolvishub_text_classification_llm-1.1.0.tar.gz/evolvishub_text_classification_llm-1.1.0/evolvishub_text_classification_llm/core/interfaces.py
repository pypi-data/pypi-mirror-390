"""
Core interfaces for the text classification library.

This module defines the abstract base classes and interfaces that enable
pluggable components for different LLM providers, data sources, workflows,
and storage backends.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, AsyncGenerator, Union
from datetime import datetime

from .schemas import (
    ClassificationInput, 
    ClassificationResult, 
    BatchProcessingResult,
    ProviderConfig, 
    WorkflowConfig,
    ProcessingStatus
)


class ILLMProvider(ABC):
    """
    Abstract interface for LLM providers.
    
    This interface enables the system to work with different LLM providers
    (OpenAI, Anthropic, Google, etc.) through a unified API.
    """
    
    def __init__(self, config: ProviderConfig):
        """Initialize the provider with configuration."""
        self.config = config
        self._initialized = False
    
    @abstractmethod
    async def initialize(self) -> bool:
        """
        Initialize the provider (load models, authenticate, etc.).
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def generate(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> str:
        """
        Generate text response from messages.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text response
            
        Raises:
            ProviderError: If generation fails
        """
        pass
    
    @abstractmethod
    async def generate_stream(
        self, 
        messages: List[Dict[str, str]], 
        **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        Generate streaming text response.
        
        Args:
            messages: List of message dictionaries
            **kwargs: Additional generation parameters
            
        Yields:
            Text chunks as they are generated
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> Dict[str, Any]:
        """
        Check provider health and availability.
        
        Returns:
            Dictionary with health status information
        """
        pass
    
    @abstractmethod
    async def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for the provider.
        
        Returns:
            Dictionary with usage metrics (tokens, requests, costs, etc.)
        """
        pass
    
    @abstractmethod
    async def estimate_cost(self, text: str) -> float:
        """
        Estimate the cost for processing given text.
        
        Args:
            text: Input text to estimate cost for
            
        Returns:
            Estimated cost in USD
        """
        pass
    
    @abstractmethod
    async def cleanup(self):
        """Cleanup provider resources."""
        pass
    
    @property
    def is_initialized(self) -> bool:
        """Check if provider is initialized."""
        return self._initialized
    
    @property
    def provider_type(self) -> str:
        """Get provider type identifier."""
        return self.config.provider_type.value
    
    @property
    def model_name(self) -> str:
        """Get model name."""
        return self.config.model


class IDataFetcher(ABC):
    """
    Abstract interface for data source connectors.
    
    This interface enables the system to connect to different data sources
    (databases, files, APIs, streams) and fetch data for classification.
    """
    
    @abstractmethod
    async def extract(
        self, 
        limit: Optional[int] = None, 
        offset: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract raw data from the source.
        
        Args:
            limit: Maximum number of records to fetch
            offset: Number of records to skip
            filters: Additional filtering criteria
            
        Returns:
            List of raw data records
        """
        pass
    
    @abstractmethod
    async def extract_stream(
        self,
        batch_size: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> AsyncGenerator[List[Dict[str, Any]], None]:
        """
        Extract data as a stream for large datasets.
        
        Args:
            batch_size: Size of each batch
            filters: Additional filtering criteria
            
        Yields:
            Batches of raw data records
        """
        pass
    
    @abstractmethod
    async def prepare(self, raw_data: List[Dict[str, Any]]) -> List[ClassificationInput]:
        """
        Transform raw data to standardized classification input.
        
        Args:
            raw_data: Raw data records from source
            
        Returns:
            List of ClassificationInput objects
        """
        pass
    
    @abstractmethod
    async def mark_processed(
        self, 
        record_ids: List[str], 
        status: ProcessingStatus = ProcessingStatus.COMPLETED
    ) -> bool:
        """
        Mark records as processed in the data source.
        
        Args:
            record_ids: List of record IDs to mark
            status: Processing status to set
            
        Returns:
            True if all records were successfully marked
        """
        pass
    
    @abstractmethod
    async def get_processing_stats(self) -> Dict[str, Any]:
        """
        Get processing statistics from the data source.
        
        Returns:
            Dictionary with processing statistics
        """
        pass


class IResultProcessor(ABC):
    """
    Abstract interface for processing and storing classification results.
    
    This interface enables different result processing strategies
    (database storage, file export, API forwarding, etc.).
    """
    
    @abstractmethod
    async def store_results(self, results: List[ClassificationResult]) -> bool:
        """
        Store classification results.
        
        Args:
            results: List of classification results to store
            
        Returns:
            True if all results were stored successfully
        """
        pass
    
    @abstractmethod
    async def store_batch_result(self, batch_result: BatchProcessingResult) -> bool:
        """
        Store batch processing result.
        
        Args:
            batch_result: Batch processing result to store
            
        Returns:
            True if batch result was stored successfully
        """
        pass
    
    @abstractmethod
    async def get_results(
        self,
        input_ids: Optional[List[str]] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        limit: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ClassificationResult]:
        """
        Retrieve stored classification results.
        
        Args:
            input_ids: Specific input IDs to retrieve
            date_from: Start date for filtering
            date_to: End date for filtering
            limit: Maximum number of results
            filters: Additional filtering criteria
            
        Returns:
            List of classification results
        """
        pass
    
    @abstractmethod
    async def get_analytics(
        self,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Get analytics and aggregated statistics.
        
        Args:
            date_from: Start date for analytics
            date_to: End date for analytics
            
        Returns:
            Dictionary with analytics data
        """
        pass


class IWorkflowEngine(ABC):
    """
    Abstract interface for workflow management.
    
    This interface enables different workflow implementations
    (LangGraph, custom workflows, etc.) to be used interchangeably.
    """
    
    def __init__(self, config: WorkflowConfig):
        """Initialize workflow with configuration."""
        self.config = config
    
    @abstractmethod
    async def execute(self, input_data: ClassificationInput) -> ClassificationResult:
        """
        Execute workflow for a single input.
        
        Args:
            input_data: Input to process
            
        Returns:
            Classification result
        """
        pass
    
    @abstractmethod
    async def execute_batch(
        self, 
        input_batch: List[ClassificationInput]
    ) -> BatchProcessingResult:
        """
        Execute workflow for a batch of inputs.
        
        Args:
            input_batch: List of inputs to process
            
        Returns:
            Batch processing result
        """
        pass
    
    @abstractmethod
    async def validate_config(self) -> bool:
        """
        Validate workflow configuration.
        
        Returns:
            True if configuration is valid
        """
        pass
    
    @abstractmethod
    async def get_workflow_info(self) -> Dict[str, Any]:
        """
        Get information about the workflow.
        
        Returns:
            Dictionary with workflow metadata
        """
        pass


class IProviderFactory(ABC):
    """
    Abstract interface for LLM provider factories.
    
    This interface enables dynamic provider creation and registration.
    """
    
    @abstractmethod
    def create_provider(self, config: ProviderConfig) -> ILLMProvider:
        """
        Create an LLM provider instance.
        
        Args:
            config: Provider configuration
            
        Returns:
            Configured provider instance
        """
        pass
    
    @abstractmethod
    def register_provider(self, provider_type: str, provider_class: type):
        """
        Register a new provider type.
        
        Args:
            provider_type: Provider type identifier
            provider_class: Provider implementation class
        """
        pass
    
    @abstractmethod
    def get_supported_providers(self) -> List[str]:
        """
        Get list of supported provider types.
        
        Returns:
            List of provider type identifiers
        """
        pass


class ICacheManager(ABC):
    """
    Abstract interface for caching implementations.
    
    This interface enables different caching strategies
    (memory, Redis, disk, etc.) to be used interchangeably.
    """
    
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found
        """
        pass
    
    @abstractmethod
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl_seconds: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl_seconds: Time to live in seconds
            
        Returns:
            True if value was cached successfully
        """
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if value was deleted
        """
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """
        Clear all cached values.
        
        Returns:
            True if cache was cleared
        """
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics
        """
        pass


class IMonitoringCollector(ABC):
    """
    Abstract interface for monitoring and metrics collection.
    
    This interface enables different monitoring implementations
    (Prometheus, custom metrics, etc.) to be used.
    """
    
    @abstractmethod
    async def record_request(
        self, 
        provider: str, 
        model: str, 
        duration_ms: float,
        success: bool
    ):
        """Record a classification request."""
        pass
    
    @abstractmethod
    async def record_batch(
        self, 
        batch_size: int, 
        duration_ms: float, 
        success_rate: float
    ):
        """Record a batch processing operation."""
        pass
    
    @abstractmethod
    async def record_error(self, error_type: str, provider: str):
        """Record an error occurrence."""
        pass
    
    @abstractmethod
    async def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics."""
        pass
