"""Custom exceptions for the MrMonei SDK"""

class MoneiAPIError(Exception):
    """Base exception for all MrMonei API errors"""
    def __init__(self, message: str, status_code: int = None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response

class AuthenticationError(MoneiAPIError):
    """Raised when authentication fails"""
    pass

class ValidationError(MoneiAPIError):
    """Raised when input validation fails"""
    pass

class NotFoundError(MoneiAPIError):
    """Raised when a resource is not found"""
    pass

class RateLimitError(MoneiAPIError):
    """Raised when rate limit is exceeded"""
    pass

class InsufficientBalanceError(MoneiAPIError):
    """Raised when insufficient balance for transaction"""
    pass