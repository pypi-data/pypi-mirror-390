from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

from utils.supabase_utils import (
    conversation_exists,
    create_conversation,
    delete_conversation,
    get_conversation_messages,
    get_recent_conversation_messages,
    save_conversation_message,
    save_conversation_message_with_cached_timestamp,
    save_function_call_with_output_atomic,
    save_function_call_with_output_atomic_cached,
    update_conversation_metadata,
)

logger = logging.getLogger(__name__)

class ConversationManager:
    """
    High-level interface for managing conversations and their history.
    
    This class orchestrates database operations for conversation management,
    providing convenient methods for creating, updating, and retrieving
    conversation data while abstracting away the database implementation details.
    """
    
    def __init__(self):
        self.max_context_messages = 50  # Configurable limit for context
        
    async def create_new_conversation(
        self, 
        user_id: str = None, 
        system_prompt: str = None,
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """
        Create a new conversation with optional system prompt.
        
        Parameters
        ----------
        user_id : str, optional
            The user ID to associate with this conversation
        system_prompt : str, optional
            Initial system prompt for the conversation
        metadata : Dict[str, Any], optional
            Additional metadata to store
            
        Returns
        -------
        Optional[str]
            The conversation_id if successful, None otherwise
        """
        try:
            # Prepare metadata
            conversation_metadata = metadata or {}
            if system_prompt:
                conversation_metadata["system_prompt"] = system_prompt
                
            # Create conversation record
            conversation_id = await create_conversation(user_id, conversation_metadata)
            
            if conversation_id and system_prompt:
                # Save system prompt as first message
                await save_conversation_message(conversation_id, "system", system_prompt, 1)
                
            return conversation_id
            
        except Exception as e:
            logger.error(f"Error creating new conversation: {str(e)}")
            return None
    
    async def add_user_message(self, conversation_id: str, content: str) -> bool:
        """
        Add a user message to the conversation.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        content : str
            The user message content
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        return await save_conversation_message(conversation_id, "user", content)
    
    async def add_assistant_message(self, conversation_id: str, content: str) -> bool:
        """
        Add an assistant message to the conversation.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        content : str
            The assistant message content
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        return await save_conversation_message(conversation_id, "assistant", content)
    
    async def get_conversation_history(
        self, 
        conversation_id: str,
        max_messages: int = None
    ) -> List[Dict[str, str]]:
        """
        Get conversation history formatted for OpenAI API.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        max_messages : int, optional
            Maximum number of messages to retrieve (uses default if not specified)
            
        Returns
        -------
        List[Dict[str, str]]
            List of messages formatted as [{"role": "user", "content": "..."}, ...]
        """
        try:
            # Use provided limit or default
            limit = max_messages or self.max_context_messages
            
            # Get recent messages from database
            db_messages = await get_recent_conversation_messages(conversation_id, limit)
            
            # Convert to OpenAI format
            formatted_messages = []
            for msg in db_messages:
                formatted_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            return formatted_messages
            
        except Exception as e:
            logger.error(f"Error getting conversation history for {conversation_id}: {str(e)}")
            return []
    
    async def build_input_for_responses_api(
        self, 
        conversation_id: str, 
        new_user_message: str = None,
        max_messages: int = None
    ) -> List[Dict[str, Any]]:
        """
        Build input for OpenAI Responses API from conversation history.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        new_user_message : str, optional
            New user message to add (will be added to history automatically)
        max_messages : int, optional
            Maximum number of messages to include in context
            
        Returns
        -------
        List[Dict[str, Any]]
            Input formatted for OpenAI Responses API
        """
        try:
            # Add new user message if provided
            if new_user_message:
                await self.add_user_message(conversation_id, new_user_message)
            
            # Get conversation history
            history = await self.get_conversation_history(conversation_id, max_messages)
            
            # Convert to Responses API format
            input_items = []
            for msg in history:
                if msg["role"] in ['system', 'user', 'assistant']:
                    # Regular message
                    # If content is a JSON string of an array, parse it back to an array
                    content = msg["content"]
                    if isinstance(content, str) and content.startswith('[') \
                        and content.endswith(']'):
                        try:
                            content = json.loads(content)
                        except (json.JSONDecodeError, TypeError):
                            pass
                            
                    input_items.append({
                        "type": "message",
                        "role": msg["role"],
                        "content": content
                    })
                elif msg["role"] == 'function_call':
                    # Function call - content should be JSON with name, arguments, call_id
                    try:
                        call_data = json.loads(msg["content"])
                        # Validate required fields - use fallbacks for missing data
                        function_name = call_data.get("name", "unknown_function_name")
                        call_id = call_data.get("call_id", f"unknown_call_{len(input_items)}")
                        
                        if "name" not in call_data:
                            logger.warning(
                                f"Function call missing name in conversation {conversation_id}, "
                                f"using fallback 'unknown_function_name'. Data: {call_data}"
                            )
                        if "call_id" not in call_data:
                            logger.warning(
                                f"Function call missing call_id in conversation {conversation_id}, "
                                f"using fallback '{call_id}'. Data: {call_data}"
                            )
                        
                        input_items.append({
                            "type": "function_call",
                            "name": function_name,
                            "arguments": call_data.get("arguments", "{}"),
                            "call_id": call_id
                        })
                    except (json.JSONDecodeError, KeyError) as e:
                        logger.warning(
                            f"Malformed function call JSON in conversation {conversation_id}: {e}. "
                            f"Content: {msg.get('content', 'N/A')}. Using fallback function call."
                        )
                        # Create a fallback function call to maintain conversation flow
                        fallback_call_id = f"malformed_call_{len(input_items)}"
                        input_items.append({
                            "type": "function_call",
                            "name": "unknown_function_name",
                            "arguments": "{}",
                            "call_id": fallback_call_id
                        })
                elif msg["role"] == 'function_call_output':
                    # Function call output - content should be JSON with call_id, output
                    output_data = json.loads(msg["content"])
                    input_items.append({
                        "type": "function_call_output",
                        "call_id": output_data["call_id"],
                        "output": output_data["output"]
                    })
            
            return input_items
            
        except Exception as e:
            logger.error(f"Error building input for conversation {conversation_id}: {str(e)}")
            return []
    
    async def save_assistant_response(
        self, 
        conversation_id: str, 
        response_content: str
    ) -> bool:
        """
        Save the assistant's response to the conversation.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        response_content : str
            The assistant's response content
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        return await self.add_assistant_message(conversation_id, response_content)

    async def save_function_call(self, conversation_id: str, name: str, arguments: str | dict,
    call_id: str) -> bool:
        """
        Save a function call to the conversation.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        name : str
            The function name
        arguments : str | dict
            The function arguments
        call_id : str
            The call ID
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            # Prepare function call data
            call_data = {
                "name": name,
                "arguments": arguments,
                "call_id": call_id
            }
            
            # Save to database using the utility function
            return await save_conversation_message(conversation_id, "function_call",
                                                   json.dumps(call_data))
            
        except Exception as e:
            logger.error(f"Error saving function call to conversation {conversation_id}: {str(e)}")
            return False

    async def save_function_call_output(self, conversation_id: str, call_id: str,
    output: str) -> bool:
        """
        Save a function call output to the conversation.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        call_id : str
            The call ID
        output : str
            The function output
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            # Prepare function output data
            output_data = {
                "call_id": call_id,
                "output": output
            }
            
            # Save to database using the utility function
            return await save_conversation_message(conversation_id, "function_call_output",
                                                   json.dumps(output_data))
            
        except Exception as e:
            logger.error(
                f"Error saving function call output to conversation {conversation_id}: {str(e)}"
            )
            return False

    async def save_function_call_with_output_immediate(
        self, 
        conversation_id: str, 
        name: str, 
        arguments: str | dict, 
        call_id: str, 
        output: str
    ) -> bool:
        """
        Atomically save a function call and its output to prevent mismatches.
        
        This method uses the atomic database operation to ensure that both
        the function call and its output are saved together, eliminating
        race conditions that can occur under high load.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        name : str
            The function name
        arguments : str | dict
            The function arguments
        call_id : str
            The call ID
        output : str
            The function output
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            return await save_function_call_with_output_atomic(
                conversation_id, name, arguments, call_id, output
            )
        except Exception as e:
            logger.error(f"Error in atomic save for function call {call_id}: {str(e)}")
            return False

    async def save_function_call_with_output_cached(
        self, 
        conversation_id: str, 
        name: str, 
        arguments: str | dict, 
        call_id: str, 
        output: str,
        base_timestamp: float
    ) -> bool:
        """
        Atomically save a function call and its output using cached base timestamp.
        
        This avoids database hits for getting the base timestamp on every save,
        providing better performance under high load.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        name : str
            The function name
        arguments : str | dict
            The function arguments
        call_id : str
            The call ID
        output : str
            The function output
        base_timestamp : float
            The cached base timestamp for this conversation
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            return await save_function_call_with_output_atomic_cached(
                conversation_id, name, arguments, call_id, output, base_timestamp
            )
        except Exception as e:
            logger.error(f"Error in cached atomic save for function call {call_id}: {str(e)}")
            return False

    async def save_message_with_cached_timestamp(
        self,
        conversation_id: str,
        role: str,
        content: str,
        base_timestamp: float
    ) -> bool:
        """
        Save a message using cached base timestamp for ordering.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        role : str
            The message role
        content : str
            The message content
        base_timestamp : float
            The cached base timestamp for this conversation
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        try:
            return await save_conversation_message_with_cached_timestamp(
                conversation_id, role, content, base_timestamp
            )
        except Exception as e:
            logger.error(f"Error saving message with cached timestamp: {str(e)}")
            return False
    
    async def conversation_exists_check(self, conversation_id: str) -> bool:
        """
        Check if a conversation exists.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID to check
            
        Returns
        -------
        bool
            True if conversation exists, False otherwise
        """
        return await conversation_exists(conversation_id)
    
    async def update_metadata(
        self, 
        conversation_id: str, 
        metadata: Dict[str, Any]
    ) -> bool:
        """
        Update conversation metadata.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
        metadata : Dict[str, Any]
            Metadata to update
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        return await update_conversation_metadata(conversation_id, metadata)
    
    async def delete_conversation_and_messages(self, conversation_id: str) -> bool:
        """
        Delete a conversation and all its messages.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID to delete
            
        Returns
        -------
        bool
            True if successful, False otherwise
        """
        return await delete_conversation(conversation_id)
    
    async def get_conversation_stats(self, conversation_id: str) -> Dict[str, Any]:
        """
        Get statistics about a conversation.
        
        Parameters
        ----------
        conversation_id : str
            The conversation ID
            
        Returns
        -------
        Dict[str, Any]
            Statistics including message count, roles breakdown, etc.
        """
        try:
            # Get all messages for stats
            all_messages = await get_conversation_messages(conversation_id)
            
            stats = {
                "total_messages": len(all_messages),
                "user_messages": len([m for m in all_messages if m["role"] == "user"]),
                "assistant_messages": len([m for m in all_messages if m["role"] == "assistant"]),
                "system_messages": len([m for m in all_messages if m["role"] == "system"]),
                "first_message_at": all_messages[0]["created_at"] if all_messages else None,
                "last_message_at": all_messages[-1]["created_at"] if all_messages else None,
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats for conversation {conversation_id}: {str(e)}")
            return {}
    
    def set_max_context_messages(self, max_messages: int):
        """
        Set the maximum number of messages to include in context.
        
        Parameters
        ----------
        max_messages : int
            Maximum number of messages for context
        """
        self.max_context_messages = max_messages 