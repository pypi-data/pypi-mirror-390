"""Singleton pattern decorators for class instantiation."""

from typing import Any, Callable, Dict, Type, TypeVar

__all__ = (
    "singleton_class",
    "singleton_class_by_args",
)

T = TypeVar("T")


def singleton_class(cls: Type[T]) -> Callable[..., T]:
    """Decorator ensuring a class has only one instance regardless of
    arguments.

    Description:
        Creates a singleton pattern where only one instance of the class
        exists, even if instantiated with different arguments. Subsequent
        calls return the same instance created by the first call.

    Args:
        cls: The class to convert to a singleton.

    Returns:
        A function that returns the singleton instance.
    """
    instances: Dict[Type[T], T] = {}

    def get_instance(*args: Any, **kwargs: Any) -> T:
        """Return the singleton instance, creating it if necessary.

        Args:
            *args: Positional arguments for class constructor (ignored after first call).
            **kwargs: Keyword arguments for class constructor (ignored after first call).

        Returns:
            The single shared instance of the class.
        """
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance


def singleton_class_by_args(cls: Type[T]) -> Callable[..., T]:
    """Decorator ensuring one instance per unique set of constructor arguments.

    Description:
        Creates a singleton-like pattern where instances are cached based on
        their constructor arguments. Each unique combination of arguments
        results in one cached instance that is reused for matching calls.

    Args:
        cls: The class to apply argument-based singleton behavior to.

    Returns:
        A function that returns instances cached by arguments.
    """
    instances: Dict[Any, T] = {}

    def get_instance(*args: Any, **kwargs: Any) -> T:
        """Return an instance unique to the given arguments.

        Args:
            *args: Positional arguments for class constructor.
            **kwargs: Keyword arguments for class constructor.

        Returns:
            An instance of the class unique to this combination of arguments.
        """
        # Create a unique key based on the arguments
        key = (args, frozenset(kwargs.items()))
        if key not in instances:
            instances[key] = cls(*args, **kwargs)
        return instances[key]

    return get_instance
