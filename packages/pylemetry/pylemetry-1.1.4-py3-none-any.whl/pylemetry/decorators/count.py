from typing import Callable, Optional, ParamSpec, TypeVar

from functools import wraps

from pylemetry import registry
from pylemetry.meters import Counter


P = ParamSpec("P")
R = TypeVar("R", covariant=True)


def count(name: Optional[str] = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to count the number of invocations of a given callable. Creates a Counter meter in the Registry
    with either the provided name or the fully qualified name of the callable object as the metric name.

    :param name: Name of the meter to create, if None the function name is used
    :return: Result of the wrapped function
    """

    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            counter_name = f.__qualname__ if name is None else name

            counter = registry.get_counter(counter_name)

            if not counter:
                counter = Counter()
                registry.add_counter(counter_name, counter)

            counter += 1

            return f(*args, **kwargs)

        return wrapper

    return decorator
