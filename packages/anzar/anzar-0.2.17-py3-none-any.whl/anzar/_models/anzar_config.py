from enum import Enum
from pydantic import BaseModel


## ------------------------------------------------------------
class DatabaseDriver(str, Enum):
    SQLite = "SQLite"
    PostgreSQL = "PostgreSQL"
    MongoDB = "MongoDB"


class Database(BaseModel):
    driver: DatabaseDriver
    connection_string: str


## ------------------------------------------------------------
class HttpsConfig(BaseModel):
    enabled: bool = False
    port: int = 3000
    cert_path: str | None = None
    key_path: str | None = None


class CorsConfig(BaseModel):
    allowed_origins: list[str] = ["http://localhost:3000"]


class Server(BaseModel):
    https: HttpsConfig | None = None
    cors: CorsConfig | None = None


## ------------------------------------------------------------
class AuthStrategy(str, Enum):
    Jwt = "Jwt"
    Session = "Session"


class JWT(BaseModel):
    expires_in: int | None = None
    refresh_expires_in: int | None = None


class EmailVerification(BaseModel):
    required: bool | None = None
    token_expires_in: int | None = None


class EmailConfig(BaseModel):
    verification: EmailVerification | None = None


class PasswordRequirements(BaseModel):
    min_length: int | None = None
    max_length: int | None = None


class PasswordReset(BaseModel):
    token_expires_in: int | None = None


class PasswordSecurity(BaseModel):
    max_failed_login_attempts: int | None = None
    lockout_duration: int | None = None


class PasswordConfig(BaseModel):
    requirements: PasswordRequirements | None = None
    reset: PasswordReset | None = None
    security: PasswordSecurity | None = None


class Authentication(BaseModel):
    strategy: AuthStrategy | None = None
    jwt: JWT | None = None
    email: EmailConfig | None = None
    password: PasswordConfig | None = None


## ------------------------------------------------------------
class Security(BaseModel):
    secret_key: str


## ------------------------------------------------------------
class AnzarConfig(BaseModel):
    api_url: str
    database: Database
    security: Security
    server: Server | None = None
    auth: Authentication | None = None
