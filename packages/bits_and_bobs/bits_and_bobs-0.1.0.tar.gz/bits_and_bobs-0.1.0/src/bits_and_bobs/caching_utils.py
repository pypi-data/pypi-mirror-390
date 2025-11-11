"""Functions related to caching."""

import typing as t
from functools import wraps

T = t.TypeVar("T", bound=object)


def cache_arguments(
    *arguments: str, disable_condition: t.Callable[[], bool] = lambda: False
) -> t.Callable[[t.Callable[..., T]], t.Callable[..., T]]:
    """Cache specified arguments of a function.

    This extends `functools.cache` by allowing selective caching based on
    specific arguments. If no arguments are specified, all arguments are cached.

    Args:
        arguments:
            The list of argument names to cache. If empty, all arguments are cached.
        disable_condition:
            A function that checks if cache should be disabled.

    Returns:
        A decorator that caches the specified arguments of a function.

    Example:
        Here is a basic example of how to use the `cache_arguments` decorator:
        >>> @cache_arguments("x", "y")
        ... def add(x: int, y: int, z: int) -> int:
        ...     print("Computing...")
        ...     return x + y + z
        >>> # First call with (1, 2, 3) computes the result
        >>> add(1, 2, 3)
        Computing...
        6
        >>> # Second call with same (1, 2) but different z uses cache
        >>> add(1, 2, 4)
        6
        >>> # Also works if we use keyword arguments
        >>> add(x=1, y=2, z=5)
        6
        >>> # Call with different (2, 3) computes the result
        >>> add(2, 3, 4)
        Computing...
        9

        If no arguments are specified, all arguments are cached:
        >>> @cache_arguments()
        ... def subtract(a: int, b: int) -> int:
        ...     print("Computing...")
        ...     return a - b
        >>> subtract(5, 3)
        Computing...
        2
        >>> subtract(5, 3)
        2

        Here is an example demonstrating the use of `disable_condition` to
        conditionally disable caching:
        >>> @cache_arguments(
        ...     "x", "y", disable_condition=lambda: os.getenv("DISABLE_CACHE") == "1"
        ... )
        ... def multiply(x: int, y: int, z: int) -> int:
        ...     print("Computing...")
        ...     return x * y * z
        >>> # Cache is disabled if DISABLE_CACHE environment variable is set to "1"
        >>> import os
        >>> os.environ["DISABLE_CACHE"] = "1"
        >>> multiply(2, 3, 4)
        Computing...
        24
        >>> multiply(2, 3, 5)
        Computing...
        30
        >>> # Cache is enabled when DISABLE_CACHE is not "1"
        >>> os.environ["DISABLE_CACHE"] = "0"
        >>> multiply(2, 3, 4)
        Computing...
        24
        >>> multiply(2, 3, 5)
        24

        If you specify arguments that do not exist in the function signature,
        a ValueError is raised:
        >>> @cache_arguments("a", "b")
        ... def divide(x: int, y: int) -> float:
        ...     return x / y
        >>> divide(4, 2)
        Traceback (most recent call last):
        ...
        ValueError: Argument a not found in function divide parameters.
    """

    def caching_decorator(func: t.Callable[..., T]) -> t.Callable[..., T]:
        """Decorator that caches the specified arguments of a function.

        Args:
            func:
                The function to decorate.

        Returns:
            The decorated function.
        """
        cache: dict[tuple, T] = dict()

        @wraps(wrapped=func)
        def wrapper(*args, **kwargs) -> T:
            """Wrapper function that caches the specified arguments.

            Args:
                *args:
                    The positional arguments to the function.
                **kwargs:
                    The keyword arguments to the function.

            Returns:
                The result of the function.

            Raises:
                ValueError:
                    If an argument name is not found in the function parameters.
            """
            if not arguments:
                key = args + tuple(kwargs[k] for k in sorted(kwargs.keys()))
            else:
                func_params = func.__code__.co_varnames
                key_items: list[t.Any] = list()
                for arg_name in arguments:
                    if arg_name in kwargs:
                        key_items.append(kwargs[arg_name])
                    else:
                        try:
                            arg_index = func_params.index(arg_name)
                            key_items.append(args[arg_index])
                        except (ValueError, IndexError):
                            raise ValueError(
                                f"Argument {arg_name} not found in function "
                                f"{func.__name__} parameters."
                            )
                key = tuple(key_items)

            # Get the function value
            if disable_condition() or key not in cache:
                value = func(*args, **kwargs)
            else:
                value = cache[key]

            # Cache the value if not already cached and caching is not disabled
            if key not in cache and not disable_condition():
                cache[key] = value

            return value

        return wrapper

    return caching_decorator
