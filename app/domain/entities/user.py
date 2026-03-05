from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import uuid4


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


@dataclass
class User:
    email: str
    name: str
    role: UserRole
    is_active: bool = True
    id: str = field(default_factory=lambda: str(uuid4()))
    password_hash: Optional[str] = None
    avatar_url: Optional[str] = None
    google_id: Optional[str] = None
    refresh_token: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self) -> None:
        self._validate()

    def _validate(self) -> None:
        if not self.email or not re.match(r"^[^@]+@[^@]+\.[^@]+$", self.email):
            raise ValueError("Invalid email address")
        if not self.name or len(self.name.strip()) < 2:
            raise ValueError("Name must be at least 2 characters")

    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN
