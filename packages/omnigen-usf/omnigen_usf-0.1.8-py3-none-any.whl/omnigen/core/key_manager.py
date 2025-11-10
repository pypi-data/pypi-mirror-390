"""
API Key rotation and management.

Features:
- Multiple API keys per provider
- Automatic rotation on rate limit
- Load balancing across keys
- Comprehensive error handling
"""

import threading
from typing import Dict, List, Optional
from collections import deque
from omnigen.utils.logger import setup_logger

logger = setup_logger()


class APIKeyManager:
    """
    Manages multiple API keys with rotation and fallback.
    
    Features:
    - Multiple keys per provider
    - Automatic rotation on rate limit
    - Round-robin load balancing
    - Thread-safe operations
    - Comprehensive error handling
    """
    
    def __init__(self):
        """Initialize API key manager."""
        try:
            self.keys: Dict[str, deque] = {}  # provider -> deque of keys
            self.key_stats: Dict[str, Dict] = {}  # key -> stats
            self.lock = threading.Lock()
            logger.info("APIKeyManager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize APIKeyManager: {e}", exc_info=True)
            self.keys = {}
            self.key_stats = {}
            self.lock = threading.Lock()
    
    def add_keys(self, provider_name: str, api_keys: List[str]):
        """
        Add multiple API keys for a provider.
        
        Args:
            provider_name: Provider name
            api_keys: List of API keys
        """
        try:
            with self.lock:
                if provider_name not in self.keys:
                    self.keys[provider_name] = deque()
                
                for key in api_keys:
                    try:
                        if key and key not in self.keys[provider_name]:
                            self.keys[provider_name].append(key)
                            self.key_stats[key] = {
                                'requests': 0,
                                'failures': 0,
                                'rate_limits': 0,
                                'last_used': None
                            }
                    except Exception as e:
                        logger.warning(f"Error adding key: {e}")
                
                logger.info(f"Added {len(api_keys)} keys for {provider_name}")
                
        except Exception as e:
            logger.error(f"Failed to add keys for {provider_name}: {e}", exc_info=True)
    
    def get_next_key(self, provider_name: str) -> Optional[str]:
        """
        Get next available API key (round-robin).
        
        Args:
            provider_name: Provider name
            
        Returns:
            API key or None if no keys available
        """
        try:
            with self.lock:
                if provider_name not in self.keys or not self.keys[provider_name]:
                    logger.warning(f"No keys available for {provider_name}")
                    return None
                
                # Rotate to next key
                try:
                    self.keys[provider_name].rotate(-1)
                    key = self.keys[provider_name][0]
                    
                    # Update stats
                    import time
                    if key in self.key_stats:
                        self.key_stats[key]['requests'] = self.key_stats[key].get('requests', 0) + 1
                        self.key_stats[key]['last_used'] = time.time()
                    
                    return key
                except Exception as e:
                    logger.error(f"Error rotating keys: {e}")
                    # Try to return first key
                    try:
                        return self.keys[provider_name][0] if self.keys[provider_name] else None
                    except:
                        return None
                        
        except Exception as e:
            logger.error(f"Error getting next key for {provider_name}: {e}", exc_info=True)
            return None
    
    def mark_rate_limited(self, provider_name: str, api_key: str):
        """
        Mark a key as rate limited (moves to end of rotation).
        
        Args:
            provider_name: Provider name
            api_key: API key that hit rate limit
        """
        try:
            with self.lock:
                if api_key in self.key_stats:
                    self.key_stats[api_key]['rate_limits'] = self.key_stats[api_key].get('rate_limits', 0) + 1
                
                # Move to end of queue
                if provider_name in self.keys and api_key in self.keys[provider_name]:
                    try:
                        # Find and move to end
                        keys_list = list(self.keys[provider_name])
                        if api_key in keys_list:
                            keys_list.remove(api_key)
                            keys_list.append(api_key)
                            self.keys[provider_name] = deque(keys_list)
                            logger.info(f"Moved rate-limited key to end for {provider_name}")
                    except Exception as e:
                        logger.warning(f"Error moving rate-limited key: {e}")
                        
        except Exception as e:
            logger.error(f"Error marking rate limited: {e}", exc_info=True)
    
    def mark_failed(self, api_key: str):
        """Mark a key as failed."""
        try:
            with self.lock:
                if api_key in self.key_stats:
                    self.key_stats[api_key]['failures'] = self.key_stats[api_key].get('failures', 0) + 1
        except Exception as e:
            logger.error(f"Error marking failed: {e}", exc_info=True)
    
    def get_stats(self, provider_name: Optional[str] = None) -> Dict:
        """Get key statistics."""
        try:
            with self.lock:
                if provider_name:
                    # Stats for specific provider
                    if provider_name in self.keys:
                        return {
                            'provider': provider_name,
                            'total_keys': len(self.keys[provider_name]),
                            'keys': [
                                {
                                    'key': key[:10] + '...',
                                    **self.key_stats.get(key, {})
                                }
                                for key in self.keys[provider_name]
                            ]
                        }
                    return {}
                else:
                    # All providers
                    return {
                        prov: {
                            'total_keys': len(keys),
                            'active': len([k for k in keys if self.key_stats.get(k, {}).get('failures', 0) == 0])
                        }
                        for prov, keys in self.keys.items()
                    }
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {}