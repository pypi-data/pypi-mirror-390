"""Custom exceptions for the pyarchiveit package."""


class Error(Exception):
    """Base exception for ArchiveIt-related errors."""


class InvalidAuthError(Error):
    """Raised when authentication credentials are invalid."""
