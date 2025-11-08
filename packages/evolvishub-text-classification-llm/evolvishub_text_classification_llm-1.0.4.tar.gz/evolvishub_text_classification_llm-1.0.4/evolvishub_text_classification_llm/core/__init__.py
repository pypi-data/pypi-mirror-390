"""
Core module for evolvishub-text-classification-llm.

This module contains the fundamental schemas, exceptions, and utilities
used throughout the text classification library.
"""

from .schemas import (
    ProviderType,
    ProviderConfig,
    WorkflowConfig,
    ClassificationInput,
    ClassificationResult,
    BatchProcessingResult,
    ProcessingStatus,
    WorkflowType
)

# Import config if available
try:
    from .config import LibraryConfig
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

# Import interfaces if available
try:
    from .interfaces import IDataFetcher, IClassificationProvider
    INTERFACES_AVAILABLE = True
except ImportError:
    INTERFACES_AVAILABLE = False

from .exceptions import (
    TextClassificationError,
    ProviderError,
    ConfigurationError,
    WorkflowError,
    StreamingError,
    ValidationError
)

__all__ = [
    # Schemas
    "ProviderType",
    "ProviderConfig",
    "WorkflowConfig",
    "ClassificationInput",
    "ClassificationResult",
    "BatchProcessingResult",
    "ProcessingStatus",
    "WorkflowType",

    # Exceptions
    "TextClassificationError",
    "ProviderError",
    "ConfigurationError",
    "WorkflowError",
    "StreamingError",
    "ValidationError"
]

# Add conditional exports
if CONFIG_AVAILABLE:
    __all__.append("LibraryConfig")

if INTERFACES_AVAILABLE:
    __all__.extend(["IDataFetcher", "IClassificationProvider"])
