"""
Base workflow framework for text classification.

This module provides the foundation for building custom classification workflows
using a flexible, composable architecture with support for LangGraph integration.
"""

import asyncio
import json
import logging
import time
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, List, Optional, Type, Callable, TypedDict
from dataclasses import dataclass, field
from pydantic import BaseModel, ValidationError

from ..core.interfaces import IWorkflowEngine, ILLMProvider
from ..core.schemas import ClassificationInput, ClassificationResult, WorkflowConfig
from ..core.exceptions import WorkflowError, ValidationError as LibValidationError, TimeoutError


logger = logging.getLogger(__name__)


@dataclass
class WorkflowStep:
    """Represents a single step in the workflow execution."""
    timestamp: datetime
    step_name: str
    status: str  # "started", "completed", "failed", "skipped"
    duration_ms: float
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Tracks the execution of a workflow."""
    workflow_id: str
    input_id: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    status: str = "running"  # "running", "completed", "failed", "timeout"
    steps: List[WorkflowStep] = field(default_factory=list)
    result: Optional[ClassificationResult] = None
    error: Optional[str] = None
    retry_count: int = 0
    
    @property
    def duration_ms(self) -> float:
        """Calculate total execution duration."""
        if self.completed_at:
            return (self.completed_at - self.started_at).total_seconds() * 1000
        return (datetime.utcnow() - self.started_at).total_seconds() * 1000
    
    def add_step(self, step: WorkflowStep):
        """Add a workflow step."""
        self.steps.append(step)
    
    def get_step_by_name(self, step_name: str) -> Optional[WorkflowStep]:
        """Get a step by name."""
        for step in self.steps:
            if step.step_name == step_name:
                return step
        return None
    
    def get_successful_steps(self) -> List[WorkflowStep]:
        """Get all successful steps."""
        return [step for step in self.steps if step.status == "completed"]
    
    def get_failed_steps(self) -> List[WorkflowStep]:
        """Get all failed steps."""
        return [step for step in self.steps if step.status == "failed"]


class WorkflowNode(ABC):
    """
    Abstract base class for workflow nodes.
    
    Each node represents a single operation in the workflow pipeline.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        """Initialize the workflow node."""
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    async def execute(self, input_data: Any, context: Dict[str, Any]) -> Any:
        """
        Execute the node operation.
        
        Args:
            input_data: Input data for this node
            context: Workflow execution context
            
        Returns:
            Output data from this node
        """
        pass
    
    async def validate_input(self, input_data: Any) -> bool:
        """
        Validate input data for this node.
        
        Args:
            input_data: Input data to validate
            
        Returns:
            True if input is valid
        """
        return True
    
    async def validate_output(self, output_data: Any) -> bool:
        """
        Validate output data from this node.
        
        Args:
            output_data: Output data to validate
            
        Returns:
            True if output is valid
        """
        return True
    
    def get_node_info(self) -> Dict[str, Any]:
        """Get information about this node."""
        return {
            "name": self.name,
            "type": self.__class__.__name__,
            "config": self.config
        }


class PreprocessingNode(WorkflowNode):
    """Node for text preprocessing operations."""
    
    async def execute(self, input_data: ClassificationInput, context: Dict[str, Any]) -> ClassificationInput:
        """Execute text preprocessing."""
        # Apply preprocessing functions
        preprocessors = self.config.get("preprocessors", [])
        
        processed_text = input_data.text
        
        for preprocessor_name in preprocessors:
            if preprocessor_name == "clean_whitespace":
                processed_text = self._clean_whitespace(processed_text)
            elif preprocessor_name == "remove_urls":
                processed_text = self._remove_urls(processed_text)
            elif preprocessor_name == "normalize_case":
                processed_text = self._normalize_case(processed_text)
            elif preprocessor_name == "remove_special_chars":
                processed_text = self._remove_special_chars(processed_text)
        
        # Create new input with processed text
        return ClassificationInput(
            id=input_data.id,
            text=processed_text,
            metadata=input_data.metadata,
            source=input_data.source,
            timestamp=input_data.timestamp
        )
    
    def _clean_whitespace(self, text: str) -> str:
        """Clean excessive whitespace."""
        import re
        return re.sub(r'\s+', ' ', text.strip())
    
    def _remove_urls(self, text: str) -> str:
        """Remove URLs from text."""
        import re
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.sub(url_pattern, '', text)
    
    def _normalize_case(self, text: str) -> str:
        """Normalize text case."""
        case_mode = self.config.get("case_mode", "lower")
        if case_mode == "lower":
            return text.lower()
        elif case_mode == "upper":
            return text.upper()
        elif case_mode == "title":
            return text.title()
        return text
    
    def _remove_special_chars(self, text: str) -> str:
        """Remove special characters."""
        import re
        return re.sub(r'[^\w\s]', '', text)


class LLMClassificationNode(WorkflowNode):
    """Node for LLM-based classification."""
    
    def __init__(self, name: str, provider: ILLMProvider, config: Optional[Dict[str, Any]] = None):
        """Initialize LLM classification node."""
        super().__init__(name, config)
        self.provider = provider
    
    async def execute(self, input_data: ClassificationInput, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute LLM classification."""
        # Build messages for LLM
        messages = self._build_messages(input_data, context)
        
        # Generate response
        response = await self.provider.generate(
            messages=messages,
            temperature=self.config.get("temperature", 0.1),
            max_tokens=self.config.get("max_tokens", 500)
        )
        
        # Parse response
        parsed_response = self._parse_response(response)
        
        return parsed_response
    
    def _build_messages(self, input_data: ClassificationInput, context: Dict[str, Any]) -> List[Dict[str, str]]:
        """Build messages for LLM."""
        messages = []
        
        # System message
        system_prompt = self.config.get("system_prompt", "You are a text classifier.")
        messages.append({"role": "system", "content": system_prompt})
        
        # User message
        user_prompt_template = self.config.get("user_prompt_template", "Classify this text: {text}")
        user_prompt = user_prompt_template.format(text=input_data.text)
        messages.append({"role": "user", "content": user_prompt})
        
        return messages
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response."""
        try:
            # Try to parse as JSON
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # Fallback to simple parsing
            return {"raw_response": response}
            
        except json.JSONDecodeError:
            return {"raw_response": response}


class ValidationNode(WorkflowNode):
    """Node for validating classification results."""
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute validation."""
        # Check confidence threshold
        min_confidence = self.config.get("min_confidence", 0.5)
        confidence = input_data.get("confidence", 0.0)
        
        if confidence < min_confidence:
            input_data["validation_flags"] = input_data.get("validation_flags", [])
            input_data["validation_flags"].append("low_confidence")
        
        # Check required fields
        required_fields = self.config.get("required_fields", [])
        for field in required_fields:
            if field not in input_data:
                input_data["validation_flags"] = input_data.get("validation_flags", [])
                input_data["validation_flags"].append(f"missing_{field}")
        
        return input_data


class PostprocessingNode(WorkflowNode):
    """Node for post-processing classification results."""
    
    async def execute(self, input_data: Dict[str, Any], context: Dict[str, Any]) -> ClassificationResult:
        """Execute post-processing and create final result."""
        # Extract classification data
        primary_category = input_data.get("primary_category")
        categories = input_data.get("categories", {})
        confidence = input_data.get("confidence", 0.0)
        
        # Calculate overall confidence if not provided
        if not confidence and categories:
            confidence = max(categories.values()) if categories else 0.0
        
        # Create classification result
        result = ClassificationResult(
            input_id=context["input_id"],
            primary_category=primary_category,
            categories=categories,
            confidence=confidence,
            sentiment=input_data.get("sentiment"),
            entities=input_data.get("entities", []),
            keywords=input_data.get("keywords", []),
            processing_time_ms=context.get("processing_time_ms", 0.0),
            model_version=context.get("model_version", "unknown"),
            provider=context.get("provider", "unknown"),
            retry_count=context.get("retry_count", 0),
            reasoning=input_data.get("reasoning"),
            uncertainty_flags=input_data.get("validation_flags", []),
            metadata=input_data.get("metadata", {})
        )
        
        return result


class BaseWorkflow(IWorkflowEngine):
    """
    Base workflow implementation.
    
    Provides a framework for building custom classification workflows
    with support for node composition, error handling, and monitoring.
    """
    
    def __init__(self, config: WorkflowConfig):
        """Initialize base workflow."""
        super().__init__(config)
        self.nodes: List[WorkflowNode] = []
        self.execution_history: List[WorkflowExecution] = []
        self._max_history = 1000
    
    def add_node(self, node: WorkflowNode) -> 'BaseWorkflow':
        """Add a node to the workflow."""
        self.nodes.append(node)
        return self
    
    def add_preprocessing(self, preprocessors: List[str]) -> 'BaseWorkflow':
        """Add preprocessing node."""
        node = PreprocessingNode("preprocessing", {"preprocessors": preprocessors})
        return self.add_node(node)
    
    def add_llm_classification(
        self, 
        provider: ILLMProvider, 
        system_prompt: str,
        user_prompt_template: str,
        **kwargs
    ) -> 'BaseWorkflow':
        """Add LLM classification node."""
        config = {
            "system_prompt": system_prompt,
            "user_prompt_template": user_prompt_template,
            **kwargs
        }
        node = LLMClassificationNode("llm_classification", provider, config)
        return self.add_node(node)
    
    def add_validation(self, min_confidence: float = 0.5, required_fields: List[str] = None) -> 'BaseWorkflow':
        """Add validation node."""
        config = {
            "min_confidence": min_confidence,
            "required_fields": required_fields or []
        }
        node = ValidationNode("validation", config)
        return self.add_node(node)
    
    def add_postprocessing(self) -> 'BaseWorkflow':
        """Add post-processing node."""
        node = PostprocessingNode("postprocessing")
        return self.add_node(node)
    
    async def execute(self, input_data: ClassificationInput) -> ClassificationResult:
        """Execute the workflow for a single input."""
        execution = WorkflowExecution(
            workflow_id=self.config.name,
            input_id=str(input_data.id),
            started_at=datetime.utcnow()
        )
        
        try:
            # Initialize context
            context = {
                "input_id": input_data.id,
                "workflow_name": self.config.name,
                "provider": self.config.primary_provider.provider_type.value,
                "model_version": self.config.primary_provider.model,
                "retry_count": 0
            }
            
            # Execute nodes sequentially
            current_data = input_data
            
            for node in self.nodes:
                step_start = time.time()
                step = WorkflowStep(
                    timestamp=datetime.utcnow(),
                    step_name=node.name,
                    status="started",
                    duration_ms=0.0,
                    input_data=current_data
                )
                
                try:
                    # Execute node
                    current_data = await node.execute(current_data, context)
                    
                    # Update step
                    step.status = "completed"
                    step.output_data = current_data
                    step.duration_ms = (time.time() - step_start) * 1000
                    
                except Exception as e:
                    step.status = "failed"
                    step.error = str(e)
                    step.duration_ms = (time.time() - step_start) * 1000
                    execution.add_step(step)
                    raise WorkflowError(
                        f"Node {node.name} failed: {e}",
                        workflow_name=self.config.name,
                        step_name=node.name,
                        cause=e
                    )
                
                execution.add_step(step)
            
            # Ensure final result is ClassificationResult
            if not isinstance(current_data, ClassificationResult):
                raise WorkflowError(
                    "Workflow did not produce ClassificationResult",
                    workflow_name=self.config.name
                )
            
            # Update execution
            execution.status = "completed"
            execution.completed_at = datetime.utcnow()
            execution.result = current_data
            
            # Update processing time in result
            current_data.processing_time_ms = execution.duration_ms
            
            return current_data
            
        except Exception as e:
            execution.status = "failed"
            execution.completed_at = datetime.utcnow()
            execution.error = str(e)
            
            if isinstance(e, WorkflowError):
                raise
            raise WorkflowError(
                f"Workflow execution failed: {e}",
                workflow_name=self.config.name,
                cause=e
            )
        
        finally:
            # Store execution history
            self._store_execution(execution)
    
    async def execute_batch(self, input_batch: List[ClassificationInput]) -> 'BatchProcessingResult':
        """Execute workflow for a batch of inputs."""
        from ..core.schemas import BatchProcessingResult
        
        start_time = datetime.utcnow()
        results = []
        errors = []
        
        # Process inputs concurrently
        max_concurrent = self.config.max_concurrent
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def process_single(input_data: ClassificationInput):
            async with semaphore:
                try:
                    result = await self.execute(input_data)
                    return result
                except Exception as e:
                    error_info = {
                        "input_id": str(input_data.id),
                        "error": str(e),
                        "error_type": type(e).__name__
                    }
                    errors.append(error_info)
                    return None
        
        # Execute all inputs
        tasks = [process_single(input_data) for input_data in input_batch]
        task_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect results
        for result in task_results:
            if isinstance(result, ClassificationResult):
                results.append(result)
            elif isinstance(result, Exception):
                errors.append({
                    "error": str(result),
                    "error_type": type(result).__name__
                })
        
        # Calculate metrics
        end_time = datetime.utcnow()
        total_time_ms = (end_time - start_time).total_seconds() * 1000
        
        return BatchProcessingResult(
            total_items=len(input_batch),
            successful_items=len(results),
            failed_items=len(errors),
            results=results,
            errors=errors,
            total_processing_time_ms=total_time_ms,
            average_processing_time_ms=total_time_ms / len(input_batch) if input_batch else 0,
            throughput_items_per_second=len(input_batch) / (total_time_ms / 1000) if total_time_ms > 0 else 0,
            started_at=start_time,
            completed_at=end_time
        )
    
    async def validate_config(self) -> bool:
        """Validate workflow configuration."""
        if not self.nodes:
            raise WorkflowError("Workflow has no nodes", workflow_name=self.config.name)
        
        return True
    
    async def get_workflow_info(self) -> Dict[str, Any]:
        """Get workflow information."""
        return {
            "name": self.config.name,
            "type": self.config.workflow_type.value,
            "nodes": [node.get_node_info() for node in self.nodes],
            "config": self.config.dict(),
            "execution_count": len(self.execution_history)
        }
    
    def _store_execution(self, execution: WorkflowExecution):
        """Store execution in history."""
        self.execution_history.append(execution)
        
        # Limit history size
        if len(self.execution_history) > self._max_history:
            self.execution_history.pop(0)
    
    def get_execution_history(self, limit: int = 100) -> List[WorkflowExecution]:
        """Get recent execution history."""
        return self.execution_history[-limit:]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        if not self.execution_history:
            return {}
        
        successful = [e for e in self.execution_history if e.status == "completed"]
        failed = [e for e in self.execution_history if e.status == "failed"]
        
        avg_duration = sum(e.duration_ms for e in successful) / len(successful) if successful else 0
        
        return {
            "total_executions": len(self.execution_history),
            "successful_executions": len(successful),
            "failed_executions": len(failed),
            "success_rate": len(successful) / len(self.execution_history),
            "average_duration_ms": avg_duration,
            "last_execution": self.execution_history[-1].started_at.isoformat() if self.execution_history else None
        }


class WorkflowBuilder:
    """
    Builder for creating custom workflows.
    
    Provides a fluent interface for composing workflows from nodes.
    """
    
    def __init__(self):
        """Initialize workflow builder."""
        self._workflow = None
        self._config = None
    
    def create(self, config: WorkflowConfig) -> 'WorkflowBuilder':
        """Create a new workflow with configuration."""
        self._config = config
        self._workflow = BaseWorkflow(config)
        return self
    
    def add_preprocessing(self, preprocessors: List[str]) -> 'WorkflowBuilder':
        """Add preprocessing step."""
        if self._workflow:
            self._workflow.add_preprocessing(preprocessors)
        return self
    
    def add_classification(
        self, 
        provider: ILLMProvider,
        system_prompt: str,
        user_prompt_template: str,
        **kwargs
    ) -> 'WorkflowBuilder':
        """Add classification step."""
        if self._workflow:
            self._workflow.add_llm_classification(
                provider, system_prompt, user_prompt_template, **kwargs
            )
        return self
    
    def add_validation(self, min_confidence: float = 0.5) -> 'WorkflowBuilder':
        """Add validation step."""
        if self._workflow:
            self._workflow.add_validation(min_confidence)
        return self
    
    def add_postprocessing(self) -> 'WorkflowBuilder':
        """Add post-processing step."""
        if self._workflow:
            self._workflow.add_postprocessing()
        return self
    
    def build(self) -> BaseWorkflow:
        """Build and return the workflow."""
        if not self._workflow:
            raise WorkflowError("No workflow created. Call create() first.")
        
        return self._workflow
