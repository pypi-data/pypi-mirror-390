from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional


@dataclass
class User:
    id: str
    email: str
    name: str
    status: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class AuthResponse:
    default_org_name: Optional[str]
    token: str
    user: User
    workspaces_and_tenants: Optional[List[Dict[str, Any]]] = None


@dataclass
class RegisterResponse:
    user: User


@dataclass
class ForgotPasswordResponse:
    success: bool


@dataclass
class ResetPasswordResponse:
    success: bool


@dataclass
class UserRegisterInput:
    email: str
    name: str
    password: str
