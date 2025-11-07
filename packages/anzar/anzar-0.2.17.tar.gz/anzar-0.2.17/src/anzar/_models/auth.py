from pydantic import BaseModel, EmailStr

from anzar._models.session import Session

from .user import User


class EmailRequest(BaseModel):
    email: EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class SuccessResponse(BaseModel):
    message: str


class ResetLink(BaseModel):
    link: str
    expires_at: str


# Authentication Response
class SessionTokens(BaseModel):
    access: str
    refresh: str


class Verification(BaseModel):
    token: str
    link: str


class AuthResponse(BaseModel):
    user: User
    tokens: SessionTokens | None = None
    verification: Verification | None = None


class AuthPayload(BaseModel):
    user: User
    verification: Verification | None = None


class AuthUser(BaseModel):
    user: User
    session: Session | None = None
