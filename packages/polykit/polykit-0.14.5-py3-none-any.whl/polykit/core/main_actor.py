"""This is completely ridiculous and slightly insane, but I'm creating it to help me learn Swift."""

from __future__ import annotations

import threading
from functools import wraps
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


class MainActorHelper:
    """Main actor is a thread-safe actor that runs on the main thread."""

    def __init__(self):
        self._lock = threading.Lock()
        self._main_thread = threading.current_thread()

    def run(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Run a function on the main thread."""
        if threading.current_thread() == self._main_thread:
            return func(*args, **kwargs)
        with self._lock:
            return func(*args, **kwargs)


# Global main actor instance
main_actor = MainActorHelper()


def MainActor(func: Callable[..., Any]) -> Callable[..., Any]:  # noqa: N802
    """Decorator to run a function on the main thread."""

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        return main_actor.run(func, *args, **kwargs)

    return wrapper
