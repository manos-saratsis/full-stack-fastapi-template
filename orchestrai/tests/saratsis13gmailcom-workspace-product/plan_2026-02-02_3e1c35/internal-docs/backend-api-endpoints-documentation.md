I need to fetch the actual content of the route files to document the API endpoints properly.# Backend API Endpoints Documentation

## Overview

This document provides a complete reference for all REST API endpoints in the FastAPI backend. The API follows RESTful conventions and uses OAuth2 with Bearer tokens for authentication.

**Base URL**: `/api/v1` (all routes are prefixed with this in production)

**Source Files**:
- `backend/app/api/routes/login.py` - Authentication endpoints
- `backend/app/api/routes/users.py` - User management
- `backend/app/api/routes/items.py` - Items CRUD operations
- `backend/app/api/routes/utils.py` - Utility endpoints
- `backend/app/api/routes/private.py` - Private/internal endpoints

---

## Authentication

### POST `/login/access-token`

OAuth2 compatible token login endpoint to obtain an access token for authenticated requests.

**Rate Limit**: 5 requests per minute per IP address

**Request Body** (form-data):
```
username: string (email address)
password: string
```

**Response**: `Token`
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Status Codes**:
- `200`: Success
- `400`: Incorrect email/password or inactive user
- `429`: Rate limit exceeded

**Implementation**: `backend/app/api/routes/login.py:17-34`

**Example**:
```bash
curl -X POST "http://localhost/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=secretpass"
```

**Authentication Flow**:
1. Validates credentials via `crud.authenticate()`
2. Checks if user is active
3. Creates JWT token with expiration (default: configured in `settings.ACCESS_TOKEN_EXPIRE_MINUTES`)
4. Returns token for use in subsequent requests

---

### POST `/login/test-token`

Test if an access token is valid and retrieve the associated user.

**Authentication**: Required (Bearer token)

**Response**: `UserPublic`
```json
{
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "John Doe",
  "id": "uuid"
}
```

**Implementation**: `backend/app/api/routes/login.py:37-42`

---

### POST `/password-recovery/{email}`

Initiate password recovery process for a user. Sends a password reset email with a token.

**Rate Limit**: 3 requests per hour per IP address

**Path Parameters**:
- `email` (string): User's email address

**Response**: `Message`
```json
{
  "message": "Password recovery email sent"
}
```

**Status Codes**:
- `200`: Success (email sent)
- `404`: User with email not found
- `429`: Rate limit exceeded

**Implementation**: `backend/app/api/routes/login.py:45-66`

**Behavior**:
- Generates JWT password reset token via `generate_password_reset_token()`
- Sends email with reset link containing token
- Always returns success even if email not found (security best practice)

---

### POST `/reset-password/`

Reset user password using the token received via email.

**Authentication**: None required (uses token from email)

**Request Body**: `NewPassword`
```json
{
  "token": "string",
  "new_password": "string"
}
```

**Response**: `Message`
```json
{
  "message": "Password updated successfully"
}
```

**Status Codes**:
- `200`: Success
- `400`: Invalid token or inactive user
- `404`: User not found

**Implementation**: `backend/app/api/routes/login.py:69-90`

**Process**:
1. Verifies token and extracts email via `verify_password_reset_token()`
2. Looks up user by email
3. Validates user is active
4. Hashes new password with `get_password_hash()`
5. Updates user's password in database

---

### POST `/password-recovery-html-content/{email}`

**Admin Only** - Generate HTML content for password recovery email (for testing/preview).

**Authentication**: Required (superuser only)

**Path Parameters**:
- `email` (string): User's email address

**Response**: HTML content with password reset email

**Status Codes**:
- `200`: Success
- `404`: User not found
- `403`: Not authorized (non-superuser)

**Implementation**: `backend/app/api/routes/login.py:93-115`

---

## User Management

Router prefix: `/users`

### GET `/users/`

**Admin Only** - Retrieve paginated list of all users.

**Authentication**: Required (superuser only)

**Query Parameters**:
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100): Maximum number of records to return

**Response**: `UsersPublic`
```json
{
  "data": [
    {
      "email": "user@example.com",
      "is_active": true,
      "is_superuser": false,
      "full_name": "John Doe",
      "id": "uuid"
    }
  ],
  "count": 1
}
```

**Implementation**: `backend/app/api/routes/users.py:24-36`

---

### POST `/users/`

**Admin Only** - Create a new user (admin-initiated user creation).

**Authentication**: Required (superuser only)

**Request Body**: `UserCreate`
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_superuser": false
}
```

**Response**: `UserPublic`
```json
{
  "email": "newuser@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "Jane Doe",
  "id": "uuid"
}
```

**Status Codes**:
- `200`: Success
- `400`: User with email already exists
- `403`: Not authorized

**Implementation**: `backend/app/api/routes/users.py:39-59`

**Behavior**:
- Validates email uniqueness
- Creates user via `crud.create_user()`
- Sends welcome email if `settings.emails_enabled` is true
- Returns created user (without password)

---

### GET `/users/me`

Get the current authenticated user's profile.

**Authentication**: Required

**Response**: `UserPublic`
```json
{
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "John Doe",
  "id": "uuid"
}
```

**Implementation**: `backend/app/api/routes/users.py:103-108`

---

### PATCH `/users/me`

Update the current user's profile information.

**Authentication**: Required

**Request Body**: `UserUpdateMe`
```json
{
  "email": "newemail@example.com",
  "full_name": "John Updated"
}
```

**Response**: `UserPublic`

**Status Codes**:
- `200`: Success
- `409`: Email already exists for another user

**Implementation**: `backend/app/api/routes/users.py:62-78`

**Validation**:
- Checks if new email is already used by another user
- Only updates fields provided in request body (`exclude_unset=True`)

---

### PATCH `/users/me/password`

Update the current user's password.

**Authentication**: Required

**Request Body**: `UpdatePassword`
```json
{
  "current_password": "oldpassword",
  "new_password": "newpassword"
}
```

**Response**: `Message`
```json
{
  "message": "Password updated successfully"
}
```

**Status Codes**:
- `200`: Success
- `400`: Incorrect current password or new password same as current

**Implementation**: `backend/app/api/routes/users.py:81-100`

**Validation**:
- Verifies current password via `verify_password()`
- Ensures new password is different from current
- Hashes new password before storing

---

### DELETE `/users/me`

Delete the current user's account.

**Authentication**: Required

**Response**: `Message`
```json
{
  "message": "User deleted successfully"
}
```

**Status Codes**:
- `200`: Success
- `403`: Superusers cannot delete themselves

**Implementation**: `backend/app/api/routes/users.py:111-121`

**Restrictions**:
- Superuser accounts cannot be self-deleted (security measure)

---

### POST `/users/signup`

Public endpoint for user self-registration.

**Authentication**: None required

**Request Body**: `UserRegister`
```json
{
  "email": "newuser@example.com",
  "password": "securepassword",
  "full_name": "Jane Doe"
}
```

**Response**: `UserPublic`

**Status Codes**:
- `200`: Success
- `400`: User with email already exists

**Implementation**: `backend/app/api/routes/users.py:124-137`

**Behavior**:
- Validates email uniqueness
- Creates user with default permissions (non-superuser, active)
- Does not send welcome email (unlike admin-created users)

---

### GET `/users/{user_id}`

Get a specific user by their ID.

**Authentication**: Required

**Path Parameters**:
- `user_id` (UUID): User's unique identifier

**Response**: `UserPublic`

**Status Codes**:
- `200`: Success
- `403`: Not authorized (can only view own profile unless superuser)

**Implementation**: `backend/app/api/routes/users.py:140-154`

**Access Control**:
- Users can always view their own profile
- Superusers can view any user profile
- Regular users cannot view other users' profiles

---

### PATCH `/users/{user_id}`

**Admin Only** - Update any user's profile.

**Authentication**: Required (superuser only)

**Path Parameters**:
- `user_id` (UUID): User's unique identifier

**Request Body**: `UserUpdate`
```json
{
  "email": "updated@example.com",
  "full_name": "Updated Name",
  "is_active": false,
  "is_superuser": true
}
```

**Response**: `UserPublic`

**Status Codes**:
- `200`: Success
- `404`: User not found
- `409`: Email already exists for another user
- `403`: Not authorized

**Implementation**: `backend/app/api/routes/users.py:157-182`

---

### DELETE `/users/{user_id}`

**Admin Only** - Delete a user and all their associated items.

**Authentication**: Required (superuser only)

**Path Parameters**:
- `user_id` (UUID): User's unique identifier

**Response**: `Message`
```json
{
  "message": "User deleted successfully"
}
```

**Status Codes**:
- `200`: Success
- `404`: User not found
- `403`: Cannot delete self (superusers)

**Implementation**: `backend/app/api/routes/users.py:185-203`

**Cascade Behavior**:
- Deletes all items owned by the user (via `delete(Item).where(col(Item.owner_id) == user_id)`)
- Then deletes the user record
- Superusers cannot delete themselves (security measure)

---

## Items Management

Router prefix: `/items`

### GET `/items/`

Retrieve paginated list of items.

**Authentication**: Required

**Query Parameters**:
- `skip` (integer, default: 0): Number of records to skip
- `limit` (integer, default: 100): Maximum number of records to return

**Response**: `ItemsPublic`
```json
{
  "data": [
    {
      "id": "uuid",
      "title": "Item Title",
      "description": "Item description",
      "owner_id": "uuid"
    }
  ],
  "count": 1
}
```

**Implementation**: `backend/app/api/routes/items.py:11-38`

**Access Control**:
- **Superusers**: Can view all items in the system
- **Regular users**: Can only view their own items (filtered by `owner_id`)

---

### GET `/items/{id}`

Get a specific item by ID.

**Authentication**: Required

**Path Parameters**:
- `id` (UUID): Item's unique identifier

**Response**: `ItemPublic`
```json
{
  "id": "uuid",
  "title": "Item Title",
  "description": "Item description",
  "owner_id": "uuid"
}
```

**Status Codes**:
- `200`: Success
- `404`: Item not found
- `400`: Not enough permissions (not owner or superuser)

**Implementation**: `backend/app/api/routes/items.py:41-51`

---

### POST `/items/`

Create a new item.

**Authentication**: Required

**Request Body**: `ItemCreate`
```json
{
  "title": "New Item",
  "description": "Item description"
}
```

**Response**: `ItemPublic`
```json
{
  "id": "uuid",
  "title": "New Item",
  "description": "Item description",
  "owner_id": "uuid"
}
```

**Implementation**: `backend/app/api/routes/items.py:54-64`

**Behavior**:
- Automatically sets `owner_id` to current user's ID
- Creates item in database and returns full item with generated UUID

---

### PUT `/items/{id}`

Update an existing item.

**Authentication**: Required

**Path Parameters**:
- `id` (UUID): Item's unique identifier

**Request Body**: `ItemUpdate`
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response**: `ItemPublic`

**Status Codes**:
- `200`: Success
- `404`: Item not found
- `400`: Not enough permissions (not owner or superuser)

**Implementation**: `backend/app/api/routes/items.py:67-86`

**Access Control**:
- Users can only update their own items
- Superusers can update any item

---

### DELETE `/items/{id}`

Delete an item.

**Authentication**: Required

**Path Parameters**:
- `id` (UUID): Item's unique identifier

**Response**: `Message`
```json
{
  "message": "Item deleted successfully"
}
```

**Status Codes**:
- `200`: Success
- `404`: Item not found
- `400`: Not enough permissions (not owner or superuser)

**Implementation**: `backend/app/api/routes/items.py:89-102`

**Access Control**:
- Users can only delete their own items
- Superusers can delete any item

---

## Utility Endpoints

Router prefix: `/utils`

### POST `/utils/test-email/`

**Admin Only** - Send a test email to verify email configuration.

**Authentication**: Required (superuser only)

**Query Parameters**:
- `email_to` (EmailStr): Recipient email address

**Response**: `Message`
```json
{
  "message": "Test email sent"
}
```

**Status Code**: `201` Created

**Implementation**: `backend/app/api/routes/utils.py:11-23`

**Purpose**:
- Allows administrators to test email server configuration
- Generates test email via `generate_test_email()`
- Sends email via configured SMTP settings

---

### GET `/utils/health-check/`

Public health check endpoint to verify API is running.

**Authentication**: None required

**Response**: `boolean`
```json
true
```

**Implementation**: `backend/app/api/routes/utils.py:26-28`

**Use Cases**:
- Load balancer health checks
- Monitoring systems
- Container orchestration readiness probes

---

## Private/Internal Endpoints

Router prefix: `/private`

### POST `/private/users/`

Internal endpoint for programmatic user creation (no authentication required).

**Authentication**: None required

**Request Body**: `PrivateUserCreate`
```json
{
  "email": "internal@example.com",
  "password": "password",
  "full_name": "Internal User",
  "is_verified": false
}
```

**Response**: `UserPublic`

**Implementation**: `backend/app/api/routes/private.py:22-37`

**⚠️ Security Warning**:
- This endpoint has no authentication
- Should be restricted to internal network access only
- Not included in public API documentation
- Intended for service-to-service communication or internal tooling

---

## Common Response Models

### Message
```json
{
  "message": "string"
}
```
Used for simple success/confirmation responses.

### UserPublic
```json
{
  "email": "user@example.com",
  "is_active": true,
  "is_superuser": false,
  "full_name": "John Doe",
  "id": "uuid"
}
```

### ItemPublic
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "owner_id": "uuid"
}
```

### Token
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

---

## Authentication & Authorization

### Bearer Token Authentication

All protected endpoints require Bearer token authentication. Include the access token in the Authorization header:

```bash
Authorization: Bearer <access_token>
```

**Token Lifecycle**:
1. Obtain token via `POST /login/access-token`
2. Include token in Authorization header for protected endpoints
3. Token expires after configured time (default: `settings.ACCESS_TOKEN_EXPIRE_MINUTES`)
4. Obtain new token when expired

### Permission Levels

**Public**: No authentication required
- `POST /users/signup`
- `GET /utils/health-check/`
- `POST /private/users/` (internal only)

**Authenticated**: Requires valid access token
- `GET /users/me`
- `PATCH /users/me`
- All `/items/` endpoints

**Superuser Only**: Requires authenticated superuser
- `GET /users/`
- `POST /users/`
- `PATCH /users/{user_id}`
- `DELETE /users/{user_id}`
- `POST /utils/test-email/`

**Implementation**: Authorization checks via dependencies in `backend/app/api/deps.py`:
- `CurrentUser` - Validates authenticated user
- `get_current_active_superuser` - Validates superuser privileges

---

## Rate Limiting

Rate limiting is implemented using SlowAPI with IP-based tracking.

**Configured Limits**:
- `POST /login/access-token`: 5 requests/minute per IP
- `POST /password-recovery/{email}`: 3 requests/hour per IP

**Implementation**: `backend/app/api/routes/login.py`
```python
limiter = Limiter(key_func=get_remote_address)
@limiter.limit("5/minute")
```

**Response on Rate Limit Exceeded**:
- Status Code: `429 Too Many Requests`
- Headers include rate limit information

---

## Error Responses

### Standard Error Format

```json
{
  "detail": "Error message"
}
```

### Common Status Codes

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input or business logic error
- `401 Unauthorized`: Missing or invalid authentication token
- `403 Forbidden`: Authenticated but insufficient privileges
- `404 Not Found`: Resource does not exist
- `409 Conflict`: Resource conflict (e.g., duplicate email)
- `429 Too Many Requests`: Rate limit exceeded

### Example Error Responses

**Invalid credentials** (`400`):
```json
{
  "detail": "Incorrect email or password"
}
```

**Insufficient permissions** (`403`):
```json
{
  "detail": "The user doesn't have enough privileges"
}
```

**Resource not found** (`404`):
```json
{
  "detail": "Item not found"
}
```

---

## OpenAPI Documentation

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: `http://localhost/docs`
- **ReDoc**: `http://localhost/redoc`
- **OpenAPI JSON**: `http://localhost/openapi.json`

These interfaces provide:
- Interactive API testing
- Request/response schema validation
- Automatic authentication handling
- Code generation templates

---

## Database Dependencies

All endpoints use SQLModel/SQLAlchemy sessions injected via FastAPI dependencies:

```python
from app.api.deps import SessionDep

@router.get("/")
def endpoint(session: SessionDep):
    # session is automatically provided and managed
```

**Implementation**: `SessionDep` is defined in `backend/app/api/deps.py` and provides:
- Automatic session creation per request
- Transaction management (commit/rollback)
- Connection pooling
- Session cleanup after request

---

## CORS Configuration

Cross-Origin Resource Sharing (CORS) is configured in the main application. Frontend applications must be included in the allowed origins list (configured via environment variables).

---

## Development Notes

### Adding New Endpoints

1. Create or update route file in `backend/app/api/routes/`
2. Define Pydantic models in `backend/app/models/`
3. Import and register router in `backend/app/api/main.py`
4. Add CRUD operations in `backend/app/crud.py` if needed
5. Update this documentation

### Testing Endpoints

Use the included test suite or interactive docs:
- Unit tests: `backend/app/tests/`
- Swagger UI: `/docs` endpoint
- Integration tests should cover all authentication scenarios

### Schema Validation

All request/response data is validated using Pydantic models. Invalid data automatically returns `422 Unprocessable Entity` with validation error details.