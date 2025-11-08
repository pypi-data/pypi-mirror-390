"""Custom exceptions for hzclient."""

class GameClientError(Exception):
  """Base exception for hzclient."""


class AuthError(GameClientError):
  """Authentication related errors."""


class RequestError(GameClientError):
  """Errors related to sending requests."""


class ConstantError(GameClientError):
  """Errors related to constants initialization."""


class InitializationError(GameClientError):
  """Errors during client initialization."""