"""
Timing decorators for performance measurement.

Usage:
    from backend.decorators.timeit import time_node, get_timings, clear_timings
    
    @time_node
    def my_function(state):
        ...
"""
import time
import functools
import threading
from typing import Dict, Callable, Any
import json
import logging

# Thread-local storage for per-request timings
_timing_storage = threading.local()

def _get_storage() -> Dict[str, float]:
    """Get thread-local timing storage."""
    if not hasattr(_timing_storage, 'timings'):
        _timing_storage.timings = {}
    return _timing_storage.timings


def clear_timings():
    """Clear all recorded timings for current thread."""
    _timing_storage.timings = {}


def get_timings() -> Dict[str, float]:
    """Get all recorded timings for current thread."""
    return dict(_get_storage())


def time_node(func: Callable = None, *, name: str = None):
    """
    Decorator to time a node function and store timing.
    
    Usage:
        @time_node
        def classify_intent(state):
            ...
            
        @time_node(name="custom_name")
        def my_func(state):
            ...
    """
    def decorator(fn: Callable) -> Callable:
        node_name = name or fn.__name__
        
        @functools.wraps(fn)
        def wrapper(*args, **kwargs) -> Any:
            start = time.perf_counter()
            try:
                result = fn(*args, **kwargs)
                return result
            finally:
                elapsed = time.perf_counter() - start
                storage = _get_storage()
                storage[node_name] = elapsed
                
                # Log structured timing info
                timing_log = {
                    "event": "node_timing",
                    "node": node_name,
                    "elapsed_ms": round(elapsed * 1000, 2),
                }
                logging.debug(json.dumps(timing_log))
        
        return wrapper
    
    if func is not None:
        # Called without arguments: @time_node
        return decorator(func)
    # Called with arguments: @time_node(name="...")
    return decorator


def timed_context(name: str):
    """
    Context manager for timing arbitrary code blocks.
    
    Usage:
        with timed_context("db_query"):
            result = db.query(...)
    """
    class TimedContext:
        def __enter__(self):
            self.start = time.perf_counter()
            return self
        
        def __exit__(self, *args):
            elapsed = time.perf_counter() - self.start
            storage = _get_storage()
            storage[name] = elapsed
    
    return TimedContext()


def log_all_timings():
    """Log all timings as structured JSON."""
    timings = get_timings()
    if timings:
        total = sum(timings.values())
        log_data = {
            "event": "request_timings",
            "total_ms": round(total * 1000, 2),
            "nodes": {k: round(v * 1000, 2) for k, v in timings.items()}
        }
        logging.info(json.dumps(log_data))
