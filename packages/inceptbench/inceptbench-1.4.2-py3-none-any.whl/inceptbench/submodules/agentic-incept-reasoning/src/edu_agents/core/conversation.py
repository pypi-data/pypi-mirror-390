from __future__ import annotations

import asyncio
import logging
import time
from datetime import datetime, timezone
from typing import Any, Dict, List

from edu_agents.core.conversation_manager import ConversationManager

from .api_key_manager import get_async_openai_client

logger = logging.getLogger(__name__)

# Import httpx errors with fallback
try:
    from httpx import RemoteProtocolError
except ImportError:
    # Fallback if httpx isn't available or doesn't have this error
    class RemoteProtocolError(Exception):
        pass

logger = logging.getLogger(__name__)

def is_retryable_error(error: Exception) -> bool:
    """
    Determine if an error is retryable based on its type and message.
    
    Parameters
    ----------
    error : Exception
        The exception to check
        
    Returns
    -------
    bool
        True if the error should be retried
    """
    # Import here to avoid circular imports and handle version differences
    try:
        from openai import APITimeoutError, RateLimitError
    except ImportError:
        # Fallback if openai types aren't available
        RateLimitError = Exception
        APITimeoutError = Exception
    
    # APIConnectionError might not exist in all versions
    try:
        from openai import APIConnectionError
    except ImportError:
        APIConnectionError = Exception
    
    # Rate limiting errors are always retryable
    if isinstance(error, RateLimitError):
        return True
    
    # Timeout errors are retryable
    if isinstance(error, APITimeoutError):
        return True
    
    # Connection errors are retryable
    if isinstance(error, APIConnectionError):
        return True
    
    # Network connection errors are retryable
    network_errors = [RemoteProtocolError, ConnectionError]
    
    # Add more common network error types
    try:
        import requests
        network_errors.extend([
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.ReadTimeout,
            requests.exceptions.HTTPError
        ])
    except ImportError:
        pass
    
    if isinstance(error, tuple(network_errors)):
        return True
    
    # Check for specific API error patterns
    if hasattr(error, 'message'):
        error_str = str(error.message).lower()
    else:
        error_str = str(error).lower()
    
    retryable_patterns = [
        'error occurred while processing your request',
        'an error occurred while processing your request',
        'internal server error',
        'service unavailable', 
        'temporarily unavailable',
        'please try again',
        'request rate has increased suddenly',
        'overloading the model',
        'peer closed connection',
        'incomplete chunked read',
        'streaming finished without response.completed',
        'connection reset',
        'connection aborted',
        'read timeout',
        'timeout',
        'timed out',
        'server error',
        'bad gateway',
        'service temporarily overloaded'
    ]
    
    return any(pattern in error_str for pattern in retryable_patterns)

async def call_with_retry_async(call_func_async, max_retries: int = 3, base_delay: float = 1.0) -> Any:
    """
    Call an async function with exponential backoff retry logic.
    
    Parameters
    ----------
    call_func_async : coroutine
        The async function to call
    max_retries : int
        Maximum number of retry attempts
    base_delay : float
        Base delay for exponential backoff
        
    Returns
    -------
    Any
        The result of the function call
    """
    last_error = None
    
    for attempt in range(max_retries + 1):
        try:
            return await call_func_async()
        except Exception as e:
            last_error = e
            
            # Check if this error is retryable
            if not is_retryable_error(e):
                logger.error(
                    f"Non-retryable error on attempt {attempt + 1}: {type(e).__name__}: {str(e)}"
                )
                raise
            
            # If this is our last attempt, raise the error
            if attempt == max_retries:
                logger.error(
                    f"Max retries ({max_retries}) exceeded. Final error: {type(e).__name__}: "
                    f"{str(e)}"
                )
                raise
            
            # Calculate backoff delay
            delay = min(base_delay * (2 ** attempt), 30.0)  # Cap at 30 seconds
            
            logger.warning(
                f"Retryable error on attempt {attempt + 1}/{max_retries + 1}: {type(e).__name__}: "
                f"{str(e)}"
            )
            logger.info(f"Waiting {delay:.1f}s before retry {attempt + 2}")
            
            await asyncio.sleep(delay)
    
    # This should never be reached, but just in case
    raise last_error

class Conversation:
    """Thin wrapper around `openai.responses.create` that handles:
       • `messages` bookkeeping
       • Database-backed conversation history management
       • opt-in reasoning settings
    """

    def __init__(self, *, model: str, system_prompt: str, effort: str = "medium",
    files: list[dict] = None, conversation_id: str | None = None, user_id: str = None,
    is_incept: bool = False):
        self.model = model
        self.system_prompt = system_prompt
        self.system_prompt_label = "developer" if model \
            in ["o3", "o4-mini", "o4-mini-high", "incept"] else "system"
        self.effort = effort
        self.files = files or []
        self.user_id = user_id
        self.is_incept = is_incept

        # Configure async OpenAI client with timeout settings and key rotation
        self.client = get_async_openai_client(timeout=600.0)  # 10 minutes timeout for LLM calls
        self.were_files_added = False
        
        # Use ConversationManager for database-backed conversation history
        self.conversation_manager = ConversationManager()
        self.conversation_id = conversation_id  # Use provided conversation_id or None for new
        self.items = []  # Built dynamically from database
        self.reasoning_cfg = {"effort": effort, "summary": "auto"}
        
        # Cache base timestamp to avoid database hits on every message save
        self._base_timestamp = None
        self._base_timestamp_initialized = False

    # ------------------------------------------------------------------ #
    # message helpers                                                    #
    # ------------------------------------------------------------------ #
    def user(self, content: str) -> None:
        """Add a user message to the conversation."""
        # Handle files in the content if they exist and haven't been added yet
        if self.files and not self.were_files_added:
            # Avoid mutating the shared files list – create a fresh list per message
            # Create array of content items
            _content = list(self.files) + [
                {
                    "type": "input_text",
                    "text": content,
                }
            ]
            self.were_files_added = True
            
            # Store as array, not string
            self._pending_user_message = _content
        else:
            # If no files, just store the text content directly
            self._pending_user_message = content

    def tool_result(self, tool_call_id: str, content: str) -> None:
        """Save tool result to conversation history for next input."""
        # Save to database for persistence (database is now the source of truth)
        # Tool results are retrieved from database on next OpenAI API call
        if self.conversation_id:
            # We need to run this in an async context - store for later processing
            if not hasattr(self, '_tool_results_to_save'):
                self._tool_results_to_save = []
            self._tool_results_to_save.append({
                "call_id": tool_call_id,
                "output": content,
            })

    def reset_conversation(self) -> None:
        """Reset the conversation state."""
        self.client = get_async_openai_client(timeout=600.0)  # 10 minutes timeout for LLM calls
        # Reset conversation_id to None to create new conversation
        self.conversation_id = None
        self.items = []
        # Reset files flag so they can be added again in the new conversation
        self.were_files_added = False

    # ------------------------------------------------------------------ #
    # keep the linked function_call item                                 #
    # ------------------------------------------------------------------ #
    def add_function_call(self, *, name: str, arguments: str | dict, call_id: str):
        """Save function call to conversation history for next input."""
        # Save to database for persistence (database is now the source of truth)
        # Function calls are retrieved from database on next OpenAI API call
        if self.conversation_id:
            # We need to run this in an async context - store for later processing
            if not hasattr(self, '_function_calls_to_save'):
                self._function_calls_to_save = []
            self._function_calls_to_save.append({
                "name": name,
                "arguments": arguments,
                "call_id": call_id,
            })

    async def _ensure_conversation_exists(self) -> bool:
        """Ensure conversation exists in database."""
        if self.conversation_id is None:
            # Create new conversation and set base timestamp
            current_time = datetime.now(timezone.utc).timestamp()
            self.conversation_id = await self.conversation_manager.create_new_conversation(
                user_id=self.user_id,
                system_prompt=self.system_prompt
            )
            if self.conversation_id:
                # Cache the base timestamp for this new conversation
                self.set_conversation_base_timestamp(current_time)
            return self.conversation_id is not None
        else:
            # Check if conversation exists
            exists = await self.conversation_manager.conversation_exists_check(self.conversation_id)
            if not exists:
                # Conversation doesn't exist, create it
                # Note: This will create a new conversation_id, not use the provided one
                current_time = datetime.now(timezone.utc).timestamp()
                self.conversation_id = await self.conversation_manager.create_new_conversation(
                    user_id=self.user_id,
                    system_prompt=self.system_prompt
                )
                if self.conversation_id:
                    # Cache the base timestamp for this new conversation
                    self.set_conversation_base_timestamp(current_time)
                return self.conversation_id is not None
            else:
                # Existing conversation - initialize base timestamp from database if needed
                if not self._base_timestamp_initialized:
                    await self._initialize_base_timestamp()
            return True

    async def _build_input(self) -> List[Dict[str, Any]]:
        """Build input using conversation history from database."""
        if not await self._ensure_conversation_exists():
            # If conversation creation failed, fall back to basic input
            return [{
                "type": "message",
                "role": self.system_prompt_label,
                "content": self.system_prompt
            }]
        
        # Get the pending user message
        user_message = getattr(self, '_pending_user_message', None)
        
        # Clear the pending user message after getting it (to prevent duplicate saves)
        if user_message is not None:
            delattr(self, '_pending_user_message')
        
        # Clean up any remaining deferred persistence arrays to reduce memory pressure
        # These should be empty now that we use atomic persistence, but clean up for safety
        if hasattr(self, '_function_calls_to_save'):
            remaining_calls = getattr(self, '_function_calls_to_save', [])
            if remaining_calls:
                logger.warning(
                    f"Found {len(remaining_calls)} deferred function calls during atomic "
                    "persistence mode"
                )
                # Still process them as fallback
                for call_data in remaining_calls:
                    try:
                        function_name = call_data.get("name", "unknown_function_name")
                        call_id = call_data.get("call_id",
                                                f"unknown_call_{int(time.time() * 1000)}")
                        
                        await self.conversation_manager.save_function_call(
                            self.conversation_id,
                            function_name,
                            call_data.get("arguments", "{}"),
                            call_id
                        )
                    except Exception as e:
                        logger.error(f"Error saving deferred function call: {e}")
            delattr(self, '_function_calls_to_save')
        
        # Clean up any remaining deferred tool results
        if hasattr(self, '_tool_results_to_save'):
            remaining_results = getattr(self, '_tool_results_to_save', [])
            if remaining_results:
                logger.warning(
                    f"Found {len(remaining_results)} deferred tool results during atomic "
                    "persistence mode"
                )
                # Still process them as fallback
                for result_data in remaining_results:
                    try:
                        await self.conversation_manager.save_function_call_output(
                            self.conversation_id,
                            result_data["call_id"],
                            result_data["output"]
                        )
                    except Exception as e:
                        logger.error(f"Error saving deferred tool result: {e}")
            delattr(self, '_tool_results_to_save')
        
        # Build input from conversation history (includes all saved function calls/results)
        input_items = await self.conversation_manager.build_input_for_responses_api(
            self.conversation_id,
            new_user_message=user_message
        )
        
        return input_items

    # ------------------------------------------------------------------ #
    # Core call                                                          #
    # ------------------------------------------------------------------ #
    async def call_async(
        self,
        *,
        tools: list[dict] = None,
        stream: bool = False,
    ):
        """
        Make an async API call with conversation handling and retry logic.
        
        This is the primary method for making API calls. The sync call() method
        has been removed - all calls should use this async version.
        """
        # Build input using conversation history from database
        input_items = await self._build_input()
        
        async def _make_call():
            return await self.client.responses.create(
                model=self.model,
                input=input_items,
                tools=tools or [],
                tool_choice="auto" if tools else None,
                reasoning=self.reasoning_cfg,
                stream=stream,
                parallel_tool_calls=True,
            )
        
        return await call_with_retry_async(_make_call, max_retries=3)

    async def save_assistant_response(self, response_content: str) -> bool:
        """Save assistant response to conversation history."""
        if self.conversation_id:
            return await self.conversation_manager.save_assistant_response(
                self.conversation_id, response_content
            )
        return True

    async def save_function_call_immediate(self, *, name: str, arguments: str | dict,
    call_id: str) -> bool:
        """
        Save function call to database immediately instead of queueing.
        
        This method provides immediate persistence to reduce race conditions
        under high load conditions.
        """
        if self.conversation_id:
            await self._ensure_conversation_exists()
            return await self.conversation_manager.save_function_call(
                self.conversation_id, name, arguments, call_id
            )
        return True

    async def save_tool_result_immediate(self, tool_call_id: str, content: str) -> bool:
        """
        Save tool result to database immediately instead of queueing.
        
        This method provides immediate persistence to reduce race conditions
        under high load conditions.
        """
        if self.conversation_id:
            await self._ensure_conversation_exists()
            return await self.conversation_manager.save_function_call_output(
                self.conversation_id, tool_call_id, content
            )
        return True

    async def save_function_call_with_output_atomic(
        self, *, name: str, arguments: str | dict, call_id: str, output: str
    ) -> bool:
        """
        Atomically save both function call and output to prevent mismatches.
        
        This is the preferred method for saving function calls under high load
        as it eliminates race conditions between saving the call and its output.
        Uses cached base timestamp to avoid database hits on every save.
        """
        if self.conversation_id:
            await self._ensure_conversation_exists()
            # Get cached base timestamp to avoid database hit
            base_timestamp = await self.get_conversation_base_timestamp()
            return await self.conversation_manager.save_function_call_with_output_cached(
                self.conversation_id, name, arguments, call_id, output, base_timestamp
            )
        return True

    async def get_conversation_base_timestamp(self) -> float:
        """
        Get the cached base timestamp for this conversation.
        Initializes it from database or creates new one if needed.
        """
        if not self._base_timestamp_initialized:
            await self._initialize_base_timestamp()
        return self._base_timestamp

    async def _initialize_base_timestamp(self) -> None:
        """Initialize the base timestamp cache from database or create new one."""
        if self.conversation_id is None:
            # No conversation yet, will be initialized when conversation is created
            self._base_timestamp = None
            self._base_timestamp_initialized = True
            return

        # Import here to avoid circular imports
        from utils.supabase_utils import get_or_create_conversation_base_timestamp

        # Get base timestamp from database (only once per conversation instance)
        self._base_timestamp = await get_or_create_conversation_base_timestamp(self.conversation_id)
        self._base_timestamp_initialized = True

    def set_conversation_base_timestamp(self, timestamp: float) -> None:
        """Set the cached base timestamp (used when creating new conversations)."""
        self._base_timestamp = timestamp
        self._base_timestamp_initialized = True

    def calculate_message_order(self, current_timestamp: float = None) -> int:
        """
        Calculate message order using cached base timestamp.
        Avoids database hits for every message save.
        """
        if not self._base_timestamp_initialized or self._base_timestamp is None:
            # Fallback to simple ordering if base timestamp not available
            logger.warning("Base timestamp not initialized, using fallback ordering")
            return 1

        if current_timestamp is None:
            from datetime import datetime, timezone
            current_timestamp = datetime.now(timezone.utc).timestamp()

        offset_seconds = current_timestamp - self._base_timestamp
        if offset_seconds < 0:
            # Handle clock skew
            return 1
        
        # Use round() to handle floating point precision
        return round(offset_seconds * 10) + 1

    def get_conversation_id(self) -> str:
        """Get the current conversation ID."""
        return self.conversation_id