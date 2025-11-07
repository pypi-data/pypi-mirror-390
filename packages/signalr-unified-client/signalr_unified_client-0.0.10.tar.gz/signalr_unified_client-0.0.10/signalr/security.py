"""
Security utilities for SignalR client library.
Provides secure logging, exception handling, and validation functions.
"""
import logging
import re
import warnings
from urllib.parse import urlparse
from typing import Optional, Any, Callable, Tuple

# Security event logger
_security_logger: Optional[logging.Logger] = None


def get_security_logger() -> logging.Logger:
    """Get or create the security logger."""
    global _security_logger
    if _security_logger is None:
        _security_logger = logging.getLogger('signalr.security')
        if not _security_logger.handlers:
            # Add a null handler if no handlers are configured
            # This prevents logging to root logger if no handler is set up
            _security_logger.addHandler(logging.NullHandler())
            _security_logger.setLevel(logging.WARNING)
    return _security_logger


def log_security_event(level: int, message: str, exc_info: Optional[Exception] = None, **kwargs):
    """
    Log a security-related event.
    
    Args:
        level: Logging level (logging.WARNING, logging.ERROR, etc.)
        message: Security event message
        exc_info: Optional exception to log
        **kwargs: Additional context to log
    """
    logger = get_security_logger()
    extra = {'security_event': True, **kwargs}
    logger.log(level, message, exc_info=exc_info, extra=extra)


def log_security_warning(message: str, exc_info: Optional[Exception] = None, **kwargs):
    """Log a security warning."""
    log_security_event(logging.WARNING, message, exc_info, **kwargs)


def log_security_error(message: str, exc_info: Optional[Exception] = None, **kwargs):
    """Log a security error."""
    log_security_event(logging.ERROR, message, exc_info, **kwargs)


def check_ssl_configuration(sslopt: Optional[dict]) -> bool:
    """
    Check SSL configuration for insecure settings and emit warnings.
    
    Returns:
        True if configuration is secure, False if insecure
    """
    if not sslopt:
        return True
    
    is_secure = True
    
    # Check for disabled hostname verification
    if sslopt.get('check_hostname') is False:
        warning_msg = (
            "Insecure SSL configuration detected: hostname verification is disabled. "
            "This makes the connection vulnerable to man-in-the-middle attacks. "
            "Only use this in development/testing environments."
        )
        warnings.warn(warning_msg, SecurityWarning, stacklevel=3)
        log_security_warning(
            "SSL hostname verification disabled",
            ssl_config={"check_hostname": False}
        )
        is_secure = False
    
    # Check for disabled certificate verification
    if sslopt.get('cert_reqs') == 0 or sslopt.get('cert_reqs') == 'CERT_NONE':
        warning_msg = (
            "Insecure SSL configuration detected: certificate verification is disabled. "
            "This makes the connection vulnerable to man-in-the-middle attacks. "
            "Only use this in development/testing environments."
        )
        warnings.warn(warning_msg, SecurityWarning, stacklevel=3)
        log_security_warning(
            "SSL certificate verification disabled",
            ssl_config={"cert_reqs": sslopt.get('cert_reqs')}
        )
        is_secure = False
    
    return is_secure


class SecurityWarning(Warning):
    """Warning for security-related issues."""
    pass


class SecurityError(Exception):
    """Exception for security-related errors."""
    pass


class ValidationError(SecurityError):
    """Exception for input validation errors."""
    pass


# Validation constants
ALLOWED_URL_SCHEMES = {'http', 'https', 'ws', 'wss'}
MAX_HUB_NAME_LENGTH = 128
MAX_METHOD_NAME_LENGTH = 128
MAX_QUERY_PARAM_KEY_LENGTH = 256
MAX_QUERY_PARAM_VALUE_LENGTH = 2048
MAX_QUERY_PARAMS_COUNT = 50
MAX_QUERY_STRING_LENGTH = 8192
HUB_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
METHOD_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_]+$')
QUERY_PARAM_KEY_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

# JSON parsing limits
MAX_JSON_MESSAGE_SIZE = 1024 * 1024  # 1MB default
MAX_JSON_DEPTH = 32  # Maximum nesting depth


def validate_url(url: str) -> Tuple[bool, Optional[str]]:
    """
    Validate URL format and scheme.
    
    Args:
        url: URL string to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not url or not isinstance(url, str):
        return False, "URL must be a non-empty string"
    
    if len(url) > 8192:  # Reasonable URL length limit
        return False, "URL exceeds maximum length"
    
    try:
        parsed = urlparse(url)
        
        # Check scheme
        if not parsed.scheme:
            return False, "URL must include a scheme"
        
        if parsed.scheme.lower() not in ALLOWED_URL_SCHEMES:
            return False, f"URL scheme must be one of {ALLOWED_URL_SCHEMES}, got: {parsed.scheme}"
        
        # Check hostname
        if not parsed.netloc:
            return False, "URL must include a hostname"
        
        # Basic validation passed
        return True, None
        
    except Exception as e:
        return False, f"Invalid URL format: {str(e)}"


def sanitize_hub_name(name: str) -> str:
    """
    Sanitize hub name to allow only safe characters.
    
    Args:
        name: Hub name to sanitize
        
    Returns:
        Sanitized hub name
        
    Raises:
        ValidationError: If hub name is invalid
    """
    if not name or not isinstance(name, str):
        raise ValidationError("Hub name must be a non-empty string")
    
    if len(name) > MAX_HUB_NAME_LENGTH:
        raise ValidationError(f"Hub name exceeds maximum length of {MAX_HUB_NAME_LENGTH}")
    
    if not HUB_NAME_PATTERN.match(name):
        raise ValidationError(
            f"Hub name contains invalid characters. "
            f"Only alphanumeric characters, underscores, and hyphens are allowed."
        )
    
    return name


def validate_method_name(name: str) -> str:
    """
    Validate method name.
    
    Args:
        name: Method name to validate
        
    Returns:
        Validated method name
        
    Raises:
        ValidationError: If method name is invalid
    """
    if not name or not isinstance(name, str):
        raise ValidationError("Method name must be a non-empty string")
    
    if len(name) > MAX_METHOD_NAME_LENGTH:
        raise ValidationError(f"Method name exceeds maximum length of {MAX_METHOD_NAME_LENGTH}")
    
    if not METHOD_NAME_PATTERN.match(name):
        raise ValidationError(
            f"Method name contains invalid characters. "
            f"Only alphanumeric characters and underscores are allowed."
        )
    
    return name


def validate_query_param_key(key: str) -> str:
    """
    Validate query parameter key.
    
    Args:
        key: Query parameter key to validate
        
    Returns:
        Validated key
        
    Raises:
        ValidationError: If key is invalid
    """
    if not key or not isinstance(key, str):
        raise ValidationError("Query parameter key must be a non-empty string")
    
    if len(key) > MAX_QUERY_PARAM_KEY_LENGTH:
        raise ValidationError(f"Query parameter key exceeds maximum length of {MAX_QUERY_PARAM_KEY_LENGTH}")
    
    if not QUERY_PARAM_KEY_PATTERN.match(key):
        raise ValidationError(
            f"Query parameter key contains invalid characters. "
            f"Only alphanumeric characters, underscores, and hyphens are allowed."
        )
    
    return key


def validate_query_params(params: dict) -> dict:
    """
    Validate query parameters dictionary.
    
    Args:
        params: Dictionary of query parameters
        
    Returns:
        Validated parameters dictionary
        
    Raises:
        ValidationError: If parameters are invalid
    """
    if not isinstance(params, dict):
        raise ValidationError("Query parameters must be a dictionary")
    
    if len(params) > MAX_QUERY_PARAMS_COUNT:
        raise ValidationError(f"Too many query parameters (max {MAX_QUERY_PARAMS_COUNT})")
    
    validated = {}
    total_length = 0
    
    for key, value in params.items():
        # Validate key
        validated_key = validate_query_param_key(str(key))
        
        # Validate value
        value_str = str(value)
        if len(value_str) > MAX_QUERY_PARAM_VALUE_LENGTH:
            raise ValidationError(
                f"Query parameter value for '{validated_key}' exceeds maximum length of {MAX_QUERY_PARAM_VALUE_LENGTH}"
            )
        
        # Check for CRLF injection in value
        if '\r' in value_str or '\n' in value_str:
            raise ValidationError(
                f"Query parameter value for '{validated_key}' contains invalid characters (CRLF)"
            )
        
        total_length += len(validated_key) + len(value_str) + 2  # +2 for '=' and '&'
        if total_length > MAX_QUERY_STRING_LENGTH:
            raise ValidationError(f"Total query string length exceeds maximum of {MAX_QUERY_STRING_LENGTH}")
        
        validated[validated_key] = value_str
    
    return validated


def sanitize_header_value(value: str) -> str:
    """
    Sanitize HTTP header value to prevent CRLF injection.
    
    Args:
        value: Header value to sanitize
        
    Returns:
        Sanitized header value
        
    Raises:
        ValidationError: If header value contains invalid characters
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Remove CRLF characters
    if '\r' in value or '\n' in value:
        raise ValidationError(
            "Header value contains invalid characters (CRLF injection attempt)"
        )
    
    # Remove null bytes
    if '\x00' in value:
        raise ValidationError(
            "Header value contains null bytes"
        )
    
    return value


def validate_header_name(name: str) -> str:
    """
    Validate HTTP header name.
    
    Security Note: This validation is more restrictive than the HTTP specification
    (RFC 7230) allows. While HTTP header names can technically contain more characters
    (including colons, spaces in quoted strings, etc.), we restrict to alphanumeric
    characters, underscores, and hyphens to prevent:
    - Header injection attacks (CRLF injection)
    - Invalid header construction
    - Potential parsing issues
    
    This is a security-focused trade-off for enhanced safety.
    
    Args:
        name: Header name to validate
        
    Returns:
        Validated header name
        
    Raises:
        ValidationError: If header name is invalid
    """
    if not name or not isinstance(name, str):
        raise ValidationError("Header name must be a non-empty string")
    
    # Header names should be alphanumeric with hyphens
    # Security: More restrictive than HTTP spec to prevent injection attacks
    if not re.match(r'^[a-zA-Z0-9_-]+$', name):
        raise ValidationError(
            "Header name contains invalid characters. "
            "Only alphanumeric characters, underscores, and hyphens are allowed. "
            "This is more restrictive than HTTP spec for security reasons."
        )
    
    return name


def validate_headers(headers: dict) -> dict:
    """
    Validate and sanitize HTTP headers.
    
    Args:
        headers: Dictionary of headers to validate
        
    Returns:
        Validated and sanitized headers dictionary
        
    Raises:
        ValidationError: If headers are invalid
    """
    if not isinstance(headers, dict):
        raise ValidationError("Headers must be a dictionary")
    
    validated = {}
    for name, value in headers.items():
        validated_name = validate_header_name(str(name))
        validated_value = sanitize_header_value(str(value))
        validated[validated_name] = validated_value
    
    return validated


def safe_json_loads(text: str, max_size: int = MAX_JSON_MESSAGE_SIZE, max_depth: int = MAX_JSON_DEPTH):
    """
    Safely parse JSON with size and depth limits to prevent JSON bomb attacks.
    
    Args:
        text: JSON string to parse
        max_size: Maximum size of JSON string in bytes
        max_depth: Maximum nesting depth
        
    Returns:
        Parsed JSON object
        
    Raises:
        ValueError: If JSON exceeds size or depth limits
        json.JSONDecodeError: If JSON is invalid
    """
    import json
    
    if not text:
        return None
    
    # Check size limit
    text_size = len(text.encode('utf-8')) if isinstance(text, str) else len(text)
    if text_size > max_size:
        raise ValueError(
            f"JSON message size ({text_size} bytes) exceeds maximum allowed size ({max_size} bytes)"
        )
    
    # Parse JSON
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        log_security_warning(
            "JSON decode error",
            exc_info=e,
            json_size=text_size
        )
        raise
    
    # Check depth using iterative approach to prevent stack overflow
    try:
        # Use iterative stack-based approach instead of recursion
        stack = [(data, 0)]  # (object, current_depth)
        while stack:
            obj, current_depth = stack.pop()
            
            if current_depth > max_depth:
                raise ValueError(
                    f"JSON nesting depth ({current_depth}) exceeds maximum allowed depth ({max_depth})"
                )
            
            if isinstance(obj, dict):
                for value in obj.values():
                    stack.append((value, current_depth + 1))
            elif isinstance(obj, list):
                for item in obj:
                    stack.append((item, current_depth + 1))
    except ValueError as e:
        log_security_error(
            "JSON depth limit exceeded - possible JSON bomb attack",
            exc_info=e
        )
        raise
    
    return data

