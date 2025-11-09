"""
Main classification engine for the text classification library.

This module provides the primary interface for text classification,
integrating providers, workflows, and configuration management.
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from pathlib import Path

# Core imports
from ..core.schemas import (
    ClassificationInput, ClassificationResult, WorkflowConfig,
    ProviderConfig, ProviderType
)
from ..core.exceptions import (
    ConfigurationError, WorkflowError, ProviderError
)

# Conditional imports
try:
    from ..core.config import LibraryConfig
    LIBRARY_CONFIG_AVAILABLE = True
except ImportError:
    LIBRARY_CONFIG_AVAILABLE = False

try:
    from ..providers.factory import ProviderFactory
    PROVIDER_FACTORY_AVAILABLE = True
except ImportError:
    PROVIDER_FACTORY_AVAILABLE = False

try:
    from ..providers.base import BaseLLMProvider
    BASE_PROVIDER_AVAILABLE = True
except ImportError:
    BASE_PROVIDER_AVAILABLE = False

try:
    from .base import WorkflowBuilder
    WORKFLOW_BUILDER_AVAILABLE = True
except ImportError:
    WORKFLOW_BUILDER_AVAILABLE = False


logger = logging.getLogger(__name__)


class ClassificationEngine:
    """
    Main classification engine.
    
    This class provides the primary interface for text classification,
    handling provider management, workflow execution, and configuration.
    """
    
    def __init__(
        self,
        config: Optional[WorkflowConfig] = None,
        providers: Optional[List[Any]] = None
    ):
        """
        Initialize classification engine.

        Args:
            config: Workflow configuration
            providers: Pre-initialized providers (optional)
        """
        self.config = config
        self.providers: Dict[str, Any] = {}
        self.primary_provider: Optional[Any] = None
        self.workflow: Optional[Any] = None
        self._initialized = False

        # Add pre-initialized providers
        if providers:
            for provider in providers:
                self.providers[getattr(provider, 'provider_type', 'unknown')] = provider
    
    @classmethod
    def from_config_file(cls, config_path: Union[str, Path]) -> 'ClassificationEngine':
        """
        Create classification engine from configuration file.
        
        Args:
            config_path: Path to configuration file (YAML/JSON)
            
        Returns:
            Configured ClassificationEngine instance
        """
        try:
            # Load library configuration
            lib_config = LibraryConfig.from_file(config_path)
            
            # Create engine
            engine = cls(config=lib_config)
            
            return engine
            
        except Exception as e:
            raise ConfigurationError(
                f"Failed to create engine from config file: {e}",
                config_file=str(config_path),
                cause=e
            )
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> 'ClassificationEngine':
        """
        Create classification engine from configuration dictionary.
        
        Args:
            config_dict: Configuration dictionary
            
        Returns:
            Configured ClassificationEngine instance
        """
        try:
            # Create library configuration if available
            if LIBRARY_CONFIG_AVAILABLE:
                lib_config = LibraryConfig.from_dict(config_dict)
                engine = cls(config=lib_config)
            else:
                # Create engine with basic configuration
                engine = cls()
                # Set basic properties from config_dict
                if 'provider_type' in config_dict:
                    engine._provider_type = config_dict['provider_type']
                if 'model' in config_dict:
                    engine._model = config_dict['model']

            return engine

        except Exception as e:
            raise ConfigurationError(
                f"Failed to create engine from config dict: {e}",
                cause=e
            )
    
    @classmethod
    def create_simple(
        cls,
        provider_type: str = "openai",
        model: str = "gpt-3.5-turbo",
        api_key: Optional[str] = None,
        categories: Optional[List[str]] = None,
        **kwargs
    ) -> 'ClassificationEngine':
        """
        Create a simple classification engine with minimal configuration.
        
        Args:
            provider_type: LLM provider type
            model: Model name
            api_key: API key for cloud providers
            categories: Classification categories
            **kwargs: Additional configuration
            
        Returns:
            Configured ClassificationEngine instance
        """
        # Create provider configuration
        provider_config = ProviderConfig(
            provider_type=ProviderType(provider_type),
            model=model,
            api_key=api_key,
            **kwargs
        )
        
        # Create workflow configuration
        workflow_config = WorkflowConfig(
            name="simple_classification",
            primary_provider=provider_config,
            categories=categories or ["positive", "negative", "neutral"]
        )
        
        # Create engine
        engine = ClassificationEngine(config=workflow_config)
        
        return engine
    
    async def initialize(self) -> bool:
        """
        Initialize the classification engine.
        
        This method sets up providers, creates workflows, and prepares
        the engine for classification requests.
        
        Returns:
            True if initialization successful
        """
        try:
            logger.info("Initializing classification engine...")
            
            # Initialize providers
            await self._initialize_providers()
            
            # Create workflow
            await self._create_workflow()
            
            # Validate configuration
            await self._validate_setup()
            
            self._initialized = True
            logger.info("Classification engine initialized successfully")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize classification engine: {e}")
            raise WorkflowError(
                f"Engine initialization failed: {e}",
                cause=e
            )
    
    async def classify(
        self, 
        text: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> ClassificationResult:
        """
        Classify a single text input.
        
        Args:
            text: Text to classify
            metadata: Additional metadata
            
        Returns:
            Classification result
        """
        if not self._initialized:
            await self.initialize()
        
        # Create classification input
        classification_input = ClassificationInput(
            text=text,
            metadata=metadata or {}
        )
        
        try:
            # Check if primary provider supports enhanced classification
            if (hasattr(self.primary_provider, 'classify_text') and
                hasattr(self.primary_provider, 'supports_classification') and
                self.primary_provider.supports_classification):

                # Use enhanced classification for HuggingFace provider
                categories = self.config.categories if self.config.categories else None
                classification_result = await self.primary_provider.classify_text(
                    text=text,
                    categories=categories,
                    include_sentiment=True
                )

                # Convert to ClassificationResult
                result = ClassificationResult(
                    input_id=classification_input.id,
                    primary_category=classification_result.get("primary_category"),
                    categories=classification_result.get("categories", {}),
                    confidence=classification_result.get("confidence", 0.0),
                    sentiment=classification_result.get("sentiment"),
                    processing_time_ms=classification_result.get("processing_time_ms", 0.0),
                    provider=self.primary_provider.provider_type,
                    model_version=self.config.primary_provider.model,
                    metadata=metadata or {}
                )

                logger.debug(f"Enhanced classification completed for input {classification_input.id}")
                return result
            else:
                # Fallback to workflow execution for other providers
                result = await self.workflow.execute(classification_input)

                logger.debug(f"Workflow classification completed for input {classification_input.id}")
                return result

        except Exception as e:
            logger.error(f"Classification failed: {e}")
            raise WorkflowError(
                f"Classification failed: {e}",
                cause=e
            )
    
    async def classify_batch(
        self, 
        texts: List[str], 
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[ClassificationResult]:
        """
        Classify a batch of texts.
        
        Args:
            texts: List of texts to classify
            metadata_list: List of metadata dictionaries (optional)
            
        Returns:
            List of classification results
        """
        if not self._initialized:
            await self.initialize()
        
        # Create classification inputs
        inputs = []
        for i, text in enumerate(texts):
            metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else {}
            inputs.append(ClassificationInput(text=text, metadata=metadata))
        
        try:
            # Execute batch workflow
            batch_result = await self.workflow.execute_batch(inputs)
            
            logger.info(f"Batch classification completed: {batch_result.successful_items}/{batch_result.total_items} successful")
            
            return batch_result.results
            
        except Exception as e:
            logger.error(f"Batch classification failed: {e}")
            raise WorkflowError(
                f"Batch classification failed: {e}",
                cause=e
            )
    
    async def get_health_status(self) -> Dict[str, Any]:
        """
        Get health status of the classification engine.
        
        Returns:
            Dictionary with health information
        """
        status = {
            "engine_initialized": self._initialized,
            "providers": {},
            "workflow": None
        }
        
        # Check provider health
        for name, provider in self.providers.items():
            try:
                provider_health = await provider.health_check()
                status["providers"][name] = provider_health
            except Exception as e:
                status["providers"][name] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Check workflow status
        if self.workflow:
            try:
                workflow_info = await self.workflow.get_workflow_info()
                status["workflow"] = {
                    "status": "healthy",
                    "info": workflow_info
                }
            except Exception as e:
                status["workflow"] = {
                    "status": "unhealthy",
                    "error": str(e)
                }
        
        # Determine overall status
        overall_status = "healthy"
        if not self._initialized:
            overall_status = "not_initialized"
        elif any(p.get("status") == "unhealthy" for p in status["providers"].values()):
            overall_status = "degraded"
        elif status["workflow"] and status["workflow"].get("status") == "unhealthy":
            overall_status = "degraded"
        
        status["overall_status"] = overall_status
        
        return status
    
    async def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for the engine.
        
        Returns:
            Dictionary with usage statistics
        """
        stats = {
            "providers": {},
            "workflow": None
        }
        
        # Get provider stats
        for name, provider in self.providers.items():
            try:
                provider_stats = await provider.get_usage_stats()
                stats["providers"][name] = provider_stats
            except Exception as e:
                stats["providers"][name] = {"error": str(e)}
        
        # Get workflow stats
        if self.workflow:
            try:
                workflow_stats = self.workflow.get_execution_stats()
                stats["workflow"] = workflow_stats
            except Exception as e:
                stats["workflow"] = {"error": str(e)}
        
        return stats
    
    async def cleanup(self):
        """Cleanup engine resources."""
        logger.info("Cleaning up classification engine...")
        
        # Cleanup providers
        for provider in self.providers.values():
            try:
                await provider.cleanup()
            except Exception as e:
                logger.warning(f"Error cleaning up provider: {e}")
        
        self.providers.clear()
        self.primary_provider = None
        self.workflow = None
        self._initialized = False
        
        logger.info("Classification engine cleanup completed")
    
    # Private methods
    
    async def _initialize_providers(self):
        """Initialize LLM providers."""
        if isinstance(self.config, LibraryConfig):
            # Initialize from library config
            for name, provider_config in self.config.providers.items():
                if name not in self.providers:
                    provider = ProviderFactory.create_provider(provider_config)
                    await provider.initialize()
                    self.providers[name] = provider
            
            # Set primary provider
            if self.config.default_provider in self.providers:
                self.primary_provider = self.providers[self.config.default_provider]
            elif self.providers:
                self.primary_provider = next(iter(self.providers.values()))
        
        elif isinstance(self.config, WorkflowConfig):
            # Initialize from workflow config
            if "primary" not in self.providers:
                provider = ProviderFactory.create_provider(self.config.primary_provider)
                await provider.initialize()
                self.providers["primary"] = provider
                self.primary_provider = provider
            
            # Initialize fallback providers
            for i, fallback_config in enumerate(self.config.fallback_providers):
                fallback_name = f"fallback_{i}"
                if fallback_name not in self.providers:
                    provider = ProviderFactory.create_provider(fallback_config)
                    await provider.initialize()
                    self.providers[fallback_name] = provider
        
        if not self.primary_provider:
            raise ConfigurationError("No primary provider configured")
    
    async def _create_workflow(self):
        """Create classification workflow."""
        if isinstance(self.config, WorkflowConfig):
            workflow_config = self.config
        else:
            # Create default workflow config
            workflow_config = WorkflowConfig(
                name="default_classification",
                primary_provider=list(self.providers.values())[0].config
            )
        
        # Build workflow
        if not WORKFLOW_BUILDER_AVAILABLE:
            raise WorkflowError("WorkflowBuilder not available. Please check installation.")

        builder = WorkflowBuilder()
        
        self.workflow = (builder
            .create(workflow_config)
            .add_preprocessing(["clean_whitespace", "remove_urls"])
            .add_classification(
                provider=self.primary_provider,
                system_prompt=workflow_config.system_prompt or "You are a text classifier.",
                user_prompt_template=workflow_config.user_prompt_template
            )
            .add_validation(workflow_config.min_confidence_threshold)
            .add_postprocessing()
            .build())
    
    async def _validate_setup(self):
        """Validate engine setup."""
        if not self.providers:
            raise ConfigurationError("No providers configured")
        
        if not self.primary_provider:
            raise ConfigurationError("No primary provider set")
        
        if not self.workflow:
            raise ConfigurationError("No workflow created")
        
        # Validate workflow
        await self.workflow.validate_config()
    
    # Context manager support
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.cleanup()
