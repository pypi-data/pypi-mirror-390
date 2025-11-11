from __future__ import annotations

from typing import Callable, Any
from edu_agents.core.runnable_agent import RunnableAgent

class BasicAgent(RunnableAgent):
    """Simple agent that uses the base o3 model without tools or special instructions."""

    def __init__(self, *, model: str = "o3", on_event: Callable[[str, Any], None] = None, conversation_id: str | None = None, user_id: str = None, amq_json_format: bool = False, request_id: str = None, cancellation_flag = None) -> None:
        # Simple system prompt without special instructions
        system_prompt = "You are a helpful AI assistant that answers questions accurately and honestly."
        
        # Initialize without any files
        super().__init__(model=model, system_prompt=system_prompt, files=None, on_event=on_event, conversation_id=conversation_id, user_id=user_id, amq_json_format=amq_json_format, request_id=request_id, cancellation_flag=cancellation_flag)
        
        # No tools are added to keep it simple 