from dataclasses import dataclass


@dataclass
class Config:
  """Configuration for an API Session.

  Fields:
    server_id: Identifier (subdomain) for the game server (required). E.g., "us1".
    email: User email for login (required). E.g., "user@example.com".
    password: User password for login (required). E.g., "securepassword".
    impersonate: User agent or impersonation hint used by the HTTP client. E.g., "chrome".
    timeout: Request timeout in seconds. E.g., 5.0.
  """

  server_id: str
  email: str
  password: str
  impersonate: str = "chrome"
  timeout: float = 5.0
  login_retries: int = 2

  def __post_init__(self):
    for field in ('email', 'password', 'server_id'):
      value = getattr(self, field)
      if not value or not isinstance(value, str):
        raise ValueError(f"{field} must be a non-empty string")

  @property
  def base_url(self) -> str:
    """Construct the base URL for the game server."""
    return f"https://{self.server_id}.herozerogame.com"
