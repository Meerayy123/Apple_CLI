# app/services/exceptions.py
class AppError(Exception):
    """Base app error shown to the user with a friendly message."""


class AuthError(AppError):
    """Login/authentication problems."""


class PermissionError(AppError):
    """User lacks permission for an action."""


class ValidationError(AppError):
    """Bad input or failed precondition."""


class NotFoundError(AppError):
    """Requested resource not found."""
