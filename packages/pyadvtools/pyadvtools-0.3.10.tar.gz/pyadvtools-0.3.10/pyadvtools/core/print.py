import time
from collections.abc import Callable
from functools import wraps


def print_run_time(func: Callable) -> Callable:
    """Decorator to measure and print function execution time.

    A decorator that wraps a function to measure its execution time and
    print the result. The timing is measured in seconds and displayed
    with the function name.

    Args:
        func: The function to be decorated.

    Returns:
        function: Wrapped function that prints execution time.

    Examples:
        >>> @print_run_time
        ... def slow_function():
        ...     time.sleep(1)
        ...     return "done"
        >>> result = slow_function()
        Run time for slow_function: 1.000123
        >>> result
        'done'
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        print(f"Run time for {func.__name__}: {time.time() - start_time}")
        return result

    return wrapper


if __name__ == "__main__":
    pass
