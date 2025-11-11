"""Custom exceptions for Mia21 SDK."""


class Mia21Error(Exception):
    """Base exception for Mia21 SDK."""
    pass


class ChatNotInitializedError(Mia21Error):
    """Chat session not initialized."""
    pass


class APIError(Mia21Error):
    """API request failed."""
    pass


class ValidationError(Mia21Error):
    """Request validation failed."""
    pass


class RateLimitError(Mia21Error):
    """Rate limit exceeded."""
    pass





