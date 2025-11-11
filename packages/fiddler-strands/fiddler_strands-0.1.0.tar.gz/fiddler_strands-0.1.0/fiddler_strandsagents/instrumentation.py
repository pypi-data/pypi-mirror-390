#!/usr/bin/env python3
"""
OpenTelemetry instrumentation for automatically injecting logging hooks
into all Strands Agent instances.

This module uses OpenTelemetry's BaseInstrumentor to properly instrument
the Agent class and automatically add LoggingHook to all agents without
requiring manual specification.
"""

import logging
from typing import Collection

from opentelemetry.instrumentation.instrumentor import (  # type: ignore[attr-defined]
    BaseInstrumentor,
)
from strands import Agent
from strands.telemetry import StrandsTelemetry
from wrapt import wrap_function_wrapper

from fiddler_strandsagents.span_processor import FiddlerSpanProcessor

from .hooks import FiddlerInstrumentationHook

logger = logging.getLogger(__name__)


class StrandsAgentInstrumentor(BaseInstrumentor):
    def __init__(self, strands_telemetry: StrandsTelemetry):
        self.strands_telemetry = strands_telemetry
        self._original_agent_init = Agent.__init__
        super().__init__()

    def instrumentation_dependencies(self) -> Collection[str]:
        return ['strands-agents']

    def _instrument(self, **kwargs):
        self.strands_telemetry.tracer_provider.add_span_processor(
            FiddlerSpanProcessor()
        )
        _agent_class = Agent

        wrap_function_wrapper(
            _agent_class,
            '__init__',
            self._patched_agent_init,
        )
        logger.info(
            '🎯 Strands Agent instrumentation enabled - LoggingHook will be injected'
        )

    def _uninstrument(self, **kwargs):
        Agent.__init__ = self._original_agent_init
        logger.info('⚠️ Uninstrumenting Strands Agent instrumentation')

    def _patched_agent_init(self, wrapped, instance, args, kwargs):
        """Patched agent initialization to inject LoggingHook.
        Note that instance argument appears unused but is required by wrapt."""
        existing_hooks = kwargs.get('hooks', [])
        if existing_hooks is None:
            existing_hooks = []

        if not any(isinstance(h, FiddlerInstrumentationHook) for h in existing_hooks):
            existing_hooks.append(FiddlerInstrumentationHook())
            kwargs['hooks'] = existing_hooks

        return wrapped(*args, **kwargs)
