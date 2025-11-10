"""
Security utilities for sanitizing sensitive data in logs and outputs.

Prevents API keys, tokens, and other sensitive information from appearing in logs.
"""

import re
from typing import Dict, Any, Union, List

# Sensitive field patterns to sanitize
SENSITIVE_FIELDS = {
    'api_key', 'apikey', 'key', 'token', 'password', 'secret', 
    'authorization', 'auth', 'credential', 'credentials',
    'access_token', 'refresh_token', 'bearer', 'jwt'
}

# Patterns that might contain sensitive data
SENSITIVE_PATTERNS = [
    r'sk-[a-zA-Z0-9]{48}',  # OpenAI keys
    r'Bearer\s+[a-zA-Z0-9\-._~+/]+=*',  # Bearer tokens
    r'[a-zA-Z0-9]{32,}',  # Long alphanumeric strings (potential keys)
]


def sanitize_value(value: str, mask: str = '***REDACTED***') -> str:
    """
    Sanitize a single value that might be sensitive.
    
    Args:
        value: Value to sanitize
        mask: Replacement string for sensitive data
        
    Returns:
        Sanitized value
    """
    if not isinstance(value, str):
        return value
    
    # Check if it matches known sensitive patterns
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, value):
            return mask
    
    # If it's a very long string, partially mask it
    if len(value) > 64:
        return f"{value[:8]}...{mask}...{value[-4:]}"
    
    return value


def sanitize_dict(data: Dict[str, Any], mask: str = '***REDACTED***') -> Dict[str, Any]:
    """
    Recursively sanitize dictionary by masking sensitive fields.
    
    Args:
        data: Dictionary to sanitize
        mask: Replacement string for sensitive data
        
    Returns:
        Sanitized dictionary (new copy)
    """
    if not isinstance(data, dict):
        return data
    
    sanitized = {}
    
    for key, value in data.items():
        # Check if key is sensitive
        key_lower = key.lower().replace('_', '').replace('-', '')
        is_sensitive = any(sens in key_lower for sens in SENSITIVE_FIELDS)
        
        if is_sensitive:
            # Mask the value
            sanitized[key] = mask
        elif isinstance(value, dict):
            # Recursively sanitize nested dicts
            sanitized[key] = sanitize_dict(value, mask)
        elif isinstance(value, list):
            # Sanitize lists
            sanitized[key] = [
                sanitize_dict(item, mask) if isinstance(item, dict) else sanitize_value(str(item), mask)
                for item in value
            ]
        elif isinstance(value, str):
            # Check if value itself looks sensitive
            sanitized[key] = sanitize_value(value, mask)
        else:
            sanitized[key] = value
    
    return sanitized


def sanitize_string(text: str, mask: str = '***REDACTED***') -> str:
    """
    Sanitize string by replacing patterns that look like API keys or tokens.
    
    Args:
        text: Text to sanitize
        mask: Replacement string
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return text
    
    sanitized = text
    
    # Replace known sensitive patterns
    for pattern in SENSITIVE_PATTERNS:
        sanitized = re.sub(pattern, mask, sanitized)
    
    return sanitized


def sanitize_url(url: str, mask: str = '***REDACTED***') -> str:
    """
    Sanitize URL by masking query parameters that might contain sensitive data.
    
    Args:
        url: URL to sanitize
        mask: Replacement string
        
    Returns:
        Sanitized URL
    """
    if not isinstance(url, str) or '?' not in url:
        return url
    
    base, query = url.split('?', 1)
    params = query.split('&')
    
    sanitized_params = []
    for param in params:
        if '=' in param:
            key, value = param.split('=', 1)
            key_lower = key.lower()
            if any(sens in key_lower for sens in SENSITIVE_FIELDS):
                sanitized_params.append(f"{key}={mask}")
            else:
                sanitized_params.append(param)
        else:
            sanitized_params.append(param)
    
    return f"{base}?{'&'.join(sanitized_params)}"


def sanitize_for_logging(data: Any, mask: str = '***') -> Any:
    """
    Main sanitization function for logging.
    
    Handles dicts, strings, lists, and other types.
    
    Args:
        data: Data to sanitize
        mask: Replacement string
        
    Returns:
        Sanitized data
    """
    if isinstance(data, dict):
        return sanitize_dict(data, mask)
    elif isinstance(data, str):
        return sanitize_string(data, mask)
    elif isinstance(data, list):
        return [sanitize_for_logging(item, mask) for item in data]
    else:
        return data


def create_safe_error_message(error: Exception, include_traceback: bool = False) -> str:
    """
    Create error message safe for logging (no sensitive data).
    
    Args:
        error: Exception to format
        include_traceback: Whether to include traceback
        
    Returns:
        Sanitized error message
    """
    error_msg = str(error)
    error_type = type(error).__name__
    
    # Sanitize the error message
    sanitized_msg = sanitize_string(error_msg)
    
    # Build safe message
    safe_msg = f"{error_type}: {sanitized_msg}"
    
    if include_traceback:
        import traceback
        tb = traceback.format_exc()
        safe_msg += f"\n{sanitize_string(tb)}"
    
    return safe_msg