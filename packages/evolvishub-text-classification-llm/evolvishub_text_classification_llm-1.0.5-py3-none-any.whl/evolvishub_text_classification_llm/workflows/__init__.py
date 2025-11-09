"""
Workflows module for evolvishub-text-classification-llm.

This module contains workflow implementations including the main ClassificationEngine,
BatchProcessor, and WorkflowBuilder for orchestrating text classification tasks.
"""

# Import workflow components when available
try:
    from .classification import ClassificationEngine
    CLASSIFICATION_ENGINE_AVAILABLE = True
except ImportError:
    CLASSIFICATION_ENGINE_AVAILABLE = False

try:
    from .batch import BatchProcessor
    BATCH_PROCESSOR_AVAILABLE = True
except ImportError:
    BATCH_PROCESSOR_AVAILABLE = False

try:
    from .base import WorkflowBuilder
    WORKFLOW_BUILDER_AVAILABLE = True
except ImportError:
    WORKFLOW_BUILDER_AVAILABLE = False

__all__ = []

# Add available components to exports
if CLASSIFICATION_ENGINE_AVAILABLE:
    __all__.append("ClassificationEngine")

if BATCH_PROCESSOR_AVAILABLE:
    __all__.append("BatchProcessor")

if WORKFLOW_BUILDER_AVAILABLE:
    __all__.append("WorkflowBuilder")
