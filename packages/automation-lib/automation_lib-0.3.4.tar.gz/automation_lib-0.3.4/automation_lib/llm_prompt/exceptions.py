"""
Custom exceptions for the LLM Prompt module.
"""

class RateLimitExceededError(Exception):
    """
    Custom exception raised when an LLM provider's rate limit is exceeded.
    """
    def __init__(self, message="Rate limit exceeded for LLM provider.", original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception


class ContentFilteredError(Exception):
    """
    Custom exception raised when LLM response is blocked by content filters.
    """
    def __init__(self, message="Content was filtered by safety policies.", finish_reason=None, original_exception=None):
        super().__init__(message)
        self.finish_reason = finish_reason
        self.original_exception = original_exception


class EmptyResponseError(Exception):
    """
    Custom exception raised when LLM returns an empty response.
    """
    def __init__(self, message="LLM returned an empty response.", finish_reason=None, original_exception=None):
        super().__init__(message)
        self.finish_reason = finish_reason
        self.original_exception = original_exception
