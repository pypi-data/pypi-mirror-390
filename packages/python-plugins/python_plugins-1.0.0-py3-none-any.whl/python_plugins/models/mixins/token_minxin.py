from typing import Optional
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
import secrets

def secret_token():
    return secrets.token_hex(32)


class TokenMixin:
    token: Mapped[Optional[str]] = mapped_column(unique=True, default=secret_token)
