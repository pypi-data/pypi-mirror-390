"""
Custom exceptions for Cortefy client
"""


class CortefyException(Exception):
    """Base exception for all Cortefy errors"""
    pass


class AuthenticationError(CortefyException):
    """Raised when API key authentication fails"""
    pass


class APIError(CortefyException):
    """Raised when API returns an error response"""
    def __init__(self, message, status_code=None, response=None):
        super().__init__(message)
        self.status_code = status_code
        self.response = response


class ValidationError(CortefyException):
    """Raised when request validation fails"""
    pass

