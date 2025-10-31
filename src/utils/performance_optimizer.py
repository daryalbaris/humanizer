"""
Performance Optimization Utilities for BMAD Humanizer

This module provides performance optimization utilities including:
- LLM API call batching and caching
- Parallel processing for independent tools
- Memory-efficient streaming for large documents
- Response caching with TTL
"""

import asyncio
import hashlib
import json
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Tuple
from collections import OrderedDict
import threading


class LRUCache:
    """Thread-safe LRU Cache with TTL support"""

    def __init__(self, max_size: int = 100, ttl_seconds: int = 3600):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.lock = threading.Lock()
        self.timestamps: Dict[str, float] = {}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache if exists and not expired"""
        with self.lock:
            if key not in self.cache:
                return None

            # Check TTL
            if time.time() - self.timestamps[key] > self.ttl_seconds:
                del self.cache[key]
                del self.timestamps[key]
                return None

            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: str, value: Any) -> None:
        """Put value in cache"""
        with self.lock:
            if key in self.cache:
                self.cache.move_to_end(key)
            else:
                if len(self.cache) >= self.max_size:
                    # Remove oldest item
                    oldest_key = next(iter(self.cache))
                    del self.cache[oldest_key]
                    del self.timestamps[oldest_key]

            self.cache[key] = value
            self.timestamps[key] = time.time()

    def clear(self) -> None:
        """Clear all cache"""
        with self.lock:
            self.cache.clear()
            self.timestamps.clear()


# Global cache instance
_response_cache = LRUCache(max_size=100, ttl_seconds=3600)


def cache_response(func: Callable) -> Callable:
    """
    Decorator to cache function responses based on input hash

    Usage:
        @cache_response
        def expensive_llm_call(text, model):
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Create cache key from function name and arguments
        cache_key = _create_cache_key(func.__name__, args, kwargs)

        # Try to get from cache
        cached_result = _response_cache.get(cache_key)
        if cached_result is not None:
            return cached_result

        # Call function
        result = func(*args, **kwargs)

        # Store in cache
        _response_cache.put(cache_key, result)

        return result

    return wrapper


def _create_cache_key(func_name: str, args: tuple, kwargs: dict) -> str:
    """Create unique cache key from function arguments"""
    # Convert args and kwargs to JSON string
    key_data = {
        'func': func_name,
        'args': str(args),
        'kwargs': json.dumps(kwargs, sort_keys=True, default=str)
    }
    key_str = json.dumps(key_data, sort_keys=True)

    # Hash for efficient key
    return hashlib.md5(key_str.encode()).hexdigest()


class BatchProcessor:
    """
    Batch processor for LLM API calls

    Collects multiple requests and processes them together
    to reduce API overhead and improve throughput
    """

    def __init__(self, max_batch_size: int = 10, max_wait_ms: int = 100):
        self.max_batch_size = max_batch_size
        self.max_wait_ms = max_wait_ms
        self.queue: List[Tuple[str, asyncio.Future]] = []
        self.lock = asyncio.Lock()
        self.processor_task: Optional[asyncio.Task] = None

    async def add_request(self, text: str) -> Any:
        """Add request to batch queue"""
        future = asyncio.Future()

        async with self.lock:
            self.queue.append((text, future))

            # Start processor if not running
            if self.processor_task is None or self.processor_task.done():
                self.processor_task = asyncio.create_task(self._process_batch())

        return await future

    async def _process_batch(self):
        """Process batch of requests"""
        # Wait for batch to fill or timeout
        start_time = time.time()
        while len(self.queue) < self.max_batch_size:
            if (time.time() - start_time) * 1000 >= self.max_wait_ms:
                break
            await asyncio.sleep(0.01)

        # Get batch
        async with self.lock:
            batch = self.queue[:self.max_batch_size]
            self.queue = self.queue[self.max_batch_size:]

        if not batch:
            return

        # Process batch (override in subclass)
        results = await self._process_batch_impl([text for text, _ in batch])

        # Set results
        for (text, future), result in zip(batch, results):
            future.set_result(result)

    async def _process_batch_impl(self, texts: List[str]) -> List[Any]:
        """Override this method to implement actual batch processing"""
        raise NotImplementedError


class ParallelToolExecutor:
    """
    Execute multiple independent tools in parallel

    Example:
        executor = ParallelToolExecutor(max_workers=4)
        results = executor.execute_parallel([
            (fingerprint_remover.process, {'text': text1}),
            (burstiness_enhancer.process, {'text': text2}),
            (imperfection_injector.process, {'text': text3}),
        ])
    """

    def __init__(self, max_workers: int = 4):
        self.max_workers = max_workers

    def execute_parallel(
        self,
        tasks: List[Tuple[Callable, Dict[str, Any]]]
    ) -> List[Any]:
        """
        Execute tasks in parallel

        Args:
            tasks: List of (function, kwargs) tuples

        Returns:
            List of results in same order as tasks
        """
        results = [None] * len(tasks)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_index = {
                executor.submit(func, **kwargs): idx
                for idx, (func, kwargs) in enumerate(tasks)
            }

            # Collect results
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    results[idx] = {'error': str(e)}

        return results


class StreamingProcessor:
    """
    Process large documents in streaming fashion

    Instead of loading entire document into memory,
    process it in chunks to reduce memory footprint
    """

    def __init__(self, chunk_size: int = 5000):
        """
        Args:
            chunk_size: Number of characters per chunk
        """
        self.chunk_size = chunk_size

    def process_stream(
        self,
        text: str,
        processor: Callable[[str], Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process text in streaming chunks

        Args:
            text: Input text
            processor: Function that processes each chunk

        Returns:
            List of chunk results
        """
        chunks = self._chunk_text(text)
        results = []

        for chunk in chunks:
            result = processor(chunk)
            results.append(result)

        return results

    def _chunk_text(self, text: str) -> List[str]:
        """Split text into chunks at sentence boundaries"""
        chunks = []
        current_chunk = ""

        # Split into sentences
        import re
        sentences = re.split(r'(?<=[.!?])\s+', text)

        for sentence in sentences:
            # If adding this sentence exceeds chunk size, save current chunk
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence

        # Add remaining chunk
        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks


class PerformanceMonitor:
    """
    Monitor and track performance metrics

    Tracks:
    - API call latencies
    - Cache hit rates
    - Tool execution times
    - Memory usage
    """

    def __init__(self):
        self.metrics: Dict[str, List[float]] = {}
        self.cache_hits = 0
        self.cache_misses = 0
        self.lock = threading.Lock()

    def record_latency(self, operation: str, duration_ms: float):
        """Record operation latency"""
        with self.lock:
            if operation not in self.metrics:
                self.metrics[operation] = []
            self.metrics[operation].append(duration_ms)

    def record_cache_hit(self):
        """Record cache hit"""
        with self.lock:
            self.cache_hits += 1

    def record_cache_miss(self):
        """Record cache miss"""
        with self.lock:
            self.cache_misses += 1

    def get_stats(self) -> Dict[str, Any]:
        """Get performance statistics"""
        with self.lock:
            stats = {}

            # Calculate latency stats
            for op, latencies in self.metrics.items():
                if latencies:
                    stats[op] = {
                        'count': len(latencies),
                        'avg_ms': sum(latencies) / len(latencies),
                        'min_ms': min(latencies),
                        'max_ms': max(latencies),
                        'p95_ms': self._percentile(latencies, 95),
                        'p99_ms': self._percentile(latencies, 99)
                    }

            # Cache stats
            total_cache_ops = self.cache_hits + self.cache_misses
            if total_cache_ops > 0:
                stats['cache'] = {
                    'hits': self.cache_hits,
                    'misses': self.cache_misses,
                    'hit_rate': self.cache_hits / total_cache_ops
                }

            return stats

    @staticmethod
    def _percentile(values: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not values:
            return 0
        sorted_values = sorted(values)
        index = int((percentile / 100) * len(sorted_values))
        return sorted_values[min(index, len(sorted_values) - 1)]


# Global performance monitor
_performance_monitor = PerformanceMonitor()


def measure_performance(operation_name: str):
    """
    Decorator to measure function performance

    Usage:
        @measure_performance("paraphraser")
        def process(text):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            duration_ms = (time.time() - start_time) * 1000
            _performance_monitor.record_latency(operation_name, duration_ms)
            return result
        return wrapper
    return decorator


def get_performance_stats() -> Dict[str, Any]:
    """Get global performance statistics"""
    return _performance_monitor.get_stats()


def clear_cache():
    """Clear response cache"""
    _response_cache.clear()


# Optimization recommendations based on document size
def get_optimization_strategy(text_length: int) -> Dict[str, Any]:
    """
    Get recommended optimization strategy based on document size

    Args:
        text_length: Length of text in characters

    Returns:
        Dict with optimization recommendations
    """
    if text_length < 5000:
        # Small document: Process normally
        return {
            'strategy': 'normal',
            'use_streaming': False,
            'use_batching': False,
            'chunk_size': None,
            'batch_size': None
        }
    elif text_length < 50000:
        # Medium document: Use parallel processing
        return {
            'strategy': 'parallel',
            'use_streaming': False,
            'use_batching': True,
            'chunk_size': None,
            'batch_size': 10
        }
    else:
        # Large document: Use streaming + parallel
        return {
            'strategy': 'streaming',
            'use_streaming': True,
            'use_batching': True,
            'chunk_size': 5000,
            'batch_size': 10
        }
