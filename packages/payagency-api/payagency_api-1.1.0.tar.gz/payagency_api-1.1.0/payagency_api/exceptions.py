"""
Custom exceptions for PayAgency API SDK
"""


class PayAgencyError(Exception):
    """Base exception for PayAgency SDK errors"""
    
    def __init__(self, message: str, status_code: int = None, response: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response = response


class PayAgencyAPIError(PayAgencyError):
    """Exception raised for API errors from PayAgency"""
    pass


class PayAgencyNetworkError(PayAgencyError):
    """Exception raised for network-related errors"""
    pass


class PayAgencyValidationError(PayAgencyError):
    """Exception raised for input validation errors"""
    pass
