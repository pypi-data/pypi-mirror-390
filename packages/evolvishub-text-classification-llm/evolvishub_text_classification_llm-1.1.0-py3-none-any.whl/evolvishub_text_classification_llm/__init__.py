"""
Evolvishub Text Classification LLM Library v1.1.0

A professional, enterprise-grade Python library for building domain-specific
text classification solutions using Large Language Models (LLMs).

This library provides a generic, business-agnostic framework that enables
organizations to implement custom text classification workflows with support
for 11+ LLM providers, enhanced classification capabilities, and structured output.

Version 1.1.0 Changes:
- Enhanced HuggingFace provider with classification-specific model support
- Added structured classification output across all providers
- Implemented dual classification pipelines (sentiment + categorization)
- Fixed empty classification results and zero confidence scores
- Added OpenAI function calling for structured classification
- Standardized 0.0-1.0 confidence score normalization
- Built-in support for 13 email categories
- Improved model type detection and pipeline optimization
"""

__version__ = "1.1.0"
__author__ = "Alban Maxhuni, PhD"
__email__ = "a.maxhuni@evolvis.ai"
__license__ = "Evolis AI License"
__website__ = "https://evolvis.ai"
__description__ = "Enterprise-grade text classification library with 10+ LLM providers, streaming, and advanced workflows"

# Core imports for easy access
from .core.schemas import (
    ClassificationInput,
    ClassificationResult,
    BatchProcessingResult,
    WorkflowConfig,
    ProviderConfig
)

from .core.exceptions import (
    TextClassificationError,
    ProviderError,
    WorkflowError,
    ConfigurationError,
    ValidationError
)

# Import available modules with error handling
try:
    from .workflows.classification import ClassificationEngine
    CLASSIFICATION_ENGINE_AVAILABLE = True
except ImportError:
    CLASSIFICATION_ENGINE_AVAILABLE = False

try:
    from .providers.factory import ProviderFactory
    PROVIDER_FACTORY_AVAILABLE = True
except ImportError:
    PROVIDER_FACTORY_AVAILABLE = False

try:
    from .workflows.batch import BatchProcessor
    BATCH_PROCESSOR_AVAILABLE = True
except ImportError:
    BATCH_PROCESSOR_AVAILABLE = False

try:
    from .workflows.base import WorkflowBuilder
    WORKFLOW_BUILDER_AVAILABLE = True
except ImportError:
    WORKFLOW_BUILDER_AVAILABLE = False

try:
    from .core.config import LibraryConfig
    LIBRARY_CONFIG_AVAILABLE = True
except ImportError:
    LIBRARY_CONFIG_AVAILABLE = False

try:
    from .monitoring.health import HealthChecker
    HEALTH_CHECKER_AVAILABLE = True
except ImportError:
    HEALTH_CHECKER_AVAILABLE = False

try:
    from .monitoring.metrics import MetricsCollector
    METRICS_COLLECTOR_AVAILABLE = True
except ImportError:
    METRICS_COLLECTOR_AVAILABLE = False

# Version information (Updated for v1.1.0)
VERSION_INFO = {
    "major": 1,
    "minor": 1,
    "patch": 0,
    "release": "stable"
}

# Supported providers (10+ providers in v1.1.0)
SUPPORTED_PROVIDERS = [
    "openai",
    "anthropic",
    "google",
    "cohere",
    "mistral",      # NEW in v1.1.0
    "replicate",    # NEW in v1.1.0
    "azure_openai",
    "aws_bedrock",
    "huggingface",
    "ollama",
    "custom"
]

# Feature flags (Enhanced for v1.1.0)
FEATURES = {
    "batch_processing": True,
    "caching": True,
    "semantic_caching": True,        # NEW in v1.1.0
    "monitoring": True,
    "streaming": True,
    "real_time_streaming": True,     # NEW in v1.1.0
    "websocket_support": True,       # NEW in v1.1.0
    "async_support": True,
    "provider_fallback": True,
    "cost_optimization": True,
    "security_features": True,
    "workflow_templates": True,      # NEW in v1.1.0
    "fine_tuning": True,            # Available in v1.0.2
    "multimodal": True,             # Available in v1.0.2
    "langgraph_integration": True    # Available in v1.0.2
}

def get_version() -> str:
    """Get the library version string."""
    return __version__

def get_supported_providers() -> list:
    """Get list of supported LLM providers."""
    return SUPPORTED_PROVIDERS.copy()

def get_features() -> dict:
    """Get available features and their status."""
    return FEATURES.copy()

def create_engine(config_path: str = None, **kwargs) -> 'ClassificationEngine':
    """
    Create a classification engine with configuration.
    
    Args:
        config_path: Path to configuration file (YAML/JSON)
        **kwargs: Configuration parameters
        
    Returns:
        Configured ClassificationEngine instance
        
    Example:
        >>> engine = create_engine("config.yaml")
        >>> result = await engine.classify("Text to classify")
    """
    if config_path:
        return ClassificationEngine.from_config_file(config_path)
    else:
        return ClassificationEngine.from_dict(kwargs)

def create_batch_processor(engine: 'ClassificationEngine' = None, **kwargs) -> 'BatchProcessor':
    """
    Create a batch processor for handling multiple texts.
    
    Args:
        engine: Classification engine to use
        **kwargs: Batch processing configuration
        
    Returns:
        Configured BatchProcessor instance
        
    Example:
        >>> processor = create_batch_processor(max_concurrent=10)
        >>> results = await processor.process_batch(texts)
    """
    return BatchProcessor(engine=engine, **kwargs)

# Library-level configuration
_global_config = None

def configure(config: dict = None, config_file: str = None):
    """
    Configure the library globally.

    Args:
        config: Configuration dictionary
        config_file: Path to configuration file

    Example:
        >>> configure({"default_provider": "openai", "cache_enabled": True})
    """
    global _global_config

    if not LIBRARY_CONFIG_AVAILABLE:
        print("Warning: LibraryConfig not available, configuration ignored")
        return

    if config_file:
        _global_config = LibraryConfig.from_file(config_file)
    elif config:
        _global_config = LibraryConfig.from_dict(config)
    else:
        _global_config = LibraryConfig()

def get_config():
    """Get the global library configuration."""
    global _global_config

    if not LIBRARY_CONFIG_AVAILABLE:
        return {"warning": "LibraryConfig not available"}

    if _global_config is None:
        _global_config = LibraryConfig()
    return _global_config

# Cleanup function
def cleanup():
    """Cleanup library resources."""
    global _global_config
    if _global_config:
        _global_config.cleanup()
    _global_config = None

# Build dynamic __all__ list based on available components
__all__ = [
    # Always available schemas
    "ClassificationInput",
    "ClassificationResult",
    "BatchProcessingResult",
    "WorkflowConfig",
    "ProviderConfig",

    # Always available exceptions
    "TextClassificationError",
    "ProviderError",
    "WorkflowError",
    "ConfigurationError",
    "ValidationError",

    # Always available convenience functions
    "get_version",
    "get_supported_providers",
    "get_features",
    "cleanup"
]

# Add conditional exports based on availability
if CLASSIFICATION_ENGINE_AVAILABLE:
    __all__.append("ClassificationEngine")

if BATCH_PROCESSOR_AVAILABLE:
    __all__.append("BatchProcessor")

if WORKFLOW_BUILDER_AVAILABLE:
    __all__.append("WorkflowBuilder")

if PROVIDER_FACTORY_AVAILABLE:
    __all__.append("ProviderFactory")

if LIBRARY_CONFIG_AVAILABLE:
    __all__.extend(["LibraryConfig", "configure", "get_config"])

if HEALTH_CHECKER_AVAILABLE:
    __all__.append("HealthChecker")

if METRICS_COLLECTOR_AVAILABLE:
    __all__.append("MetricsCollector")

# Add convenience functions if their dependencies are available
if CLASSIFICATION_ENGINE_AVAILABLE:
    __all__.append("create_engine")

if BATCH_PROCESSOR_AVAILABLE:
    __all__.append("create_batch_processor")

# Note: Additional imports will be added as modules are implemented
