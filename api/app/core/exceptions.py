"""Domain exceptions.

Ported verbatim from core/exceptions.py. FastAPI exception handlers in
main.py convert these to HTTP responses with appropriate status codes.
"""


class AuthError(Exception):
    """Base class for authentication / authorization errors."""


class InvalidCredentialsError(AuthError):
    """Raised when email or password is wrong."""


class UserNotFoundError(AuthError):
    """Raised when an operation references an unknown user."""


class TokenExpiredError(AuthError):
    """Raised when a signed token (remember-me, password-reset) is past its max age."""


class TokenInvalidError(AuthError):
    """Raised when a signed token is malformed or tampered with."""


class UnauthorizedError(AuthError):
    """Raised when an authenticated user tries to access a protected resource."""
