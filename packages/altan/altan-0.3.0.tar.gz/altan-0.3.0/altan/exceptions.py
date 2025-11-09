"""
Custom exceptions for the Altan SDK
"""

class AltanSDKError(Exception):
    """Base exception for Altan SDK"""
    pass

class AltanAPIError(AltanSDKError):
    """Exception raised for API errors"""
    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data

class AltanConnectionError(AltanSDKError):
    """Exception raised for connection errors"""
    pass

class AltanAuthenticationError(AltanSDKError):
    """Exception raised for authentication errors"""
    pass
