"""Educational content generation agents using OpenAI."""

__version__ = "0.9.0"

from .core import BasicAgent, tool_emit, tool_event_cb
from .eval import EvalAgent
from .generator import GeneratorAgent

__all__ = [
    'GeneratorAgent',
    'EvalAgent',
    'tool_emit',
    'tool_event_cb',
    'BasicAgent'
]
