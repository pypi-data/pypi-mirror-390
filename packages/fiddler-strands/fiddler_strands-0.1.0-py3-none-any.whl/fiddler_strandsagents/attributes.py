import asyncio
import contextvars
from typing import Union

from pydantic import ConfigDict, validate_call
from strands import Agent
from strands.models import Model
from strands.types.tools import AgentTool


def _in_asyncio_context() -> bool:
    try:
        asyncio.get_running_loop()
        return True
    except RuntimeError:
        return False


@validate_call(config=ConfigDict(arbitrary_types_allowed=True))
def set_span_attributes(
    obj: Union[Model, AgentTool], **kwargs: Union[str, int, float, bool]
) -> None:
    """
    Set a custom attribute on an Model & AgentTool that can be accessed by logging hooks.

    This function stores key-value pairs as attributes on the object, making
    them accessible to hooks during model invocation events.

    Args:
        obj: The object to set the attribute on (typically a model or tool)
        **kwargs: Key-value pairs of attributes to set
    """
    if _in_asyncio_context():
        if not hasattr(obj, '_async_fiddler_span_attributes'):
            setattr(
                obj,
                '_async_fiddler_span_attributes',
                contextvars.ContextVar('_async_fiddler_span_attributes', default={}),
            )
        context_var = getattr(obj, '_async_fiddler_span_attributes')
        updated_attributes = context_var.get().copy()
        updated_attributes.update(kwargs)
        context_var.set(updated_attributes)
    else:
        if not hasattr(obj, '_sync_fiddler_span_attributes'):
            setattr(obj, '_sync_fiddler_span_attributes', {})
        getattr(obj, '_sync_fiddler_span_attributes').update(kwargs)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_span_attributes(
    obj: Union[Model, AgentTool],
) -> dict[str, Union[str, int, float, bool]]:
    """Get span attributes from an object."""
    if _in_asyncio_context() and hasattr(obj, '_async_fiddler_span_attributes'):
        return obj._async_fiddler_span_attributes.get().copy()
    if hasattr(obj, '_sync_fiddler_span_attributes'):
        return obj._sync_fiddler_span_attributes
    return {}


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def set_conversation_id(agent: Agent, conversation_id: str) -> None:
    """Set the conversation ID for the current application invocation.
    This will remain in use until it is called again with a new conversation ID.
    """
    if _in_asyncio_context():
        if not hasattr(agent, '_async_fiddler_conversation_id'):
            setattr(
                agent,
                '_async_fiddler_conversation_id',
                contextvars.ContextVar('_async_fiddler_conversation_id', default=''),
            )
        getattr(agent, '_async_fiddler_conversation_id').set(conversation_id)
    else:
        setattr(agent, '_sync_fiddler_conversation_id', conversation_id)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_conversation_id(agent: Agent) -> str:
    """Get the conversation ID for the current application invocation.
    This will remain in use until it is called again with a new conversation ID.
    This is only used in synchronous contexts. Use async_get_conversation_id for asynchronous contexts.
    """
    if _in_asyncio_context() and hasattr(agent, '_async_fiddler_conversation_id'):
        try:
            return agent._async_fiddler_conversation_id.get()
        except LookupError:
            pass
    if hasattr(agent, '_sync_fiddler_conversation_id'):
        return agent._sync_fiddler_conversation_id
    return ''


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def set_session_attributes(
    agent: Agent, **kwargs: Union[str, int, float, bool]
) -> None:
    """Adds Fiddler-specific attributes to a runnable's metadata."""
    if _in_asyncio_context():
        if not hasattr(agent, '_async_fiddler_session_attributes'):
            setattr(
                agent,
                '_async_fiddler_session_attributes',
                contextvars.ContextVar('_async_fiddler_session_attributes', default={}),
            )
        context_var = getattr(agent, '_async_fiddler_session_attributes')
        updated_attributes = context_var.get().copy()
        updated_attributes.update(kwargs)
        context_var.set(updated_attributes)
    else:
        if not hasattr(agent, '_sync_fiddler_session_attributes'):
            setattr(agent, '_sync_fiddler_session_attributes', {})
        getattr(agent, '_sync_fiddler_session_attributes').update(kwargs)


@validate_call(config=ConfigDict(strict=True, arbitrary_types_allowed=True))
def get_session_attributes(
    agent: Agent,
) -> dict[str, Union[str, int, float, bool]]:
    """Get the session attributes for the current application invocation."""
    if _in_asyncio_context() and hasattr(agent, '_async_fiddler_session_attributes'):
        return agent._async_fiddler_session_attributes.get().copy()

    if hasattr(agent, '_sync_fiddler_session_attributes'):
        return agent._sync_fiddler_session_attributes

    return {}
