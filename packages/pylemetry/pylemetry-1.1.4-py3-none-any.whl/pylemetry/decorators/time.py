from typing import Callable, Optional, ParamSpec, TypeVar

from functools import wraps

from pylemetry import registry
from pylemetry.meters import Timer


P = ParamSpec("P")
R = TypeVar("R", covariant=True)


def time(name: Optional[str] = None) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """
    Decorator to time the invocations of a given callable. Creates a Timer meter in the Registry with either the
    provided name or the fully qualified name of the callable object as the metric name.

    :param name: Name of the meter to create, if None the function name is used
    :return: Result of the wrapped function
    """

    def decorator(f: Callable[P, R]) -> Callable[P, R]:
        @wraps(f)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            time_name = f.__qualname__ if name is None else name

            _timer = registry.get_timer(time_name)

            if not _timer:
                _timer = Timer()
                registry.add_timer(time_name, _timer)

            with _timer.time():
                return f(*args, **kwargs)

        return wrapper

    return decorator
