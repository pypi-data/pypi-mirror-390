"""
Hook providers for Strands Agent instrumentation.

This module contains various hook implementations that can be used
with Strands agents for logging, monitoring, and observability.
"""

from opentelemetry import trace
from strands.experimental.hooks import (
    AfterModelInvocationEvent,
    AfterToolInvocationEvent,
)
from strands.hooks import BeforeInvocationEvent, HookProvider, HookRegistry

from fiddler_strandsagents.attributes import (
    get_conversation_id,
    get_session_attributes,
    get_span_attributes,
)
from fiddler_strandsagents.constants import (
    FIDDLER_CONVERSATION_ID,
    FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE,
)


class FiddlerInstrumentationHook(HookProvider):
    """
    Centralized logging hook that can be automatically injected into
    all agents for basic observability.
    """

    def register_hooks(self, registry: HookRegistry, **kwargs) -> None:
        """Register the hook callbacks with the registry."""
        registry.add_callback(AfterToolInvocationEvent, self.tool_end)
        registry.add_callback(AfterModelInvocationEvent, self.model_end)
        registry.add_callback(BeforeInvocationEvent, self.before_invocation)

    def tool_end(self, event: AfterToolInvocationEvent) -> None:
        """Handle the end of a tool invocation event."""
        if not event.selected_tool:
            return

        tool_attributes = get_span_attributes(event.selected_tool)
        if tool_attributes:
            current_tool_span = trace.get_current_span()

            attributes = {
                f'fiddler.span.user.{k}': v for k, v in tool_attributes.items()
            }
            current_tool_span.set_attributes(attributes)

    def model_end(self, event: AfterModelInvocationEvent) -> None:
        """Handle the end of a model invocation event."""
        # Access model attributes that were set using set_attribute
        model_attributes = get_span_attributes(event.agent.model)
        current_model_span = trace.get_current_span()
        if model_attributes:
            attributes = {
                f'fiddler.span.user.{k}': v for k, v in model_attributes.items()
            }
            current_model_span.set_attributes(attributes)

    def before_invocation(self, event: BeforeInvocationEvent) -> None:
        """Handle the before of an invocation event."""

        # Set the conversation ID from sync variable first
        conversation_id = get_conversation_id(event.agent)
        session_attributes = get_session_attributes(event.agent)
        current_span = trace.get_current_span()
        if conversation_id:
            current_span.set_attribute(FIDDLER_CONVERSATION_ID, conversation_id)
        if session_attributes:
            current_span.set_attributes(
                {
                    FIDDLER_USER_SESSION_ATTRIBUTE_TEMPLATE.format(key=k): v
                    for k, v in session_attributes.items()
                }
            )
