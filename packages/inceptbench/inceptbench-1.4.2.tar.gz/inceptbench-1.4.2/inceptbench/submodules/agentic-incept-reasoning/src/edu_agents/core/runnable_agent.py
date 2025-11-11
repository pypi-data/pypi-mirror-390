from __future__ import annotations

import asyncio
import inspect
import json
import logging
import time
from typing import Any, Callable, Dict, Tuple

from edu_agents.core.conversation import Conversation, is_retryable_error
from edu_agents.core.tool_context import request_id_context, tool_event_cb
from edu_agents.tools.amq_converter import AMQConverter

logger = logging.getLogger(__name__)


class RunnableAgent:
    """Base class for agents that can run conversations with tools."""

    def __init__(self, *, model: str, system_prompt: str, files: list[dict] = None,
    on_event: Callable[[str, Any], None] = None, conversation_id: str | None = None,
    user_id: str = None, amq_json_format: bool = False, request_id: str = None,
    effort: str = "medium", is_incept: bool = False, cancellation_flag = None) -> None:
        self.model = model
        self.tool_specs: list[dict] = []
        self.py_tools: Dict[str, Callable] = {}
        self.prompt_description_for_tool_call = "The prompt to send to the agent."
        self.amq_json_format = amq_json_format
        self.request_id = request_id
        self.is_incept = is_incept
        self.cancellation_flag = cancellation_flag

        # Initialize AMQ converter if needed
        if amq_json_format:
            self.amq_converter = AMQConverter()
        else:
            self.amq_converter = None

        self.conv = Conversation(
            model=model,
            system_prompt=system_prompt,
            effort=effort,
            files=files,
            conversation_id=conversation_id,
            user_id=user_id,
            is_incept=is_incept,
        )    
        self.on_event = on_event

    def add_tool(self, tool_spec: dict, tool_fn: Callable) -> None:
        self.tool_specs.append(tool_spec)
        self.py_tools[tool_spec["name"]] = tool_fn

    def as_tool(self) -> Tuple[dict, Callable]:
        """
        Returns the tool specification and callable function for using this agent as a tool.
        This allows one agent to be used as a tool by another agent.
        """
        tool_spec = {
            "type": "function",
            "name": self.__class__.__name__.lower(),
            "description": self.__class__.__doc__ or "No description available.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": self.prompt_description_for_tool_call
                    }
                },
                "required": ["prompt"]
            }
        }

        def tool_fn(prompt: str) -> str:
            self.conv.reset_conversation()
            return self.run(prompt, tool_mode=True)

        return tool_spec, tool_fn

    def emit_event(self, event_type: str, payload: Any) -> None:
        # Ensure payload is always a dictionary with at least a "text" field
        if event_type == "response_final":
            # Include conversation threading info
            payload = {
                "text": payload,
                "conversation_id": self.conv.get_conversation_id(),
            }
        else:
            # For all other event types, wrap non-dict payloads into a dict
            if not isinstance(payload, dict):
                payload = {"text": payload}

        if self.on_event is not None:
            self.on_event(event_type, payload)

    async def run_async(self, user_prompt: str, tool_mode: bool = False) -> str:
        """
        Execute the conversation loop asynchronously, emitting events via self.on_event.

        If tool_mode is True, final output will be emitted as "tool_final".
        Otherwise, it will be emitted as "response_final".

        event_type values:
          • text_delta        – streamed assistant token
          • reasoning_delta   – streamed reasoning token
          • echo_result       – final echo result
          • tool_final        – final tool output
          • response_final    – final model response
          
        Returns
        -------
        str
            The final response text
        """
        # Set request_id in tool context for tools to access (e.g., QC logging)
        # This remains constant throughout the entire API invocation, including all
        # internal QC iterations within the generator agent
        async with request_id_context(self.request_id):
            self.conv.user(user_prompt)

            while True:
                
                # ── 1️⃣  call Responses with streaming ────────────────────
                try:
                    stream = await self._call_with_stream_retry()
                    
                    completed_resp = None
                    async for ev in stream:
                        ev_type = getattr(ev, "type", "")

                        # ---------- streamed assistant text ------------
                        if ev_type in (
                            "response.output_text.delta",
                            "response.output_message.delta",
                        ):
                            self.emit_event("text_delta", ev.delta)

                        # ---------- streamed reasoning summary ---------
                        elif ev_type == "response.reasoning_summary_text.delta":
                            self.emit_event("reasoning_delta", ev.delta)

                        # ---------- streamed reasoning complete ----------------
                        elif ev_type == "response.reasoning_summary_text.done":
                            self.emit_event("reasoning_delta", "\n\n")

                        # ---------- end-of-response --------------------
                        elif ev_type == "response.completed":
                            await asyncio.sleep(1)
                            completed_resp = ev.response

                    # Safety guard – should never happen, but avoid None crash
                    if completed_resp is None:
                        raise RuntimeError(
                            f"Streaming finished without response.completed. Final response event: {ev}"
                        )
                        
                except Exception as e:
                    # Check if this is a retryable streaming error
                    if is_retryable_error(e):
                        logger.warning(
                            f"Retryable streaming error encountered, will retry: {type(e).__name__}: "
                            f"{str(e)}"
                        )
                        # Continue to restart the entire conversation loop with retry
                        continue
                    else:
                        # Non-retryable error, re-raise
                        logger.error(f"Non-retryable streaming error: {type(e).__name__}: {str(e)}")
                        raise

                # ------------------------------------------------------------------
                # 2️⃣  look for a function-call request
                # ------------------------------------------------------------------
                tool_items = [
                    itm
                    for itm in completed_resp.output
                    if getattr(itm, "type", "") == "function_call"
                ]

                if tool_items:
                    # spec guarantees only one tool call
                    tc = tool_items[0]
                    
                    # Handle malformed tool calls with fallbacks
                    tool_name = getattr(tc, 'name', 'unknown_function_name')
                    call_id = getattr(tc, 'call_id', f'unknown_call_{int(time.time() * 1000)}')
                    
                    if not hasattr(tc, 'name'):
                        logger.warning(
                            f"Tool call missing name attribute, using fallback 'unknown_function_name'."
                            f" Tool call: {tc}"
                        )
                    if not hasattr(tc, 'call_id'):
                        logger.warning(
                            f"Tool call missing call_id attribute, using fallback '{call_id}'. Tool "
                            f"call: {tc}"
                        )
                    
                    # `arguments` arrives as JSON-string; turn into dict
                    try:
                        args_dict = (
                            json.loads(tc.arguments) if isinstance(tc.arguments, str) else tc.arguments
                        )
                    except (json.JSONDecodeError, AttributeError):
                        logger.warning(
                            f"Tool call has malformed arguments, using empty dict. Tool: {tool_name}"
                        )
                        args_dict = {}

                    # Handle unknown or missing tools
                    if tool_name not in self.py_tools:
                        if tool_name == "unknown_function_name":
                            logger.warning(
                                f"Executing fallback for unknown function call with call_id: {call_id}"
                            )
                            result = "Error: Unknown function was called. This may indicate " + \
                                     f"corrupted conversation data. Call ID: {call_id}"
                        else:
                            logger.error(
                                f"Unknown tool called: {tool_name}. Available tools: "
                                f"{list(self.py_tools.keys())}"
                            )
                            result = f"Error: Tool '{tool_name}' is not available. Available " + \
                                     f"tools: {', '.join(self.py_tools.keys())}"
                    else:
                        # Execute the actual tool
                        fn = self.py_tools[tool_name]
                        # Stream tool guidance via the shared context
                        with tool_event_cb(self.emit_event):
                            try:
                                # Check if the tool is async and await it if necessary
                                if inspect.iscoroutinefunction(fn):
                                    result = await fn(**args_dict)  # type: ignore
                                else:
                                    result = fn(**args_dict)  # type: ignore
                            except Exception as e:
                                logger.error(f"Error executing tool {tool_name}: {e}")
                                result = f"Error executing {tool_name}: {str(e)}"

                    # 2. Save function call and output atomically to prevent mismatches
                    tool_result = result
                    try:
                        tool_result = result.text
                    except AttributeError:
                        tool_result = result
                    
                    if tc.name == "echo":
                        self.emit_event("echo_result", tool_result)

                    # Use atomic persistence to save both function call and output together
                    # This prevents race conditions under high load that cause mismatch errors
                    try:
                        await self.conv.save_function_call_with_output_atomic(
                            name=tool_name,
                            arguments=getattr(tc, 'arguments', '{}'),
                            call_id=call_id,
                            output=tool_result
                        )
                    except Exception as e:
                        logger.error(f"Failed to save function call {call_id} atomically: {e}")
                        # Fallback to deferred model if atomic save fails
                        self.conv.add_function_call(
                            name=tool_name,
                            arguments=getattr(tc, 'arguments', '{}'),
                            call_id=call_id,
                        )
                        self.conv.tool_result(tc.call_id, tool_result)
                    
                    continue        # restart loop with updated context

                # Otherwise the first assistant-message is the answer
                assistant_msg = next(
                    (
                        itm
                        for itm in completed_resp.output
                        if getattr(itm, "type", "") == "message"
                        and getattr(itm, "role", "") == "assistant"
                    ),
                    None,
                )

                # ── 3️⃣  we're done ───────────────────────────────────────
                if assistant_msg is not None:
                    final_text = "".join(
                        part.text
                        for part in getattr(assistant_msg, "content", [])
                        if hasattr(part, "text")
                    )
                    
                    # Convert to AMQ JSON format if requested
                    if self.amq_json_format and self.amq_converter is not None:
                        max_retries = 3
                        retry_count = 0
                        conversion_start_time = time.time()
                        
                        while retry_count <= max_retries:
                            try:
                                attempt_info = f"(attempt {retry_count + 1}/{max_retries + 1})"
                                logger.info(
                                    f"Converting final response to AMQ JSON format {attempt_info}"
                                )
                                
                                amq_json_str = await self.amq_converter.convert_to_amq(final_text)
                                
                                # Validate that conversion produced valid JSON
                                if not amq_json_str or not amq_json_str.strip():
                                    raise RuntimeError("AMQ conversion returned empty content")
                                
                                # Validate that it's actually parseable JSON
                                try:
                                    json.loads(amq_json_str)
                                except json.JSONDecodeError as json_err:
                                    raise RuntimeError(
                                        f"AMQ conversion produced invalid JSON: {json_err}"
                                    ) from json_err
                                
                                final_text = amq_json_str
                                conversion_time = time.time() - conversion_start_time
                                logger.info(
                                    f"AMQ conversion successful after {conversion_time:.1f}s "
                                    f"{attempt_info}"
                                )
                                break  # Success, exit retry loop
                                
                            except Exception as e:
                                retry_count += 1
                                error_msg = (
                                    f"AMQ conversion failed {attempt_info}: "
                                    f"{type(e).__name__}: {str(e)}"
                                )
                                
                                if retry_count <= max_retries:
                                    # Calculate exponential backoff: 2s, 4s, 8s
                                    backoff_time = 2 ** retry_count  # 2, 4, 8 seconds
                                    logger.warning(f"{error_msg} - retrying in {backoff_time}s...")
                                    await asyncio.sleep(backoff_time)
                                    continue
                                else:
                                    # All retries exhausted - hard error since JSON was requested
                                    total_time = time.time() - conversion_start_time
                                    logger.error(
                                        f"AMQ conversion failed after {max_retries + 1} attempts "
                                        f"in {total_time:.1f}s. Final error: {str(e)}"
                                    )
                                    raise RuntimeError(
                                        f"Failed to convert response to AMQ JSON format after "
                                        f"{max_retries + 1} attempts. Since JSON format was explicitly "
                                        f"requested, cannot fall back to markdown. Error: {str(e)}"
                                    ) from e
                    
                    # Save assistant response to database
                    await self.conv.save_assistant_response(final_text)
                    
                    if tool_mode:
                        self.emit_event("tool_final", final_text)
                    else:
                        self.emit_event("response_final", final_text)
                        logger.info(f"Final response: {final_text}\n")
                    return final_text
                
                raise RuntimeError("No final response found in response.")

    async def _call_with_stream_retry(self, max_retries: int = 3, base_delay: float = 1.0):
        """
        Call the conversation stream with retry logic for streaming-specific errors.
        """
        last_error = None
        
        for attempt in range(max_retries + 1):
            try:
                return await self.conv.call_async(
                    tools=self.tool_specs,
                    stream=True,
                )
            except Exception as e:
                last_error = e
                
                # Check if this error is retryable
                if not is_retryable_error(e):
                    logger.error(
                        f"Non-retryable streaming error on attempt {attempt + 1}: "
                        f"{type(e).__name__}: {str(e)}"
                    )
                    raise
                
                # If this is our last attempt, raise the error
                if attempt == max_retries:
                    logger.error(
                        f"Max streaming retries ({max_retries}) exceeded. Final error: "
                        f"{type(e).__name__}: {str(e)}"
                    )
                    raise
                
                # Calculate backoff delay
                delay = min(base_delay * (2 ** attempt), 30.0)  # Cap at 30 seconds
                
                logger.warning(
                    f"Retryable streaming error on attempt {attempt + 1}/{max_retries + 1}: "
                    f"{type(e).__name__}: {str(e)}"
                )
                logger.info(f"Waiting {delay:.1f}s before streaming retry {attempt + 2}")
                
                await asyncio.sleep(delay)
        
        # This should never be reached, but just in case
        raise last_error 