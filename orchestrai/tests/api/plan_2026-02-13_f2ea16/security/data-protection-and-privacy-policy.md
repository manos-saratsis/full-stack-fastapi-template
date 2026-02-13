# Data Protection and Privacy Policy

## Overview

This document outlines the data protection and privacy measures implemented in the Full Stack FastAPI Template application. The policy covers user data handling, storage security, encryption requirements, and compliance measures based on the actual implementation in `backend/app/models.py`, `backend/app/core/config.py`, and infrastructure configuration in `docker-compose.yml`.

## Data Classification

### Personal Identifiable Information (PII)

The application processes the following PII categories as defined in `backend/app/models.py`:

#### User Data Model (`User`)
- **Email Address** (`EmailStr`): Unique identifier, indexed, max 255 characters
- **Full Name** (`str | None`): Optional, max 255 characters
- **Password** (`hashed_password`): Stored in hashed format only
- **User ID** (`uuid.UUID`): Primary key using UUID4 generation
- **Account Status** (`is_active: bool`, `is_superuser: bool`)

#### Item Data Model (`Item`)
- **Title** (`str`): 1-255 characters
- **Description** (`str | None`): Optional, max 255 characters
- **Item ID** (`uuid.UUID`): Primary key using UUID4 generation
- **Owner Reference** (`owner_id: uuid.UUID`): Foreign key to user

## Data Storage Security

### Database Configuration

**PostgreSQL Database** (`docker-compose.yml: services.db`):

```yaml
Image: postgres:17
Volume: app-db-data:/var/lib/postgresql/data/pgdata
Environment Variables:
  - PGDATA=/var/lib/postgresql/data/pgdata
  - POSTGRES_PASSWORD (required)
  - POSTGRES_USER (required)
  - POSTGRES_DB (required)
```

**Data Persistence**:
- All user and item data persisted in named volume `app-db-data`
- Volume location: `/var/lib/postgresql/data/pgdata`
- Container restart policy: `always` (ensures data availability)

**Health Monitoring**:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 10s
  retries: 5
  start_period: 30s
  timeout: 10s
```

### Database Connection Security

**Connection String** (`backend/app/core/config.py`):
```python
@computed_field
@property
def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
    return MultiHostUrl.build(
        scheme="postgresql+psycopg",
        username=self.POSTGRES_USER,
        password=self.POSTGRES_PASSWORD,
        host=self.POSTGRES_SERVER,
        port=self.POSTGRES_PORT,
        path=self.POSTGRES_DB,
    )
```

**Security Measures**:
- Database credentials stored in environment variables
- Password required and validated (cannot be "changethis" in non-local environments)
- Internal Docker network isolation (database not exposed externally)
- Connection pooling through SQLAlchemy

## Encryption Requirements

### Passwords

**Storage** (`backend/app/models.py`):
- Passwords NEVER stored in plaintext
- Field name: `hashed_password: str` (database table)
- Input validation: 8-40 characters minimum/maximum length

**Password Constraints**:
```python
# UserCreate
password: str = Field(min_length=8, max_length=40)

# UserRegister
password: str = Field(min_length=8, max_length=40)

# UserUpdate
password: str | None = Field(default=None, min_length=8, max_length=40)

# UpdatePassword
current_password: str = Field(min_length=8, max_length=40)
new_password: str = Field(min_length=8, max_length=40)
```

### Transport Layer Security

**HTTPS Enforcement** (`docker-compose.yml`):
```yaml
# Backend HTTPS Configuration
- traefik.http.routers.${STACK_NAME}-backend-https.tls=true
- traefik.http.routers.${STACK_NAME}-backend-https.tls.certresolver=le
- traefik.http.routers.${STACK_NAME}-backend-http.middlewares=https-redirect

# Frontend HTTPS Configuration
- traefik.http.routers.${STACK_NAME}-frontend-https.tls=true
- traefik.http.routers.${STACK_NAME}-frontend-https.tls.certresolver=le
- traefik.http.routers.${STACK_NAME}-frontend-http.middlewares=https-redirect
```

**Certificate Management**:
- Let's Encrypt certificate resolver (`certresolver=le`)
- Automatic HTTP to HTTPS redirection via `https-redirect` middleware
- TLS enabled for all production endpoints

### Email Security

**SMTP Configuration** (`backend/app/core/config.py`):
```python
SMTP_TLS: bool = True
SMTP_SSL: bool = False
SMTP_PORT: int = 587
SMTP_HOST: str | None = None
SMTP_USER: str | None = None
SMTP_PASSWORD: str | None = None
```

**Requirements**:
- TLS encryption enabled by default (port 587)
- SMTP credentials stored in environment variables
- Secure transmission of password reset tokens

## Access Control

### Authentication Token Management

**JWT Token Configuration** (`backend/app/core/config.py`):
```python
SECRET_KEY: str = secrets.token_urlsafe(32)
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
```

**Token Structure** (`backend/app/models.py`):
```python
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: str | None = None
```

**Security Requirements**:
- Secret key generated using `secrets.token_urlsafe(32)` for cryptographic strength
- Secret key validation: Cannot be "changethis" in staging/production environments
- Token expiration: Maximum 8 days (11,520 minutes)
- Bearer token authentication scheme

### Password Reset Tokens

**Configuration** (`backend/app/core/config.py`):
```python
EMAIL_RESET_TOKEN_EXPIRE_HOURS: int = 48
```

**Token Model** (`backend/app/models.py`):
```python
class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
```

**Requirements**:
- Reset tokens expire after 48 hours
- Tokens transmitted only via secure email channel
- New password must meet length requirements (8-40 characters)

### User Authorization Levels

**Role-Based Access** (`backend/app/models.py`):
```python
class UserBase(SQLModel):
    is_active: bool = True
    is_superuser: bool = False
```

**Account States**:
- `is_active`: Controls account access (default: enabled)
- `is_superuser`: Administrative privileges flag (default: disabled)

**Initial Superuser** (`backend/app/core/config.py`):
```python
FIRST_SUPERUSER: EmailStr
FIRST_SUPERUSER_PASSWORD: str
```

## Data Retention and Deletion

### Cascade Deletion

**User-Item Relationship** (`backend/app/models.py`):
```python
class User(UserBase, table=True):
    items: list["Item"] = Relationship(back_populates="owner", cascade_delete=True)

class Item(ItemBase, table=True):
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
```

**Deletion Policy**:
- When a user is deleted, all associated items are automatically deleted
- Database-level cascade: `ondelete="CASCADE"` on foreign key
- Application-level cascade: `cascade_delete=True` in relationship
- No orphaned item data remains after user deletion

### Data Minimization

**Field Constraints** (`backend/app/models.py`):

| Field | Type | Required | Max Length | Purpose |
|-------|------|----------|------------|---------|
| email | EmailStr | Yes | 255 | Unique identifier |
| full_name | str | No | 255 | Optional display name |
| password | str | Yes | 40 | Authentication credential |
| title | str | Yes | 255 | Item identification |
| description | str | No | 255 | Item metadata |

**Principles**:
- Optional fields default to `None` (not collected unless provided)
- Maximum length constraints prevent excessive data storage
- No collection of sensitive data beyond authentication requirements

## User Consent and Data Rights

### Data Access

**Public API Models** (`backend/app/models.py`):
```python
class UserPublic(UserBase):
    id: uuid.UUID
    # Excludes: hashed_password

class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
```

**Privacy Controls**:
- Password hashes NEVER returned via API
- Users can access their own data through authenticated endpoints
- Public models explicitly exclude sensitive fields

### Self-Service Data Management

**User Update Models** (`backend/app/models.py`):
```python
class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)
```

**User Rights**:
- Update personal information (email, full_name)
- Change password with current password verification
- All update fields optional (partial updates supported)

## Cross-Border Data Transfer

### Network Architecture

**Service Isolation** (`docker-compose.yml`):
```yaml
networks:
  traefik-public:
    external: true
  default:
```

**Data Location**:
- Database accessible only within `default` internal network
- Backend services bridge both `traefik-public` and `default` networks
- Frontend/backend expose HTTPS endpoints via Traefik reverse proxy
- Database port (5432) not exposed externally

### CORS Configuration

**Cross-Origin Policy** (`backend/app/core/config.py`):
```python
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

**Requirements**:
- Explicit allowlist of cross-origin domains
- Frontend host automatically included
- Comma-separated or list format supported
- Trailing slashes normalized

## Environment-Specific Security

### Configuration Validation

**Secret Validation** (`backend/app/core/config.py`):
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

**Environment Enforcement**:
- `ENVIRONMENT`: `local`, `staging`, or `production`
- Local: Warnings for default secrets
- Staging/Production: Application fails to start with default secrets
- Mandatory validation for: `SECRET_KEY`, `POSTGRES_PASSWORD`, `FIRST_SUPERUSER_PASSWORD`

### Production Security Requirements

**Required Environment Variables** (`docker-compose.yml`):
```yaml
- SECRET_KEY=${SECRET_KEY?Variable not set}
- FIRST_SUPERUSER=${FIRST_SUPERUSER?Variable not set}
- FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD?Variable not set}
- POSTGRES_USER=${POSTGRES_USER?Variable not set}
- POSTGRES_PASSWORD=${POSTGRES_PASSWORD?Variable not set}
- FRONTEND_HOST=${FRONTEND_HOST?Variable not set}
```

**Deployment Checklist**:
- All required variables must be set (deployment fails otherwise)
- Secrets must not be default values
- Database credentials must be unique and strong
- Frontend host must match production domain

## Database Administration Security

### Adminer Access Control

**Configuration** (`docker-compose.yml`):
```yaml
adminer:
  image: adminer
  restart: always
  networks:
    - traefik-public
    - default
  depends_on:
    - db
  labels:
    - traefik.http.routers.${STACK_NAME}-adminer-https.rule=Host(`adminer.${DOMAIN}`)
    - traefik.http.routers.${STACK_NAME}-adminer-https.tls=true
    - traefik.http.routers.${STACK_NAME}-adminer-https.tls.certresolver=le
```

**Security Considerations**:
- Adminer exposed via HTTPS only (Let's Encrypt TLS)
- Subdomain: `adminer.${DOMAIN}`
- Requires database credentials for access
- Production deployments should restrict access via firewall rules or remove service

## Monitoring and Audit Logging

### Error Tracking

**Sentry Integration** (`backend/app/core/config.py`):
```python
SENTRY_DSN: HttpUrl | None = None
```

**Configuration** (`docker-compose.yml`):
```yaml
environment:
  - SENTRY_DSN=${SENTRY_DSN}
```

**Privacy Considerations**:
- Optional integration (None by default)
- When enabled, error reports may include request context
- Configure Sentry PII scrubbing for compliance
- Sentry DSN should be treated as sensitive configuration

## Compliance Status

### Data Protection Measures Summary

**Implemented Controls**:
- ✅ Password hashing (plaintext passwords never stored)
- ✅ Transport encryption (HTTPS/TLS via Let's Encrypt)
- ✅ Email encryption (SMTP TLS enabled)
- ✅ Cascade deletion (no orphaned user data)
- ✅ Data minimization (optional fields, length limits)
- ✅ Access control (JWT authentication, role-based authorization)
- ✅ Secret validation (prevents default credentials in production)
- ✅ Network isolation (database not publicly exposed)
- ✅ CORS policy (explicit origin allowlist)

**Compliance Gaps**:
- ⚠️ No explicit data retention period documented in code
- ⚠️ No automated backup encryption configuration visible
- ⚠️ No explicit audit logging implementation in provided files
- ⚠️ No data export functionality for user data portability
- ⚠️ No cookie consent or privacy policy acceptance tracking

### Regulatory Considerations

**GDPR Alignment**:
- **Right to Access**: Supported via authenticated API endpoints
- **Right to Rectification**: Supported via `UserUpdateMe` model
- **Right to Erasure**: Supported via cascade deletion
- **Data Minimization**: Optional fields, length constraints implemented
- **Consent Management**: Not implemented in provided code
- **Data Portability**: Export functionality not visible in models

**CCPA Alignment**:
- **Consumer Data Deletion**: Cascade deletion implemented
- **Data Access Requests**: API endpoints support data retrieval
- **Opt-Out Mechanisms**: Not implemented in provided code

## Incident Response

### Database Backup Recovery

**Volume Management** (`docker-compose.yml`):
```yaml
volumes:
  app-db-data:
```

**Backup Procedures** (Recommended):
```bash
# Backup command (not automated in provided configuration)
docker exec <db_container> pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup.sql

# Restore command
docker exec -i <db_container> psql -U ${POSTGRES_USER} ${POSTGRES_DB} < backup.sql
```

**Note**: Automated backup encryption and rotation not configured in provided files.

### Service Health Monitoring

**Health Checks** (`docker-compose.yml`):

**Database**:
```yaml
healthcheck:
  test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
  interval: 10s
  retries: 5
```

**Backend**:
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/utils/health-check/"]
  interval: 10s
  timeout: 5s
  retries: 5
```

**Availability Guarantees**:
- Automatic service restart on failure (`restart: always`)
- Dependent services wait for database health
- 5 retry attempts before marking unhealthy

## Configuration Reference

### Sensitive Environment Variables

| Variable | Purpose | Validation | Default |
|----------|---------|------------|---------|
| `SECRET_KEY` | JWT signing | Cannot be "changethis" | `secrets.token_urlsafe(32)` |
| `POSTGRES_PASSWORD` | Database auth | Cannot be "changethis" | None (required) |
| `FIRST_SUPERUSER_PASSWORD` | Admin account | Cannot be "changethis" | None (required) |
| `SMTP_PASSWORD` | Email auth | None | None (optional) |
| `POSTGRES_USER` | Database user | Required in deployment | None (required) |
| `POSTGRES_DB` | Database name | Required in deployment | None (required) |

### Data Model Index

**User Table** (`backend/app/models.py: User`):
- Primary Key: `id` (UUID)
- Unique Index: `email`
- Cascade Relationship: `items`

**Item Table** (`backend/app/models.py: Item`):
- Primary Key: `id` (UUID)
- Foreign Key: `owner_id` → `user.id` (CASCADE)

## Updates and Maintenance

**Configuration File**: `.env` (parent directory of backend)
**Settings Class**: `backend/app/core/config.py: Settings`
**Data Models**: `backend/app/models.py`
**Infrastructure**: `docker-compose.yml`

This policy reflects the implementation as of the current codebase version. Any changes to data handling practices must be documented through code updates in the referenced files.