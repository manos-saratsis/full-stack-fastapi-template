# Authentication and Authorization Security Policy

## Overview

This document defines the authentication and authorization security policies for the FastAPI application. The implementation uses JWT (JSON Web Tokens) for stateless authentication, bcrypt for password hashing, and role-based access control (RBAC) for authorization.

## Authentication Architecture

### JWT Token-Based Authentication

**Implementation**: `backend/app/core/security.py`

The application uses JWT tokens with the following configuration:

```python
ALGORITHM = "HS256"

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

**Token Structure**:
- **Algorithm**: HS256 (HMAC with SHA-256)
- **Payload Fields**:
  - `exp`: Token expiration timestamp (UTC)
  - `sub`: Subject identifier (user ID as string)
- **Signing Key**: `settings.SECRET_KEY` (configured in environment)

### Token Validation Flow

**Implementation**: `backend/app/api/deps.py::get_current_user()`

```python
def get_current_user(session: SessionDep, token: TokenDep) -> User:
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
```

**Validation Steps**:
1. Decode JWT using SECRET_KEY and HS256 algorithm
2. Validate token structure against `TokenPayload` model
3. Retrieve user from database using subject ID
4. Verify user existence
5. Verify user is active

**Security Controls**:
- Invalid tokens return HTTP 403 Forbidden
- Missing users return HTTP 403 Forbidden
- Inactive users return HTTP 400 Bad Request

### OAuth2 Configuration

**Implementation**: `backend/app/api/deps.py`

```python
reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)
```

**OAuth2 Password Bearer Flow**:
- **Token Endpoint**: `{API_V1_STR}/login/access-token` (default: `/api/v1/login/access-token`)
- **Flow Type**: OAuth2 Password Bearer
- **Token Type**: Bearer token in Authorization header

## Token Expiration Policy

**Configuration**: `backend/app/core/config.py`

```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
```

**Access Token Lifetime**:
- **Default Duration**: 8 days (11,520 minutes)
- **Expiration Enforcement**: Handled by JWT `exp` claim validation
- **Timezone**: UTC (`datetime.now(timezone.utc)`)

**Token Expiration Behavior**:
- Expired tokens are rejected during JWT decoding
- No automatic token refresh mechanism
- Users must re-authenticate after expiration

## Password Security Requirements

### Password Complexity Policy

**Implementation**: `backend/app/models.py`

```python
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)

class UserRegister(SQLModel):
    password: str = Field(min_length=8, max_length=40)

class UserUpdate(UserBase):
    password: str | None = Field(default=None, min_length=8, max_length=40)

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

class NewPassword(SQLModel):
    new_password: str = Field(min_length=8, max_length=40)
```

**Password Requirements**:
- **Minimum Length**: 8 characters
- **Maximum Length**: 40 characters
- **Validation**: Enforced at API model level via Pydantic Field constraints

**Password Change Operations**:
- User creation: `UserCreate.password` validation
- User registration: `UserRegister.password` validation
- User update: `UserUpdate.password` validation (optional)
- Self-service password change: `UpdatePassword` requires current password
- Password reset: `NewPassword.new_password` validation

### Password Hashing

**Implementation**: `backend/app/core/security.py`

```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

**Hashing Configuration**:
- **Algorithm**: bcrypt
- **Library**: passlib with CryptContext
- **Deprecation Policy**: `deprecated="auto"` (automatic algorithm migration)
- **Storage**: `User.hashed_password` field in database

**Security Properties**:
- Bcrypt is a key derivation function with adaptive cost factor
- Resistant to rainbow table attacks (salt per password)
- Computationally expensive to prevent brute force attacks
- One-way hashing (passwords cannot be reversed)

## Role-Based Access Control (RBAC)

### User Roles

**Implementation**: `backend/app/models.py::User`

```python
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)
```

**Role Attributes**:
- `is_active`: Controls account activation status (default: `True`)
- `is_superuser`: Grants administrative privileges (default: `False`)

**Role Hierarchy**:
1. **Inactive User**: `is_active=False` - Cannot authenticate
2. **Active User**: `is_active=True`, `is_superuser=False` - Standard user
3. **Superuser**: `is_active=True`, `is_superuser=True` - Administrative user

### Authorization Enforcement

#### Active User Check

**Implementation**: `backend/app/api/deps.py::get_current_user()`

```python
if not user.is_active:
    raise HTTPException(status_code=400, detail="Inactive user")
```

**Enforcement Point**: All authenticated endpoints via `CurrentUser` dependency

#### Superuser Authorization

**Implementation**: `backend/app/api/deps.py::get_current_active_superuser()`

```python
def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
```

**Usage**: Administrative endpoints require `Depends(get_current_active_superuser)`

**Authorization Responses**:
- Non-superuser access to admin endpoints: HTTP 403 Forbidden
- Message: "The user doesn't have enough privileges"

### Dependency Injection Pattern

**Type Annotations**:
```python
SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]
CurrentUser = Annotated[User, Depends(get_current_user)]
```

**Usage in Endpoints**:
- `current_user: CurrentUser` - Requires valid JWT and active user
- `Depends(get_current_active_superuser)` - Requires superuser role

## Secret Management

### Secret Key Configuration

**Implementation**: `backend/app/core/config.py`

```python
SECRET_KEY: str = secrets.token_urlsafe(32)
```

**Generation**:
- **Method**: `secrets.token_urlsafe(32)` - cryptographically strong random string
- **Length**: 32 bytes (256 bits) URL-safe base64 encoded
- **Usage**: JWT signing and verification

### Secret Validation Policy

**Implementation**: `backend/app/core/config.py::Settings._enforce_non_default_secrets()`

```python
def _check_default_secret(self, var_name: str, value: str | None) -> None:
    if value == "changethis":
        message = (
            f'The value of {var_name} is "changethis", '
            "for security, please change it, at least for deployments."
        )
        if self.ENVIRONMENT == "local":
            warnings.warn(message, stacklevel=1)
        else:
            raise ValueError(message)

@model_validator(mode="after")
def _enforce_non_default_secrets(self) -> Self:
    self._check_default_secret("SECRET_KEY", self.SECRET_KEY)
    self._check_default_secret("POSTGRES_PASSWORD", self.POSTGRES_PASSWORD)
    self._check_default_secret(
        "FIRST_SUPERUSER_PASSWORD", self.FIRST_SUPERUSER_PASSWORD
    )
    return self
```

**Enforcement Rules**:
- **Local Environment**: Warning issued for default secrets
- **Staging/Production**: Application startup fails with ValueError
- **Validated Secrets**:
  - `SECRET_KEY`: JWT signing key
  - `POSTGRES_PASSWORD`: Database credentials
  - `FIRST_SUPERUSER_PASSWORD`: Initial admin account

## API Security Policies

### CORS (Cross-Origin Resource Sharing)

**Implementation**: `backend/app/core/config.py`

```python
FRONTEND_HOST: str = "http://localhost:5173"
BACKEND_CORS_ORIGINS: Annotated[
    list[AnyUrl] | str, BeforeValidator(parse_cors)
] = []

@computed_field
@property
def all_cors_origins(self) -> list[str]:
    return [str(origin).rstrip("/") for origin in self.BACKEND_CORS_ORIGINS] + [
        self.FRONTEND_HOST
    ]
```

**CORS Configuration**:
- **Frontend Host**: Automatically included in allowed origins
- **Additional Origins**: Configurable via `BACKEND_CORS_ORIGINS` environment variable
- **Format**: Comma-separated list or JSON array
- **Normalization**: Trailing slashes removed from all origins

### Rate Limiting

**Implementation**: `backend/app/api/deps.py`

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

**Rate Limiting Configuration**:
- **Library**: slowapi (FastAPI rate limiting middleware)
- **Key Function**: `get_remote_address` - limits by client IP address
- **Scope**: Global limiter instance available for endpoint decoration

**Implementation Note**: Rate limits must be configured per-endpoint using `@limiter.limit()` decorator.

## Session Management

### Stateless Authentication

**Architecture**:
- **Session Type**: Stateless (JWT-based)
- **No Server-Side Sessions**: No session storage or database tracking
- **Token Storage**: Client-side (typically in browser storage or mobile keychain)

**Session Properties**:
- **Duration**: Fixed 8-day lifetime per token
- **Revocation**: Not supported (stateless design)
- **Logout**: Client-side token deletion only

**Inactive Account Handling**:
```python
if not user.is_active:
    raise HTTPException(status_code=400, detail="Inactive user")
```
- Setting `is_active=False` prevents new authentication
- Existing valid tokens remain valid until expiration
- Database-level account status checked on each request

## Email-Based Security Features

### Password Reset Token Policy

**Configuration**: `backend/app/core/config.py`

```python
EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
```

**Password Reset Security**:
- **Token Lifetime**: 48 hours
- **Model**: `NewPassword` with `token` and `new_password` fields
- **New Password Requirements**: 8-40 character length enforced

**SMTP Configuration**:
```python
SMTP_TLS: bool = True
SMTP_SSL: bool = False
SMTP_PORT: int = 587
SMTP_HOST: str | None = None
SMTP_USER: str | None = None
SMTP_PASSWORD: str | None = None
EMAILS_FROM_EMAIL: EmailStr | None = None
```

**Email Security**:
- **Transport Encryption**: TLS enabled by default (port 587)
- **SSL**: Disabled by default
- **Availability Check**: `emails_enabled` property validates SMTP configuration

## Security Compliance Matrix

### Authentication Security Controls

| Control | Implementation | Status |
|---------|---------------|--------|
| Strong password policy | 8-40 character requirement | ✅ Enforced |
| Secure password storage | bcrypt hashing | ✅ Implemented |
| Token-based authentication | JWT with HS256 | ✅ Implemented |
| Token expiration | 8-day lifetime | ✅ Configured |
| Secret key validation | Startup validation | ✅ Enforced |
| Account activation | `is_active` flag | ✅ Implemented |

### Authorization Security Controls

| Control | Implementation | Status |
|---------|---------------|--------|
| Role-based access control | `is_superuser` flag | ✅ Implemented |
| Superuser authorization | `get_current_active_superuser()` | ✅ Implemented |
| Inactive account prevention | Active user check in auth flow | ✅ Enforced |
| Privilege escalation prevention | Explicit superuser check | ✅ Implemented |

### API Security Controls

| Control | Implementation | Status |
|---------|---------------|--------|
| CORS configuration | Configurable allowed origins | ✅ Implemented |
| Rate limiting framework | slowapi integration | ✅ Available |
| Input validation | Pydantic models with constraints | ✅ Enforced |
| Secure token transmission | OAuth2 Bearer in Authorization header | ✅ Implemented |

## Security Recommendations

### Critical Actions Required

1. **SECRET_KEY Configuration**:
   - Generate unique SECRET_KEY for each environment
   - Never use default value in production
   - Rotate keys periodically (requires re-authentication)

2. **Password Policy Enhancement**:
   - Current policy only enforces length (8-40 characters)
   - Consider adding complexity requirements (uppercase, lowercase, numbers, symbols)
   - Implement password history to prevent reuse

3. **Token Revocation**:
   - Current stateless design cannot revoke valid tokens
   - Consider implementing token blacklist for critical security events
   - Alternative: Reduce token lifetime for high-security contexts

4. **Rate Limiting**:
   - `limiter` instance configured but not applied to endpoints
   - Implement rate limits on authentication endpoints
   - Recommended: 5 login attempts per 15 minutes per IP

### Operational Security Practices

1. **Account Management**:
   - Use `is_active=False` to disable compromised accounts
   - Review superuser accounts regularly
   - Monitor failed authentication attempts

2. **Environment Configuration**:
   - Validate all secrets in staging/production environments
   - Use environment-specific SECRET_KEY values
   - Secure `.env` files with appropriate file permissions

3. **Password Reset Flow**:
   - 48-hour token expiration limits exposure window
   - Invalidate reset tokens after use
   - Send confirmation emails on password changes

## User Model Security Schema

**Implementation**: `backend/app/models.py::User`

```python
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)
```

**Security-Relevant Fields**:
- `id`: UUID v4 primary key (non-sequential, prevents enumeration)
- `email`: Unique indexed field for authentication
- `hashed_password`: bcrypt hash (never exposed via API)
- `is_active`: Account status flag
- `is_superuser`: Administrative privileges flag

**Data Protection**:
- `UserPublic` model excludes `hashed_password` from API responses
- Email uniqueness enforced at database level
- Cascade delete on user removal (`cascade_delete=True` on relationships)