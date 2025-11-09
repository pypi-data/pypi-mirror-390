"""
Batch processing workflow for text classification.

This module provides efficient batch processing capabilities with
parallel execution, progress tracking, and resource management.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List, Optional, Callable, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass, field
from uuid import uuid4

from .classification import ClassificationEngine
from ..core.schemas import (
    ClassificationInput, ClassificationResult, BatchProcessingResult
)
from ..core.exceptions import WorkflowError, ResourceError


logger = logging.getLogger(__name__)


@dataclass
class BatchProgress:
    """Tracks progress of batch processing."""
    batch_id: str
    total_items: int
    processed_items: int = 0
    successful_items: int = 0
    failed_items: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    estimated_completion: Optional[datetime] = None
    current_throughput: float = 0.0  # items per second
    
    @property
    def progress_percentage(self) -> float:
        """Calculate progress percentage."""
        if self.total_items == 0:
            return 100.0
        return (self.processed_items / self.total_items) * 100
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.processed_items == 0:
            return 0.0
        return (self.successful_items / self.processed_items) * 100
    
    @property
    def elapsed_time(self) -> float:
        """Calculate elapsed time in seconds."""
        return (datetime.utcnow() - self.started_at).total_seconds()
    
    def update_throughput(self):
        """Update current throughput calculation."""
        elapsed = self.elapsed_time
        if elapsed > 0:
            self.current_throughput = self.processed_items / elapsed
            
            # Estimate completion time
            if self.current_throughput > 0:
                remaining_items = self.total_items - self.processed_items
                remaining_seconds = remaining_items / self.current_throughput
                self.estimated_completion = datetime.utcnow().timestamp() + remaining_seconds


class BatchProcessor:
    """
    Batch processor for efficient text classification.
    
    Provides parallel processing, progress tracking, resource management,
    and error handling for large-scale text classification tasks.
    """
    
    def __init__(
        self,
        engine: Optional[ClassificationEngine] = None,
        max_concurrent: int = 10,
        batch_size: int = 100,
        retry_attempts: int = 3,
        retry_delay: float = 1.0,
        progress_callback: Optional[Callable[[BatchProgress], None]] = None
    ):
        """
        Initialize batch processor.
        
        Args:
            engine: Classification engine to use
            max_concurrent: Maximum concurrent processing tasks
            batch_size: Size of processing batches
            retry_attempts: Number of retry attempts for failed items
            retry_delay: Delay between retry attempts
            progress_callback: Callback function for progress updates
        """
        self.engine = engine
        self.max_concurrent = max_concurrent
        self.batch_size = batch_size
        self.retry_attempts = retry_attempts
        self.retry_delay = retry_delay
        self.progress_callback = progress_callback
        
        # Processing state
        self._active_batches: Dict[str, BatchProgress] = {}
        self._processing_stats = {
            "total_batches": 0,
            "total_items": 0,
            "successful_items": 0,
            "failed_items": 0,
            "average_throughput": 0.0
        }
    
    async def process_batch(
        self,
        texts: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None,
        batch_id: Optional[str] = None
    ) -> BatchProcessingResult:
        """
        Process a batch of texts.
        
        Args:
            texts: List of texts to classify
            metadata_list: Optional metadata for each text
            batch_id: Optional batch identifier
            
        Returns:
            Batch processing result
        """
        batch_id = batch_id or str(uuid4())
        
        # Initialize progress tracking
        progress = BatchProgress(
            batch_id=batch_id,
            total_items=len(texts)
        )
        self._active_batches[batch_id] = progress
        
        try:
            logger.info(f"Starting batch processing: {batch_id} ({len(texts)} items)")
            
            # Create classification inputs
            inputs = []
            for i, text in enumerate(texts):
                metadata = metadata_list[i] if metadata_list and i < len(metadata_list) else {}
                inputs.append(ClassificationInput(text=text, metadata=metadata))
            
            # Process with concurrency control
            results = await self._process_with_concurrency(inputs, progress)
            
            # Create batch result
            batch_result = self._create_batch_result(inputs, results, progress)
            
            # Update global stats
            self._update_global_stats(batch_result)
            
            logger.info(f"Batch processing completed: {batch_id} "
                       f"({batch_result.successful_items}/{batch_result.total_items} successful)")
            
            return batch_result
            
        except Exception as e:
            logger.error(f"Batch processing failed: {batch_id} - {e}")
            raise WorkflowError(f"Batch processing failed: {e}", cause=e)
        
        finally:
            # Cleanup
            if batch_id in self._active_batches:
                del self._active_batches[batch_id]
    
    async def process_stream(
        self,
        input_stream: AsyncGenerator[ClassificationInput, None],
        batch_id: Optional[str] = None
    ) -> AsyncGenerator[ClassificationResult, None]:
        """
        Process a stream of inputs with real-time results.
        
        Args:
            input_stream: Async generator of classification inputs
            batch_id: Optional batch identifier
            
        Yields:
            Classification results as they are completed
        """
        batch_id = batch_id or str(uuid4())
        
        # Initialize progress (unknown total)
        progress = BatchProgress(
            batch_id=batch_id,
            total_items=0  # Will be updated as items are processed
        )
        self._active_batches[batch_id] = progress
        
        try:
            # Create semaphore for concurrency control
            semaphore = asyncio.Semaphore(self.max_concurrent)
            
            # Process items as they arrive
            async for input_item in input_stream:
                progress.total_items += 1
                
                # Process item with concurrency control
                async def process_item():
                    async with semaphore:
                        try:
                            result = await self.engine.classify(
                                input_item.text,
                                input_item.metadata
                            )
                            progress.successful_items += 1
                            return result
                        except Exception as e:
                            progress.failed_items += 1
                            logger.error(f"Failed to process item {input_item.id}: {e}")
                            return None
                        finally:
                            progress.processed_items += 1
                            progress.update_throughput()
                            
                            # Call progress callback
                            if self.progress_callback:
                                self.progress_callback(progress)
                
                # Start processing task
                task = asyncio.create_task(process_item())
                
                # Yield result when ready
                result = await task
                if result:
                    yield result
                    
        finally:
            # Cleanup
            if batch_id in self._active_batches:
                del self._active_batches[batch_id]
    
    async def process_file(
        self,
        file_path: str,
        text_column: str = "text",
        metadata_columns: Optional[List[str]] = None,
        file_format: str = "csv"
    ) -> BatchProcessingResult:
        """
        Process texts from a file.
        
        Args:
            file_path: Path to input file
            text_column: Name of text column
            metadata_columns: Names of metadata columns
            file_format: File format (csv, json, jsonl)
            
        Returns:
            Batch processing result
        """
        try:
            # Load data from file
            inputs = await self._load_from_file(
                file_path, text_column, metadata_columns, file_format
            )
            
            # Extract texts and metadata
            texts = [inp.text for inp in inputs]
            metadata_list = [inp.metadata for inp in inputs]
            
            # Process batch
            return await self.process_batch(texts, metadata_list)
            
        except Exception as e:
            raise WorkflowError(f"Failed to process file {file_path}: {e}", cause=e)
    
    async def get_progress(self, batch_id: str) -> Optional[BatchProgress]:
        """
        Get progress for a specific batch.
        
        Args:
            batch_id: Batch identifier
            
        Returns:
            Batch progress or None if not found
        """
        return self._active_batches.get(batch_id)
    
    def get_active_batches(self) -> List[BatchProgress]:
        """Get list of currently active batches."""
        return list(self._active_batches.values())
    
    def get_processing_stats(self) -> Dict[str, Any]:
        """Get overall processing statistics."""
        return self._processing_stats.copy()
    
    # Private methods
    
    async def _process_with_concurrency(
        self,
        inputs: List[ClassificationInput],
        progress: BatchProgress
    ) -> List[Optional[ClassificationResult]]:
        """Process inputs with concurrency control."""
        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(self.max_concurrent)
        
        async def process_single(input_item: ClassificationInput) -> Optional[ClassificationResult]:
            async with semaphore:
                for attempt in range(self.retry_attempts + 1):
                    try:
                        result = await self.engine.classify(
                            input_item.text,
                            input_item.metadata
                        )
                        progress.successful_items += 1
                        return result
                        
                    except Exception as e:
                        if attempt < self.retry_attempts:
                            logger.warning(f"Retry {attempt + 1} for item {input_item.id}: {e}")
                            await asyncio.sleep(self.retry_delay * (attempt + 1))
                        else:
                            logger.error(f"Failed to process item {input_item.id} after {self.retry_attempts} retries: {e}")
                            progress.failed_items += 1
                            return None
                    
                    finally:
                        if attempt == self.retry_attempts:  # Last attempt
                            progress.processed_items += 1
                            progress.update_throughput()
                            
                            # Call progress callback
                            if self.progress_callback:
                                self.progress_callback(progress)
        
        # Process all inputs concurrently
        tasks = [process_single(input_item) for input_item in inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions in results
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Task failed with exception: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results
    
    def _create_batch_result(
        self,
        inputs: List[ClassificationInput],
        results: List[Optional[ClassificationResult]],
        progress: BatchProgress
    ) -> BatchProcessingResult:
        """Create batch processing result."""
        # Filter successful results
        successful_results = [r for r in results if r is not None]
        
        # Calculate metrics
        total_time_ms = progress.elapsed_time * 1000
        avg_time_ms = total_time_ms / len(inputs) if inputs else 0
        throughput = len(inputs) / (total_time_ms / 1000) if total_time_ms > 0 else 0
        
        # Calculate provider usage
        provider_usage = {}
        for result in successful_results:
            provider = result.provider
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
        
        # Calculate average confidence
        confidences = [r.confidence for r in successful_results if r.confidence > 0]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        
        # Count high confidence results
        high_confidence_count = sum(1 for r in successful_results if r.confidence >= 0.8)
        
        return BatchProcessingResult(
            total_items=len(inputs),
            successful_items=len(successful_results),
            failed_items=len(inputs) - len(successful_results),
            results=successful_results,
            errors=[],  # Could be enhanced to collect specific errors
            total_processing_time_ms=total_time_ms,
            average_processing_time_ms=avg_time_ms,
            throughput_items_per_second=throughput,
            provider_usage=provider_usage,
            cache_hit_rate=0.0,  # Would need cache integration
            average_confidence=avg_confidence,
            high_confidence_count=high_confidence_count,
            started_at=progress.started_at,
            completed_at=datetime.utcnow()
        )
    
    def _update_global_stats(self, batch_result: BatchProcessingResult):
        """Update global processing statistics."""
        self._processing_stats["total_batches"] += 1
        self._processing_stats["total_items"] += batch_result.total_items
        self._processing_stats["successful_items"] += batch_result.successful_items
        self._processing_stats["failed_items"] += batch_result.failed_items
        
        # Update average throughput
        total_items = self._processing_stats["total_items"]
        if total_items > 0:
            self._processing_stats["average_throughput"] = (
                (self._processing_stats["average_throughput"] * (total_items - batch_result.total_items) +
                 batch_result.throughput_items_per_second * batch_result.total_items) / total_items
            )
    
    async def _load_from_file(
        self,
        file_path: str,
        text_column: str,
        metadata_columns: Optional[List[str]],
        file_format: str
    ) -> List[ClassificationInput]:
        """Load classification inputs from file."""
        import pandas as pd
        import json
        from pathlib import Path
        
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        inputs = []
        
        try:
            if file_format.lower() == "csv":
                df = pd.read_csv(file_path)
                
                for _, row in df.iterrows():
                    text = str(row[text_column])
                    metadata = {}
                    
                    if metadata_columns:
                        for col in metadata_columns:
                            if col in row:
                                metadata[col] = row[col]
                    
                    inputs.append(ClassificationInput(text=text, metadata=metadata))
            
            elif file_format.lower() in ["json", "jsonl"]:
                with open(file_path, 'r', encoding='utf-8') as f:
                    if file_format.lower() == "json":
                        data = json.load(f)
                        if isinstance(data, list):
                            for item in data:
                                text = item.get(text_column, "")
                                metadata = {k: v for k, v in item.items() 
                                          if k != text_column and (not metadata_columns or k in metadata_columns)}
                                inputs.append(ClassificationInput(text=text, metadata=metadata))
                    
                    else:  # jsonl
                        for line in f:
                            item = json.loads(line.strip())
                            text = item.get(text_column, "")
                            metadata = {k: v for k, v in item.items() 
                                      if k != text_column and (not metadata_columns or k in metadata_columns)}
                            inputs.append(ClassificationInput(text=text, metadata=metadata))
            
            else:
                raise ValueError(f"Unsupported file format: {file_format}")
            
            logger.info(f"Loaded {len(inputs)} items from {file_path}")
            return inputs
            
        except Exception as e:
            raise WorkflowError(f"Failed to load file {file_path}: {e}", cause=e)
