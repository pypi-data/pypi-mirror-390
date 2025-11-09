"""Custom exception classes for AutoSubtitle API."""


class AutoSubtitleError(Exception):
    """Base exception for AutoSubtitle API errors."""

    def __init__(self, message: str, status: int = None, code: str = None):
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.name = "AutoSubtitleError"

    def __str__(self) -> str:
        return self.message

