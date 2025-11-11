"""
API Key Manager for OpenAI API key rotation and rate limit handling.

This module provides centralized management of multiple OpenAI API keys,
automatically rotating between them when rate limits are encountered.
"""

import os
import logging
import random
from typing import List, Optional, Dict, Any
from threading import Lock
from openai import OpenAI, AsyncOpenAI
from datetime import datetime

logger = logging.getLogger(__name__)


class APIKeyManager:
    """
    Manages multiple OpenAI API keys with simple random selection.
    
    Supports both environment variable and direct key configuration.
    Tracks basic usage statistics for monitoring.
    Uses random selection to distribute load across all keys.
    """
    
    def __init__(self, api_keys: Optional[List[str]] = None):
        """
        Initialize the API key manager.
        
        Parameters
        ----------
        api_keys : Optional[List[str]]
            List of API keys to use. If None, loads from environment variables.
        """
        self._lock = Lock()
        
        # Load API keys
        if api_keys:
            self.api_keys = api_keys
        else:
            self.api_keys = self._load_keys_from_env()
        
        if not self.api_keys:
            raise ValueError("No API keys provided. Check environment variables or provide keys directly.")
        
        # Track basic usage stats
        self.key_states = {}
        for key in self.api_keys:
            self.key_states[key] = {
                'usage_count': 0,
                'last_used': None
            }
        
        logger.info(f"Initialized API Key Manager with {len(self.api_keys)} keys")
    
    def _load_keys_from_env(self) -> List[str]:
        """
        Load API keys from environment variables.
        
        Supports both single key (OPENAI_API_KEY) and multiple keys 
        (OPENAI_API_KEY_1, OPENAI_API_KEY_2, etc.)
        """
        keys = []
        
        # Try single key first
        single_key = os.getenv('OPENAI_API_KEY')
        if single_key:
            keys.append(single_key)
        
        # Try multiple keys
        i = 1
        while True:
            key = os.getenv(f'OPENAI_API_KEY_{i}')
            if key:
                keys.append(key)
                i += 1
            else:
                break
        
        # Remove duplicates while preserving order
        seen = set()
        unique_keys = []
        for key in keys:
            if key not in seen:
                seen.add(key)
                unique_keys.append(key)
        
        logger.info(f"Loaded {len(unique_keys)} API keys from environment")
        return unique_keys
    

    
    def get_available_key(self) -> str:
        """
        Get a randomly selected API key.
        
        Returns
        -------
        str
            A randomly selected API key
        """
        with self._lock:
            # Randomly select from all keys
            selected_key = random.choice(self.api_keys)
            
            # Update usage stats
            state = self.key_states[selected_key]
            state['usage_count'] += 1
            state['last_used'] = datetime.now()
            
            # Log selection for debugging
            key_index = self.api_keys.index(selected_key)
            logger.debug(f"Randomly selected API key index {key_index} (usage: {state['usage_count']})")
            return selected_key
    

    
    def get_client(self, **kwargs) -> OpenAI:
        """
        Get an OpenAI client with an available API key.
        
        Parameters
        ----------
        **kwargs
            Additional arguments to pass to OpenAI client
            
        Returns
        -------
        OpenAI
            Configured OpenAI client
        """
        api_key = self.get_available_key()
        return OpenAI(api_key=api_key, **kwargs)
    
    def get_async_client(self, **kwargs) -> AsyncOpenAI:
        """
        Get an async OpenAI client with an available API key.
        
        Parameters
        ----------
        **kwargs
            Additional arguments to pass to AsyncOpenAI client
            
        Returns
        -------
        AsyncOpenAI
            Configured async OpenAI client
        """
        api_key = self.get_available_key()
        return AsyncOpenAI(api_key=api_key, **kwargs)
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """
        Get usage statistics for all API keys.
        
        Returns
        -------
        Dict[str, Any]
            Usage statistics including total requests per key.
        """
        with self._lock:
            stats = {
                'total_keys': len(self.api_keys),
                'total_usage': sum(state['usage_count'] for state in self.key_states.values()),
                'keys': []
            }
            
            for i, key in enumerate(self.api_keys):
                state = self.key_states[key]
                key_stats = {
                    'index': i,
                    'key_suffix': key[-8:] if len(key) > 8 else key,  # Show last 8 chars for identification
                    'usage_count': state['usage_count'],
                    'last_used': state['last_used'].isoformat() if state['last_used'] else None
                }
                
                stats['keys'].append(key_stats)
            
            return stats


# Global instance
_api_key_manager: Optional[APIKeyManager] = None


def get_api_key_manager() -> APIKeyManager:
    """
    Get the global API key manager instance.
    
    Returns
    -------
    APIKeyManager
        The global API key manager
    """
    global _api_key_manager
    if _api_key_manager is None:
        _api_key_manager = APIKeyManager()
    return _api_key_manager


def get_openai_client(**kwargs) -> OpenAI:
    """
    Get an OpenAI client with random API key selection.
    
    Each call randomly selects from all available API keys
    to distribute load evenly across all keys.
    
    Parameters
    ----------
    **kwargs
        Additional arguments to pass to OpenAI client
        
    Returns
    -------
    OpenAI
        Configured OpenAI client with randomly selected API key
    """
    return get_api_key_manager().get_client(**kwargs)


def get_async_openai_client(**kwargs) -> AsyncOpenAI:
    """
    Get an async OpenAI client with random API key selection.
    
    Each call randomly selects from all available API keys
    to distribute load evenly across all keys.
    
    Parameters
    ----------
    **kwargs
        Additional arguments to pass to AsyncOpenAI client
        
    Returns
    -------
    AsyncOpenAI
        Configured async OpenAI client with randomly selected API key
    """
    return get_api_key_manager().get_async_client(**kwargs) 