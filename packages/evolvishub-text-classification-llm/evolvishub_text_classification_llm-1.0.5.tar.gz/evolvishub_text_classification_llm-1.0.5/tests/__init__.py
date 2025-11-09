"""
Test suite for evolvishub-text-classification-llm.

This package contains comprehensive tests for all library components including
unit tests, integration tests, and performance tests.
"""

# Test configuration and utilities
import sys
import os
from pathlib import Path

# Add the library to the path for testing
lib_path = Path(__file__).parent.parent / "evolvishub_text_classification_llm"
if str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

# Test markers for pytest
UNIT_TESTS = "unit"
INTEGRATION_TESTS = "integration"
PERFORMANCE_TESTS = "performance"
PROVIDER_TESTS = "provider"
WORKFLOW_TESTS = "workflow"
STREAMING_TESTS = "streaming"
MONITORING_TESTS = "monitoring"

__all__ = [
    "UNIT_TESTS",
    "INTEGRATION_TESTS", 
    "PERFORMANCE_TESTS",
    "PROVIDER_TESTS",
    "WORKFLOW_TESTS",
    "STREAMING_TESTS",
    "MONITORING_TESTS"
]
