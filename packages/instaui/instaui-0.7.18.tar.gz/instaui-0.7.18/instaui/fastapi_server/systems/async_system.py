import asyncio
from typing import Any, Awaitable, Callable, TypeVar, Union
from fastapi.concurrency import run_in_threadpool

T = TypeVar("T")


async def maybe_async(
    func: Callable[..., Union[T, Awaitable[T]]], *args: Any, **kwargs: Any
) -> T:
    """
    Run a callable that may be synchronous or asynchronous.

    - If `func` is an async function (defined with `async def`), it will be awaited directly.
    - If `func` is a regular (sync) function, it will be executed in a thread pool
      using `fastapi.concurrency.run_in_threadpool()` to avoid blocking the event loop.

    Args:
        func: The function to call. Can be synchronous or asynchronous.
        *args: Positional arguments to pass to the function.
        **kwargs: Keyword arguments to pass to the function.

    Returns:
        The result of calling `func`, regardless of whether it's sync or async.

    Example:
        >>> async def async_add(x, y): return x + y
        >>> def sync_add(x, y): return x + y
        >>> await maybe_async(async_add, 1, 2)
        3
        >>> await maybe_async(sync_add, 1, 2)
        3
    """
    if asyncio.iscoroutinefunction(func):
        return await func(*args, **kwargs)
    return await run_in_threadpool(func, *args, **kwargs)  # type: ignore[return-value]
