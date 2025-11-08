"""
Performance tracking utilities for MassGen coordination system.

This module provides lightweight timing decorators and context managers
for tracking performance metrics during agent coordination.
"""

import time
import functools
from contextlib import asynccontextmanager
from typing import Optional, Any, Callable, Dict
from uuid import uuid4


class PerformanceTimer:
    """Simple context manager for timing code blocks."""

    def __init__(self, name: str = "operation"):
        self.name = name
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.duration: Optional[float] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        return False

    async def __aenter__(self):
        self.start_time = time.time()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        self.duration = self.end_time - self.start_time
        return False


def track_latency(func: Callable) -> Callable:
    """
    Decorator for tracking latency of async functions.

    Adds timing information to the function's return value if it's a dictionary.
    Otherwise, logs the timing information.

    Args:
        func: The async function to decorate

    Returns:
        Decorated function that tracks execution time

    Example:
        >>> @track_latency
        >>> async def process_data(data):
        >>>     await asyncio.sleep(1)
        >>>     return {"result": "processed"}
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time

            # If result is a dict, add timing info
            if isinstance(result, dict):
                result['_timing'] = {
                    'duration': duration,
                    'function': func.__name__
                }

            return result
        except Exception as e:
            duration = time.time() - start_time
            # Re-raise with timing context
            raise

    return wrapper


@asynccontextmanager
async def track_activity(tracker: Any, agent_id: Optional[str], activity_type: str):
    """
    Async context manager for tracking activity duration in CoordinationTracker.

    Args:
        tracker: CoordinationTracker instance
        agent_id: ID of the agent performing the activity (None for orchestrator-level)
        activity_type: Type of activity being tracked (e.g., "answer_generation", "voting")

    Yields:
        activity_id: Unique identifier for this activity instance

    Example:
        >>> async with track_activity(tracker, "agent_1", "answer_generation") as activity_id:
        >>>     # Do work...
        >>>     await generate_answer()
        >>> # Activity duration automatically recorded in tracker
    """
    activity_id = str(uuid4())

    # Start tracking
    if hasattr(tracker, 'start_activity'):
        tracker.start_activity(activity_id, agent_id, activity_type)

    try:
        yield activity_id
    finally:
        # End tracking
        if hasattr(tracker, 'end_activity'):
            tracker.end_activity(activity_id)


def calculate_statistics(durations: list[float]) -> Dict[str, float]:
    """
    Calculate statistical measures for a list of durations.

    Args:
        durations: List of duration values in seconds

    Returns:
        Dictionary containing min, max, mean, median, and total
    """
    if not durations:
        return {
            'min': 0.0,
            'max': 0.0,
            'mean': 0.0,
            'median': 0.0,
            'total': 0.0,
            'count': 0
        }

    sorted_durations = sorted(durations)
    count = len(durations)
    total = sum(durations)
    mean = total / count

    # Calculate median
    if count % 2 == 0:
        median = (sorted_durations[count // 2 - 1] + sorted_durations[count // 2]) / 2
    else:
        median = sorted_durations[count // 2]

    return {
        'min': min(durations),
        'max': max(durations),
        'mean': mean,
        'median': median,
        'total': total,
        'count': count
    }
