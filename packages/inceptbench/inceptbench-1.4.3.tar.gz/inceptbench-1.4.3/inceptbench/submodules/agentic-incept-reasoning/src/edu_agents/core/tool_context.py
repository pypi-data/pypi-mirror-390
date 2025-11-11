"""
A thread-/task-local hook that tools can use to publish streaming events
back to the generator (which, in turn, ships them to the CLI).

Also provides request_id context for tools that need to access the current request ID
for logging and tracking purposes.

Usage:

    from edu_agents.tool_context import tool_event_cb, tool_emit, request_id_context, get_current_request_id

    async with request_id_context(request_id):
        with tool_event_cb(my_callback):
            result = some_tool()

Inside *some_tool* you can now do:

    tool_emit("tool_output_delta", "some text")
    request_id = get_current_request_id()
"""
from __future__ import annotations
import contextvars
from contextlib import asynccontextmanager, contextmanager
from typing import Any, Callable, Optional

_event_cb: contextvars.ContextVar[Callable[[str, Any], None] | None] = (
    contextvars.ContextVar("_event_cb", default=None)
)


@contextmanager
def tool_event_cb(cb: Callable[[str, Any], None]):
    token = _event_cb.set(cb)
    try:
        yield
    finally:
        _event_cb.reset(token)


def tool_emit(event: str, data: Any):
    cb = _event_cb.get()
    if cb is not None:
        cb(event, data)


# Context variable for request ID
_request_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    '_request_id', default=None
)


@asynccontextmanager
async def request_id_context(request_id: Optional[str]):
    """
    Context manager to set request ID for tools to access.
    
    This allows tools to access the current request ID for logging and tracking
    without requiring it as an explicit parameter. The request_id remains constant
    throughout a single API invocation, even across multiple internal QC iterations.
    
    Parameters
    ----------
    request_id : Optional[str]
        The request ID to make available to tools, or None if not tracking
        
    Examples
    --------
    >>> async with request_id_context("req_123"):
    ...     # Tools can now access request_id via get_current_request_id()
    ...     result = await some_tool()
    """
    token = _request_id.set(request_id)
    try:
        yield
    finally:
        _request_id.reset(token)


def get_current_request_id() -> Optional[str]:
    """
    Get the current request ID from context.
    
    Returns the request ID that was set via request_id_context(), or None if
    no request ID has been set. This allows tools to access the request ID for
    logging purposes without it being an explicit parameter.
    
    Returns
    -------
    Optional[str]
        The current request ID, or None if not in a request context
        
    Examples
    --------
    >>> request_id = get_current_request_id()
    >>> if request_id:
    ...     logger.info(f"Processing request {request_id}")
    """
    return _request_id.get() 