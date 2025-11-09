"""
Side-channel protection utilities.

Wrappers and utilities to protect against timing, cache, and other side-channel attacks.
"""

import time
from typing import Callable, Any
from csf.utils.exceptions import SecurityError


def timing_safe_operation(func: Callable, *args, min_time: float = 0.0, **kwargs) -> Any:
    """
    Execute a function with minimum execution time to reduce timing attacks.

    Note: This is a best-effort approach. True constant-time requires careful
    implementation at the algorithm level.

    Args:
        func: Function to execute
        *args: Positional arguments
        min_time: Minimum execution time in seconds
        **kwargs: Keyword arguments

    Returns:
        Function result
    """
    start_time = time.perf_counter()
    result = func(*args, **kwargs)
    elapsed = time.perf_counter() - start_time

    if elapsed < min_time:
        # Sleep to meet minimum time (best effort, not perfect)
        time.sleep(min_time - elapsed)

    return result


def check_constant_time(func: Callable, test_cases: list, max_time_variation: float = 0.1) -> bool:
    """
    Check if a function executes in approximately constant time.

    This is a basic check and not a formal proof.

    Args:
        func: Function to test
        test_cases: List of test case inputs
        max_time_variation: Maximum allowed coefficient of variation

    Returns:
        True if appears constant-time, False otherwise
    """
    if len(test_cases) < 2:
        return True

    execution_times = []

    for test_input in test_cases:
        start = time.perf_counter()
        func(test_input)
        elapsed = time.perf_counter() - start
        execution_times.append(elapsed)

    # Calculate coefficient of variation
    mean_time = sum(execution_times) / len(execution_times)
    variance = sum((t - mean_time) ** 2 for t in execution_times) / len(execution_times)
    std_dev = variance**0.5

    if mean_time == 0:
        return True

    coefficient_of_variation = std_dev / mean_time

    return coefficient_of_variation < max_time_variation


class SideChannelProtection:
    """
    Context manager for side-channel protection.

    Attempts to ensure constant-time execution of code block.
    """

    def __init__(self, min_execution_time: float = 0.0):
        """
        Initialize side-channel protection.

        Args:
            min_execution_time: Minimum execution time to enforce
        """
        self.min_time = min_execution_time
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start_time

        if elapsed < self.min_time:
            time.sleep(self.min_time - elapsed)

        return False  # Don't suppress exceptions


def mask_secret(secret: int, mask: int) -> int:
    """
    Apply a mask to a secret value.

    Args:
        secret: Secret value
        mask: Mask to apply

    Returns:
        Masked value
    """
    return secret ^ mask


def unmask_secret(masked: int, mask: int) -> int:
    """
    Remove mask from a masked secret value.

    Args:
        masked: Masked value
        mask: Mask that was applied

    Returns:
        Unmasked secret
    """
    return masked ^ mask
