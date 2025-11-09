"""
Custom exceptions for the text classification library.

This module defines specific exceptions for different error scenarios
in the text classification pipeline, enabling precise error handling
and debugging.
"""

from typing import Optional, Dict, Any, List


class TextClassificationError(Exception):
    """
    Base exception for all text classification library errors.
    
    This is the root exception class that all other library exceptions
    inherit from, enabling catch-all error handling when needed.
    """
    
    def __init__(
        self, 
        message: str, 
        error_code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        cause: Optional[Exception] = None
    ):
        """
        Initialize the exception.
        
        Args:
            message: Human-readable error message
            error_code: Machine-readable error code
            details: Additional error details
            cause: Original exception that caused this error
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code or self.__class__.__name__.upper()
        self.details = details or {}
        self.cause = cause
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert exception to dictionary format."""
        return {
            "error_type": self.__class__.__name__,
            "error_code": self.error_code,
            "message": self.message,
            "details": self.details,
            "cause": str(self.cause) if self.cause else None
        }


class ProviderError(TextClassificationError):
    """
    Raised when LLM provider operations fail.
    
    This includes authentication failures, API errors, model loading issues,
    rate limiting, and other provider-specific problems.
    """
    
    def __init__(
        self, 
        message: str, 
        provider: Optional[str] = None,
        model: Optional[str] = None,
        status_code: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize provider error.
        
        Args:
            message: Error message
            provider: Provider name that failed
            model: Model name that failed
            status_code: HTTP status code (for API errors)
            **kwargs: Additional error details
        """
        details = kwargs.get('details', {})
        if provider:
            details['provider'] = provider
        if model:
            details['model'] = model
        if status_code:
            details['status_code'] = status_code
        
        super().__init__(message, details=details, **kwargs)
        self.provider = provider
        self.model = model
        self.status_code = status_code


class AuthenticationError(ProviderError):
    """Raised when provider authentication fails."""
    
    def __init__(self, message: str, provider: Optional[str] = None, **kwargs):
        super().__init__(
            message, 
            provider=provider, 
            error_code="AUTHENTICATION_ERROR",
            **kwargs
        )


class RateLimitError(ProviderError):
    """Raised when provider rate limits are exceeded."""
    
    def __init__(
        self, 
        message: str, 
        provider: Optional[str] = None,
        retry_after: Optional[int] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if retry_after:
            details['retry_after_seconds'] = retry_after
        
        super().__init__(
            message, 
            provider=provider, 
            error_code="RATE_LIMIT_ERROR",
            details=details,
            **kwargs
        )
        self.retry_after = retry_after


class ModelLoadError(ProviderError):
    """Raised when model loading or initialization fails."""
    
    def __init__(
        self, 
        message: str, 
        provider: Optional[str] = None,
        model: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message, 
            provider=provider, 
            model=model,
            error_code="MODEL_LOAD_ERROR",
            **kwargs
        )


class WorkflowError(TextClassificationError):
    """
    Raised when workflow execution fails.
    
    This includes workflow configuration errors, execution failures,
    validation errors, and workflow state management issues.
    """
    
    def __init__(
        self, 
        message: str, 
        workflow_name: Optional[str] = None,
        step_name: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if workflow_name:
            details['workflow_name'] = workflow_name
        if step_name:
            details['step_name'] = step_name
        
        super().__init__(message, details=details, **kwargs)
        self.workflow_name = workflow_name
        self.step_name = step_name


class ValidationError(TextClassificationError):
    """
    Raised when input or output validation fails.
    
    This includes schema validation errors, data format issues,
    and constraint violations.
    """
    
    def __init__(
        self, 
        message: str, 
        field_name: Optional[str] = None,
        validation_errors: Optional[List[str]] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if field_name:
            details['field_name'] = field_name
        if validation_errors:
            details['validation_errors'] = validation_errors
        
        super().__init__(
            message, 
            error_code="VALIDATION_ERROR",
            details=details,
            **kwargs
        )
        self.field_name = field_name
        self.validation_errors = validation_errors or []


class ConfigurationError(TextClassificationError):
    """
    Raised when configuration is invalid or missing.
    
    This includes missing required configuration, invalid values,
    and configuration file parsing errors.
    """
    
    def __init__(
        self, 
        message: str, 
        config_key: Optional[str] = None,
        config_file: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if config_key:
            details['config_key'] = config_key
        if config_file:
            details['config_file'] = config_file
        
        super().__init__(
            message, 
            error_code="CONFIGURATION_ERROR",
            details=details,
            **kwargs
        )
        self.config_key = config_key
        self.config_file = config_file


class DataSourceError(TextClassificationError):
    """
    Raised when data source operations fail.
    
    This includes database connection errors, file access issues,
    API connectivity problems, and data extraction failures.
    """
    
    def __init__(
        self, 
        message: str, 
        source_type: Optional[str] = None,
        source_location: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if source_type:
            details['source_type'] = source_type
        if source_location:
            details['source_location'] = source_location
        
        super().__init__(
            message, 
            error_code="DATA_SOURCE_ERROR",
            details=details,
            **kwargs
        )
        self.source_type = source_type
        self.source_location = source_location


class ProcessingError(TextClassificationError):
    """
    Raised when text processing operations fail.
    
    This includes text preprocessing errors, classification failures,
    and result processing issues.
    """
    
    def __init__(
        self, 
        message: str, 
        processing_stage: Optional[str] = None,
        input_id: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if processing_stage:
            details['processing_stage'] = processing_stage
        if input_id:
            details['input_id'] = input_id
        
        super().__init__(
            message, 
            error_code="PROCESSING_ERROR",
            details=details,
            **kwargs
        )
        self.processing_stage = processing_stage
        self.input_id = input_id


class CacheError(TextClassificationError):
    """
    Raised when caching operations fail.
    
    This includes cache connection errors, serialization issues,
    and cache storage failures.
    """
    
    def __init__(
        self, 
        message: str, 
        cache_type: Optional[str] = None,
        cache_key: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if cache_type:
            details['cache_type'] = cache_type
        if cache_key:
            details['cache_key'] = cache_key
        
        super().__init__(
            message, 
            error_code="CACHE_ERROR",
            details=details,
            **kwargs
        )
        self.cache_type = cache_type
        self.cache_key = cache_key


class SecurityError(TextClassificationError):
    """
    Raised when security violations occur.
    
    This includes unauthorized access, input sanitization failures,
    and security policy violations.
    """
    
    def __init__(
        self, 
        message: str, 
        security_violation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if security_violation:
            details['security_violation'] = security_violation
        
        super().__init__(
            message, 
            error_code="SECURITY_ERROR",
            details=details,
            **kwargs
        )
        self.security_violation = security_violation


class ResourceError(TextClassificationError):
    """
    Raised when resource limits are exceeded.
    
    This includes memory limits, timeout errors, and resource
    exhaustion scenarios.
    """
    
    def __init__(
        self, 
        message: str, 
        resource_type: Optional[str] = None,
        limit_exceeded: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if resource_type:
            details['resource_type'] = resource_type
        if limit_exceeded:
            details['limit_exceeded'] = limit_exceeded
        
        super().__init__(
            message, 
            error_code="RESOURCE_ERROR",
            details=details,
            **kwargs
        )
        self.resource_type = resource_type
        self.limit_exceeded = limit_exceeded


class TimeoutError(ResourceError):
    """Raised when operations exceed timeout limits."""
    
    def __init__(
        self, 
        message: str, 
        timeout_seconds: Optional[float] = None,
        operation: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get('details', {})
        if timeout_seconds:
            details['timeout_seconds'] = timeout_seconds
        if operation:
            details['operation'] = operation
        
        super().__init__(
            message, 
            resource_type="timeout",
            limit_exceeded=f"{timeout_seconds}s" if timeout_seconds else None,
            error_code="TIMEOUT_ERROR",
            details=details,
            **kwargs
        )
        self.timeout_seconds = timeout_seconds
        self.operation = operation


class StreamingError(TextClassificationError):
    """
    Raised when streaming operations fail.

    This includes WebSocket connection errors, streaming protocol issues,
    real-time processing failures, and stream management problems.
    """

    def __init__(
        self,
        message: str,
        stream_id: Optional[str] = None,
        connection_id: Optional[str] = None,
        error_code: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize streaming error.

        Args:
            message: Error description
            stream_id: ID of the affected stream
            connection_id: ID of the affected connection
            error_code: Specific streaming error code
            **kwargs: Additional error details
        """
        details = kwargs.get('details', {})
        if stream_id:
            details['stream_id'] = stream_id
        if connection_id:
            details['connection_id'] = connection_id

        super().__init__(
            message,
            error_code=error_code or "STREAMING_ERROR",
            details=details,
            **kwargs
        )
        self.stream_id = stream_id
        self.connection_id = connection_id


# Exception hierarchy for easy catching
PROVIDER_EXCEPTIONS = (
    ProviderError,
    AuthenticationError,
    RateLimitError,
    ModelLoadError
)

WORKFLOW_EXCEPTIONS = (
    WorkflowError,
    ValidationError,
    ProcessingError
)

CONFIGURATION_EXCEPTIONS = (
    ConfigurationError,
    ValidationError
)

DATA_EXCEPTIONS = (
    DataSourceError,
    ProcessingError
)

RESOURCE_EXCEPTIONS = (
    ResourceError,
    TimeoutError,
    CacheError
)

STREAMING_EXCEPTIONS = (
    StreamingError,
)

ALL_EXCEPTIONS = (
    TextClassificationError,
    *PROVIDER_EXCEPTIONS,
    *WORKFLOW_EXCEPTIONS,
    *CONFIGURATION_EXCEPTIONS,
    *DATA_EXCEPTIONS,
    *RESOURCE_EXCEPTIONS,
    *STREAMING_EXCEPTIONS,
    SecurityError
)
