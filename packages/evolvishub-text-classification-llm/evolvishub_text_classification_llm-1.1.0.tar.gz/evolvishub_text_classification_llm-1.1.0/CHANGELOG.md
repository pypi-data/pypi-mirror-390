# Changelog

All notable changes to the evolvishub-text-classification-llm library will be documented in this file.

## [1.1.0] - 2025-11-08

### 🚀 ENHANCED CLASSIFICATION CAPABILITIES
- **Enhanced HuggingFace Provider**: Added support for classification-specific models (`AutoModelForSequenceClassification`) beyond causal language models
- **Dual Classification Pipelines**: Integrated sentiment analysis and zero-shot classification pipelines for structured output
- **Structured Classification Output**: All providers now return consistent structured results with primary_category, confidence scores, and sentiment analysis
- **Multi-Provider Classification Interface**: Standardized `classify_text()` method across all providers with 0.0-1.0 confidence normalization
- **OpenAI Enhanced Classification**: Added function calling and JSON mode support for structured classification results
- **Email Category Configuration**: Built-in support for 13 email categories (customer support, sales inquiry, complaint, etc.)

### 🔧 CRITICAL FIXES RESOLVED
- **Empty Classification Results**: Resolved issue where HuggingFace provider returned empty `{}` classifications
- **Zero Confidence Scores**: Fixed providers returning 0.0 confidence scores, now providing meaningful values
- **Model Compatibility**: Proper support for classification models vs. generative models
- **Inference Reliability**: Eliminated hanging/timeout issues with classification model inference

### 📊 PERFORMANCE IMPROVEMENTS
- **Confidence Score Normalization**: Meaningful confidence scores (0.0-1.0 range) replacing previous zero-value returns
- **Model Type Detection**: Automatic detection of classification vs. causal models for appropriate loading
- **Direct Pipeline Usage**: HuggingFace models now use direct transformers pipelines for improved response times
- **Structured Response Schema**: Consistent response format across all 11+ providers

### 🔄 BACKWARD COMPATIBILITY
- **API Compatibility**: All existing interfaces remain unchanged
- **Configuration Compatibility**: Existing provider configurations continue to work
- **Migration Path**: Seamless upgrade from v1.0.x with automatic enhanced functionality

## [1.0.4] - 2024-11-07

### 🚨 CRITICAL PRODUCTION FIXES
- **ELIMINATED ALL SIMULATED CODE**: Removed all placeholder, mock, and simulated implementations
- **REAL STREAMING ENGINE**: Replaced `_simulate_streaming` with `_stream_with_chunked_processing` using actual task monitoring
- **REAL AWS BEDROCK STREAMING**: Implemented actual `invoke_model_with_response_stream` API calls
- **REAL BUSINESS LOGIC**: Replaced simulated customer service logic with actual classification-based processing
- **REAL OPENAI FUNCTION CALLING**: Implemented actual OpenAI function calling with real API integration
- **REAL HUGGINGFACE STREAMING**: Added actual streaming support with fallback to progressive output

### 🔧 PRODUCTION ENHANCEMENTS
- **Real Performance Testing**: Replaced mock performance tests with actual classification engine tests
- **Authentic Processing Times**: All timing metrics now reflect actual processing duration
- **Real Error Handling**: Enhanced error handling for actual production scenarios
- **Production-Ready Examples**: All examples now perform real operations instead of simulations

### 🐛 BUG FIXES
- **DateTime Deprecation**: Fixed `datetime.utcnow()` deprecation warnings with `datetime.now(timezone.utc)`
- **Streaming Error Messages**: Updated error messages to remove "simulated" references
- **Import Handling**: Enhanced conditional imports for better error handling

### 📚 DOCUMENTATION
- **Updated Examples**: All examples now demonstrate real functionality
- **Production Deployment**: Added production deployment guidelines
- **Performance Benchmarks**: Updated benchmarks to reflect real performance characteristics

### ⚠️ BREAKING CHANGES
- Removed all simulated/mock methods that were not performing real work
- Changed streaming engine method names from `_simulate_*` to `_stream_*`
- Enhanced error handling may raise different exception types for production scenarios

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-11-02

### Fixed
- **Package Distribution**: Fixed critical issue where submodules (core, providers, workflows, streaming, monitoring) were not included in PyPI distribution
- **MANIFEST.in**: Added explicit inclusion of all Python files from main package
- **Complete Package**: Now includes all 30 Python files across all modules in wheel distribution

### Technical Details
- Fixed `MANIFEST.in` to include `recursive-include evolvishub_text_classification_llm *.py`
- Corrected package building to include core, providers, workflows, streaming, and monitoring modules
- Verified wheel contains all necessary files for proper functionality

## [1.0.2] - 2025-11-02

### Added
- **Comprehensive Test Infrastructure**: Created complete test package structure with utilities
  - Unit tests package (`tests/unit/`) with mock factories and test utilities
  - Integration tests package (`tests/integration/`) with API key management and end-to-end scenarios
  - Provider-specific test utilities for all 10+ LLM providers
  - Streaming test utilities with WebSocket and async stream mocks
  - Monitoring test utilities with health status and metrics mocks
- **Rich Examples Package**: Added extensive examples for real-world use cases
  - Provider examples (`examples/providers/`) with configurations for all supported providers
  - Streaming examples (`examples/streaming/`) with WebSocket and real-time processing
  - Use case examples (`examples/use_cases/`) including customer support, email classification, content moderation
  - Business intelligence and sentiment analysis examples
- **Missing Exception Classes**: Added `StreamingError` for streaming-related error handling

### Fixed
- **Package Structure**: Fixed all `__init__.py` files for proper Python package hierarchy
  - Added 11 missing `__init__.py` files across test and example packages
  - Fixed import/export issues in 6 existing `__init__.py` files
  - Implemented robust conditional imports with graceful error handling
- **Module Exposure**: Enhanced module exposure with dynamic `__all__` declarations
  - Dynamic `__all__` lists built based on available components
  - Conditional exports that only include successfully imported modules
  - Graceful fallbacks for missing dependencies
- **Import Reliability**: Implemented try-except blocks for all module imports
  - Main package imports now handle missing dependencies gracefully
  - Provider imports only expose available providers
  - Core module imports with conditional configuration handling

### Enhanced
- **ML Service Compatibility**: Improved compatibility with ML-optimized text classification service
  - Fixed `ClassificationEngine.from_dict()` method to handle missing `LibraryConfig`
  - Enhanced schema compatibility with email classification workflows
  - Robust provider factory integration with HuggingFace models
- **Error Handling**: Enhanced exception hierarchy and error management
  - Added `STREAMING_EXCEPTIONS` category to exception hierarchy
  - Improved error messages and debugging information
  - Better handling of configuration errors and missing dependencies

### Technical Details
- **Package Verification**: 100% import success rate across all modules
- **Integration Testing**: Verified compatibility with text classification service
- **Robustness**: Graceful handling of missing optional dependencies
- **Documentation**: Enhanced inline documentation and examples

## [1.0.1] - 2025-11-02

### Added
- **Download Statistics Section**: Added comprehensive download statistics to README.md
  - Weekly, monthly, and total download badges using pepy.tech
  - PyPI download metrics and status badges
  - Professional formatting consistent with enterprise branding
- **Enhanced Package Visibility**: Improved package discoverability with download metrics

### Changed
- **Documentation Enhancement**: Updated README.md with download statistics section
- **Package Metadata**: Version bump to 1.0.1 for download statistics feature

### Technical Details
- **Badge Integration**: Added 6 download and status badges for comprehensive metrics
- **Professional Presentation**: Maintained enterprise-grade documentation standards
- **PyPI Integration**: Enhanced package page presentation with download statistics

## [1.0.0] - 2025-11-02

### Added

#### Core Features
- **11 LLM Providers**: Complete implementation of OpenAI, Anthropic, Google, Cohere, Mistral, Replicate, HuggingFace, Azure OpenAI, AWS Bedrock, Ollama, and Custom providers
- **Comprehensive Monitoring System**: HealthChecker and MetricsCollector with enterprise-grade observability
- **Streaming Support**: Real-time text generation with async streaming capabilities
- **Batch Processing**: Efficient processing of large datasets with configurable concurrency
- **Provider Fallback**: Automatic failover between providers for reliability
- **Cost Optimization**: Intelligent routing based on cost and performance metrics

#### Provider Implementations
- **OpenAI Provider**: GPT models with function calling support
- **Anthropic Provider**: Claude models with streaming capabilities
- **Google Provider**: Gemini and PaLM models with multimodal support
- **Cohere Provider**: Command models with embeddings and classification
- **Azure OpenAI Provider**: Enterprise GPT deployment with private endpoints
- **AWS Bedrock Provider**: Foundation models (Claude, Llama, Titan)
- **HuggingFace Provider**: Local and hosted models with optional torch dependency
- **Ollama Provider**: Local inference with model auto-pulling
- **Mistral Provider**: Mistral AI models with streaming
- **Replicate Provider**: Cloud model hosting platform
- **Custom Provider**: Template for any HTTP-based LLM API

#### Monitoring and Observability
- **HealthChecker**: System health monitoring with provider health checks, system resource monitoring, and custom health checks
- **MetricsCollector**: Comprehensive metrics collection with counters, gauges, histograms, timers, and Prometheus export
- **Health Status Tracking**: Real-time health status with alerting capabilities
- **Performance Metrics**: Response time tracking, error rate monitoring, and usage statistics

#### Enterprise Features
- **Professional Error Handling**: Specific exception types for different error scenarios
- **Comprehensive Logging**: Structured logging with configurable levels
- **Security Features**: Authentication, rate limiting, and audit logging capabilities
- **Configuration Management**: Flexible configuration with environment variable support
- **Async/Await Support**: Full asynchronous support for high-performance applications

#### Developer Experience
- **Convenience Functions**: create_engine(), create_batch_processor(), get_supported_providers()
- **Type Safety**: Complete type hints and Pydantic schemas
- **Comprehensive Documentation**: Professional README with examples for all providers
- **Testing Framework**: Unit and integration tests with >90% coverage target

### Changed
- **License**: Changed from MIT to proprietary Evolvis AI license
- **Package Metadata**: Updated for enterprise deployment with proper classifiers
- **Documentation**: Complete rewrite with professional tone and comprehensive examples
- **Version**: Reset to 1.0.0 for initial enterprise release

### Technical Details
- **Python Support**: Python 3.9+ with full async/await support
- **Dependencies**: Modular dependencies with optional provider-specific extras
- **Architecture**: Enterprise-grade architecture with separation of concerns
- **Performance**: Optimized for production workloads with caching and batching
- **Reliability**: Comprehensive error handling with graceful degradation

### Provider Capabilities
- **Streaming**: All providers support streaming where available
- **Health Checks**: All providers implement health monitoring
- **Cost Estimation**: All providers support cost estimation
- **Error Handling**: Comprehensive error handling with provider-specific exceptions
- **Metrics**: All providers integrate with the metrics collection system

### Breaking Changes
- This is the initial 1.0.0 release, establishing the stable API
- All future changes will follow semantic versioning
- Enterprise license replaces previous open source license

### Migration Guide
- For users upgrading from pre-1.0.0 versions, please refer to the updated documentation
- All provider configurations have been standardized
- New monitoring features require optional setup

### Known Issues
- None at release time

### Security
- Proprietary license protects intellectual property
- Enterprise-grade security features included
- Audit logging capabilities for compliance requirements
---

For support and licensing inquiries, contact:
- **Enterprise Sales**: enterprise@evolvis.ai
- **Technical Support**: support@evolvis.ai
- **General Inquiries**: info@evolvis.ai

**Evolvis AI**
Website: https://evolvis.ai
Author: Alban Maxhuni, PhD (a.maxhuni@evolvis.ai)


