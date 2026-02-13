# Application Threat Model and Risk Assessment

## Executive Summary

This threat model identifies security risks across the full-stack FastAPI application, analyzing attack surfaces in authentication, authorization, API endpoints, data handling, and infrastructure components. The assessment covers backend API vulnerabilities, frontend client-side risks, database security, and deployment infrastructure threats.

## System Architecture Overview

**Components:**
- **Backend API**: FastAPI application (`backend/app/`)
- **Frontend**: React/TypeScript client (`frontend/src/`)
- **Database**: PostgreSQL 17 (`db` service)
- **Reverse Proxy**: Traefik with TLS termination
- **Database Admin**: Adminer interface
- **Infrastructure**: Docker containerized deployment

## Threat Categories and Attack Vectors

### 1. Authentication and Session Management Threats

#### 1.1 JWT Token Security Vulnerabilities

**Location**: `backend/app/core/security.py`

**Threat**: JWT Secret Key Compromise
- **Attack Vector**: Weak or exposed `SECRET_KEY` environment variable
- **Implementation**: `jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)` uses HS256 symmetric signing
- **Impact**: Critical - Complete authentication bypass, token forgery
- **Risk Score**: Critical (9.5/10)
- **Indicators**:
  - Secret key in `docker-compose.yml`: `SECRET_KEY=${SECRET_KEY?Variable not set}`
  - No key rotation mechanism implemented
  - Single shared secret across all tokens

**Mitigation Controls**:
- Environment variable validation enforced: `${SECRET_KEY?Variable not set}`
- SECRET_KEY must be cryptographically random (implementation responsibility)
- Recommendation: Implement RS256 asymmetric signing for production

**Threat**: Token Expiration Bypass
- **Attack Vector**: Long-lived tokens without refresh mechanism
- **Implementation**: `create_access_token(subject: str | Any, expires_delta: timedelta)` accepts arbitrary expiration
- **Impact**: High - Extended access window after credential compromise
- **Risk Score**: High (7.5/10)
- **Code Reference**: No maximum expiration validation in security.py

**Mitigation Controls**:
- Caller controls `expires_delta` parameter
- Recommendation: Enforce maximum token lifetime limits

#### 1.2 Password Storage Vulnerabilities

**Location**: `backend/app/core/security.py`

**Threat**: Weak Password Hashing Configuration
- **Implementation**: `pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")`
- **Risk Score**: Low-Medium (4.0/10)
- **Analysis**:
  - Bcrypt is cryptographically secure
  - No work factor configuration visible
  - Default bcrypt rounds may be insufficient for high-security contexts

**Mitigation Controls**:
- Industry-standard bcrypt algorithm
- Automatic deprecation handling
- Recommendation: Explicitly set work factor (rounds=12 minimum)

### 2. Authorization and Access Control Threats

#### 2.1 Broken Object Level Authorization (BOLA)

**Location**: `backend/app/api/routes/items.py`

**Threat**: Insufficient Ownership Verification
- **Attack Vector**: User accesses items owned by other users
- **Risk Score**: Critical (9.0/10)
- **Evidence Required**: Need to examine item ownership checks in CRUD operations
- **Standard Pattern**: Must verify `item.owner_id == current_user.id`

**Location**: `backend/app/api/routes/users.py`

**Threat**: User Profile Access Control
- **Attack Vector**: Users modifying other user profiles
- **Risk Score**: Critical (9.0/10)
- **Required Controls**:
  - Role-based access (superuser vs regular user)
  - Owner-based access (user can only modify own profile)
  - Admin privilege escalation prevention

#### 2.2 Function Level Authorization Bypass

**Location**: `backend/app/api/routes/private.py`

**Threat**: Administrative Function Exposure
- **Risk Score**: High (8.0/10)
- **Evidence**: File exists but contents not provided
- **Assumption**: Contains privileged operations requiring strict role checks
- **Required Controls**: Superuser/admin role verification

**Location**: `backend/app/api/routes/users.py`

**Threat**: User Management Authorization
- **Risk Score**: Critical (9.5/10)
- **Operations at Risk**:
  - User creation
  - User deletion
  - Password reset
  - Role assignment
- **Required Controls**: Multi-level authorization checks

### 3. Injection Attack Vectors

#### 3.1 SQL Injection

**Risk Assessment**: Low-Medium (3.0/10)
- **Assumption**: Using SQLAlchemy ORM (standard for FastAPI templates)
- **Protection**: Parameterized queries via ORM
- **Residual Risk**: Raw SQL queries if present
- **Verification Needed**: Confirm no raw SQL in database layer

#### 3.2 Command Injection

**Location**: `backend/scripts/prestart.sh`

**Threat**: Initialization Script Vulnerabilities
- **Risk Score**: High (7.0/10)
- **Attack Vector**: Malicious environment variables in startup script
- **Evidence**: `docker-compose.yml` executes `bash scripts/prestart.sh`
- **Environment Variables Passed**:
  - `FIRST_SUPERUSER`
  - `FIRST_SUPERUSER_PASSWORD`
  - Database credentials

**Mitigation Controls**:
- Environment variable validation: `${VARIABLE?Variable not set}` pattern
- Container isolation limits impact
- Recommendation: Validate and sanitize all environment variables

#### 3.3 NoSQL/ORM Injection

**Risk Score**: Medium (5.0/10)
- **Threat**: Mass assignment vulnerabilities
- **Attack Vector**: User-controlled filter parameters
- **Required Analysis**: Query construction in routes/items.py and routes/users.py

### 4. Cross-Site Scripting (XSS) Threats

#### 4.1 Frontend Client-Side XSS

**Location**: `frontend/src/client/`

**Threat**: API Response Rendering
- **Risk Score**: High (7.5/10)
- **Attack Vector**: Unsanitized user-generated content rendered in React
- **Evidence**: Generated TypeScript client files:
  - `frontend/src/client/types.gen.ts`
  - `frontend/src/client/sdk.gen.ts`
  - `frontend/src/client/schemas.gen.ts`

**Mitigation Controls**:
- React default XSS protection (JSX escaping)
- Risk remains with `dangerouslySetInnerHTML` if used
- API schema validation via generated types

**Threat**: Stored XSS via API Data
- **Risk Score**: High (8.0/10)
- **Attack Vector**: Malicious content in item descriptions, user names, etc.
- **Storage**: PostgreSQL database
- **Rendering**: React components via generated SDK
- **Required Controls**:
  - Input validation at API layer
  - Content Security Policy headers
  - Output encoding in frontend

#### 4.2 API Response Header Injection

**Risk Score**: Medium (5.0/10)
- **Threat**: User-controlled data in HTTP headers
- **Protection**: FastAPI framework header handling
- **Residual Risk**: Custom header manipulation

### 5. Authentication Bypass Vulnerabilities

#### 5.1 Login Endpoint Security

**Location**: `backend/app/api/routes/login.py`

**Threat**: Brute Force Attacks
- **Risk Score**: High (7.5/10)
- **Attack Vector**: Unlimited login attempts
- **Evidence**: No rate limiting visible in provided files
- **Impact**: Account compromise via credential stuffing

**Mitigation Requirements**:
- Rate limiting middleware
- Account lockout after failed attempts
- CAPTCHA for suspicious traffic
- IP-based throttling

**Threat**: Timing Attacks
- **Risk Score**: Medium (5.5/10)
- **Attack Vector**: Username enumeration via response timing
- **Implementation**: `verify_password(plain_password, hashed_password)` constant-time comparison
- **Protection**: Bcrypt provides timing attack resistance
- **Residual Risk**: Different response times for valid/invalid users

#### 5.2 Password Reset Vulnerabilities

**Location**: `backend/app/api/routes/login.py`

**Threat**: Password Reset Token Prediction
- **Risk Score**: High (8.0/10)
- **Required Analysis**: Token generation mechanism
- **Attack Vector**: Weak random number generation
- **Impact**: Account takeover

**Threat**: Password Reset Email Spoofing
- **Evidence**: SMTP configuration in `docker-compose.yml`:
  ```
  SMTP_HOST=${SMTP_HOST}
  SMTP_USER=${SMTP_USER}
  SMTP_PASSWORD=${SMTP_PASSWORD}
  EMAILS_FROM_EMAIL=${EMAILS_FROM_EMAIL}
  ```
- **Risk Score**: Medium (6.0/10)
- **Required Controls**: SPF, DKIM, DMARC validation

### 6. Data Exposure and Privacy Risks

#### 6.1 Sensitive Data in Transit

**Location**: `docker-compose.yml`

**Threat**: TLS Configuration Weaknesses
- **Risk Score**: Medium (6.0/10)
- **Implementation**: Traefik TLS with Let's Encrypt
- **Evidence**:
  ```yaml
  traefik.http.routers.backend-https.tls=true
  traefik.http.routers.backend-https.tls.certresolver=le
  ```
- **Protection**: Automatic HTTPS redirect middleware
- **Residual Risk**: TLS version/cipher configuration not specified

**Mitigation Controls**:
- HTTPS enforcement: `traefik.http.routers.backend-http.middlewares=https-redirect`
- Automated certificate renewal via Let's Encrypt
- Recommendation: Explicitly configure TLS 1.2+ only

#### 6.2 Sensitive Data at Rest

**Location**: Database volume in `docker-compose.yml`

**Threat**: Unencrypted Database Storage
- **Risk Score**: High (7.5/10)
- **Implementation**: PostgreSQL 17 with persistent volume
- **Evidence**: `app-db-data:/var/lib/postgresql/data/pgdata`
- **Protection**: None visible (filesystem-level encryption required)
- **Impact**: Data breach if host compromised or volume extracted

**Threat**: Database Credential Exposure
- **Risk Score**: Critical (9.0/10)
- **Evidence**: Environment variables in docker-compose.yml:
  ```yaml
  POSTGRES_PASSWORD=${POSTGRES_PASSWORD?Variable not set}
  POSTGRES_USER=${POSTGRES_USER?Variable not set}
  POSTGRES_DB=${POSTGRES_DB?Variable not set}
  ```
- **Protection**: Environment variable indirection (.env file)
- **Residual Risk**: .env file security, container environment inspection

#### 6.3 API Response Over-Exposure

**Location**: API routes and generated schemas

**Threat**: Excessive Data Disclosure
- **Risk Score**: Medium (6.0/10)
- **Evidence**: Generated TypeScript types (`frontend/src/client/types.gen.ts`)
- **Attack Vector**: API responses include unnecessary sensitive fields
- **Examples**:
  - User objects with internal IDs
  - Timestamps revealing system behavior
  - Relationship data exposing associations

**Mitigation Requirements**:
- Response schema DTOs separate from database models
- Field-level permissions
- Explicit include/exclude lists per endpoint

### 7. CORS and Cross-Origin Threats

**Location**: `docker-compose.yml` backend configuration

**Threat**: Overly Permissive CORS
- **Risk Score**: High (7.0/10)
- **Implementation**: `BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}`
- **Attack Vector**: Malicious site accessing authenticated API
- **Impact**: CSRF, data theft, unauthorized actions

**Mitigation Requirements**:
- Whitelist specific origins only
- Avoid wildcard (*) in production
- Credentials mode validation
- Preflight request handling

### 8. Infrastructure and Deployment Threats

#### 8.1 Container Security Vulnerabilities

**Location**: `docker-compose.yml` service definitions

**Threat**: Privileged Container Execution
- **Risk Score**: Medium (6.0/10)
- **Evidence**: No explicit privilege restrictions visible
- **Impact**: Container escape vulnerabilities
- **Recommendation**: Add `privileged: false`, `read_only: true` where possible

**Threat**: Container Image Vulnerabilities
- **Risk Score**: High (7.0/10)
- **Images**:
  - `postgres:17` (base image vulnerabilities)
  - `adminer` (third-party admin tool)
  - Custom backend/frontend builds
- **Required Controls**: Regular vulnerability scanning, image updates

#### 8.2 Network Segmentation Weaknesses

**Location**: `docker-compose.yml` networks

**Threat**: Insufficient Network Isolation
- **Risk Score**: Medium (5.5/10)
- **Implementation**:
  ```yaml
  networks:
    traefik-public:
      external: true
  ```
- **Evidence**: Services share default network and traefik-public
- **Attack Vector**: Lateral movement between containers
- **Required Controls**: Separate networks per trust boundary

#### 8.3 Database Administration Interface Exposure

**Location**: `docker-compose.yml` adminer service

**Threat**: Adminer Public Exposure
- **Risk Score**: Critical (9.0/10)
- **Implementation**: Exposed via Traefik with public DNS
- **Evidence**:
  ```yaml
  traefik.http.routers.adminer-https.rule=Host(`adminer.${DOMAIN}`)
  traefik.http.routers.adminer-https.entrypoints=https
  ```
- **Impact**: Direct database access interface available to attackers
- **Attack Vector**: Brute force database credentials, exploit Adminer vulnerabilities

**Mitigation Controls**:
- TLS encryption enforced
- Recommendation: IP whitelist, VPN requirement, or remove from production

#### 8.4 Health Check Information Disclosure

**Location**: `docker-compose.yml` backend healthcheck

**Threat**: Health Check Endpoint Exposure
- **Risk Score**: Low (3.0/10)
- **Implementation**: `curl -f http://localhost:8000/api/v1/utils/health-check/`
- **Evidence**: Accessible health check endpoint
- **Impact**: System information disclosure, deployment state visibility
- **Mitigation**: Internal-only access, minimal information disclosure

#### 8.5 Environment Variable Injection

**Threat**: Environment Variable Manipulation
- **Risk Score**: High (8.0/10)
- **Attack Vector**: Malicious values in .env file or orchestration system
- **Critical Variables**:
  - `SECRET_KEY`: Authentication compromise
  - `FIRST_SUPERUSER_PASSWORD`: Admin access
  - `SENTRY_DSN`: Monitoring data exfiltration
  - `BACKEND_CORS_ORIGINS`: CORS bypass
  - Database credentials

**Mitigation Controls**:
- Required variable validation: `${VAR?Variable not set}` pattern
- Recommendation: Secret management system (Vault, AWS Secrets Manager)

### 9. Third-Party Dependency Risks

#### 9.1 Backend Dependencies

**Critical Security Libraries**:
- **jwt**: Token signing (`backend/app/core/security.py`)
  - Risk: Vulnerabilities in JWT implementation
  - Mitigation: Regular updates, CVE monitoring
- **passlib**: Password hashing
  - Risk: Cryptographic weaknesses
  - Mitigation: Bcrypt scheme, stay current
- **FastAPI**: Framework vulnerabilities
  - Risk: Request parsing, validation bypass
  - Mitigation: Version pinning, security advisories

#### 9.2 Frontend Dependencies

**Location**: `frontend/src/client/`

**Generated Client Code Risks**:
- **Risk Score**: Medium (5.0/10)
- **Files**: `sdk.gen.ts`, `schemas.gen.ts`, `types.gen.ts`
- **Threat**: Code generation vulnerabilities
- **Attack Vector**: Malicious API schema causing XSS or code injection
- **Mitigation**: Validate OpenAPI schema source, review generated code

### 10. Business Logic Vulnerabilities

#### 10.1 Item Management Threats

**Location**: `backend/app/api/routes/items.py`

**Threat**: Resource Exhaustion
- **Risk Score**: High (7.0/10)
- **Attack Vector**: Unlimited item creation per user
- **Impact**: Database storage exhaustion, performance degradation
- **Required Controls**: Item count limits per user, rate limiting

**Threat**: Item Data Manipulation
- **Risk Score**: High (7.5/10)
- **Attack Vector**: Malicious content in item fields
- **Required Validation**:
  - Input length limits
  - Content type validation
  - Special character sanitization

#### 10.2 User Management Threats

**Location**: `backend/app/api/routes/users.py`

**Threat**: User Enumeration
- **Risk Score**: Medium (6.0/10)
- **Attack Vector**: Different responses for existing vs non-existing users
- **Endpoints at Risk**:
  - User lookup by email
  - Password reset
  - Registration
- **Impact**: Privacy violation, targeted attacks

**Threat**: Privilege Escalation
- **Risk Score**: Critical (9.5/10)
- **Attack Vector**: Regular user elevating to superuser
- **Required Controls**:
  - Immutable superuser flag after creation
  - Admin-only user role modification
  - Audit logging of permission changes

## Risk Prioritization Matrix

### Critical Risks (Immediate Action Required)

1. **JWT Secret Key Management** (9.5/10)
   - Implement secret rotation
   - Use asymmetric signing
   - Secure secret storage

2. **Privilege Escalation Prevention** (9.5/10)
   - Verify all user management operations
   - Implement role-based access control
   - Audit permission changes

3. **Adminer Public Exposure** (9.0/10)
   - Remove from production or restrict access
   - Implement IP whitelisting
   - Require VPN/bastion access

4. **Broken Object Level Authorization** (9.0/10)
   - Implement ownership verification on all resources
   - Add integration tests for authorization
   - Review all CRUD endpoints

5. **Database Credential Security** (9.0/10)
   - Use secret management system
   - Rotate credentials regularly
   - Implement connection encryption

### High Risks (Address Within Sprint)

6. **Brute Force Attack Prevention** (7.5/10)
7. **Password Reset Security** (8.0/10)
8. **Database Encryption at Rest** (7.5/10)
9. **XSS via Stored Content** (8.0/10)
10. **Environment Variable Injection** (8.0/10)
11. **CORS Misconfiguration** (7.0/10)
12. **Container Image Vulnerabilities** (7.0/10)

### Medium Risks (Plan for Resolution)

13. **Token Expiration Controls** (7.5/10)
14. **TLS Configuration Hardening** (6.0/10)
15. **Network Segmentation** (5.5/10)
16. **User Enumeration** (6.0/10)
17. **API Response Over-Exposure** (6.0/10)

## Security Testing Recommendations

### 1. Automated Security Scanning

**Static Analysis**:
```bash
# Backend
bandit -r backend/app/
semgrep --config=auto backend/

# Frontend
npm audit
eslint --plugin security frontend/src/
```

**Dependency Scanning**:
```bash
# Backend
safety check
pip-audit

# Frontend
npm audit
snyk test
```

**Container Scanning**:
```bash
trivy image ${DOCKER_IMAGE_BACKEND}
trivy image ${DOCKER_IMAGE_FRONTEND}
trivy image postgres:17
trivy image adminer
```

### 2. Dynamic Application Security Testing (DAST)

**API Security Testing**:
- OWASP ZAP automated scan
- Burp Suite professional scan
- Custom API fuzzing with Postman/Newman
- SQL injection testing with SQLMap

**Target Endpoints**:
- `/api/v1/login/`
- `/api/v1/users/`
- `/api/v1/items/`
- `/api/v1/utils/`

### 3. Manual Security Testing

**Authentication Testing**:
1. JWT token manipulation (algorithm confusion, signature bypass)
2. Token expiration validation
3. Password reset flow security
4. Session fixation attempts
5. Concurrent session handling

**Authorization Testing**:
1. Horizontal privilege escalation (user accessing other user resources)
2. Vertical privilege escalation (user to admin)
3. Missing function-level access control
4. Forced browsing to administrative functions
5. Parameter tampering for ownership bypass

**Injection Testing**:
1. SQL injection on all input parameters
2. NoSQL/ORM injection via filter parameters
3. Command injection in file operations
4. LDAP injection if directory integration exists
5. XML injection if XML processing exists

**Business Logic Testing**:
1. Resource exhaustion (unlimited item creation)
2. Race conditions (concurrent updates)
3. Workflow bypass (skip required steps)
4. Price/amount manipulation if applicable
5. Negative testing (invalid state transitions)

### 4. Infrastructure Security Testing

**Container Security**:
```bash
# Check for privileged containers
docker inspect <container_id> | grep -i privileged

# Verify read-only filesystems
docker inspect <container_id> | grep -i readonly

# Check user context
docker inspect <container_id> | grep -i user
```

**Network Security**:
```bash
# Verify network isolation
docker network inspect traefik-public
docker network inspect <stack>_default

# Test service accessibility
nmap -sV -p- <host>
```

**TLS Configuration**:
```bash
# Test TLS configuration
testssl.sh https://api.${DOMAIN}
testssl.sh https://dashboard.${DOMAIN}

# Verify certificate
openssl s_client -connect api.${DOMAIN}:443 -servername api.${DOMAIN}
```

### 5. Compliance and Audit Testing

**Security Headers**:
```bash
# Test security headers
curl -I https://api.${DOMAIN}
# Verify: Strict-Transport-Security, X-Frame-Options, X-Content-Type-Options, CSP

curl -I https://dashboard.${DOMAIN}
# Verify: CSP, X-XSS-Protection, Referrer-Policy
```

**Logging and Monitoring**:
1. Verify authentication events logged
2. Verify authorization failures logged
3. Test log injection prevention
4. Verify sensitive data not logged (passwords, tokens)
5. Test Sentry error tracking (if SENTRY_DSN configured)

## Incident Response Readiness

### Detection Capabilities Required

1. **Authentication Anomalies**:
   - Multiple failed login attempts
   - Login from unusual locations/IPs
   - Token replay attempts
   - Expired token usage

2. **Authorization Violations**:
   - Access denied events (should trigger alerts)
   - Privilege escalation attempts
   - Cross-user resource access attempts

3. **Injection Attempts**:
   - SQL error patterns in logs
   - Special characters in unexpected fields
   - Command execution failures

4. **Infrastructure Anomalies**:
   - Container restarts
   - Database connection failures
   - Unusual network traffic patterns
   - Certificate expiration warnings

### Response Procedures

**Authentication Compromise**:
1. Rotate SECRET_KEY immediately
2. Invalidate all existing tokens
3. Force password reset for affected users
4. Review authentication logs
5. Implement additional MFA if not present

**Data Breach**:
1. Isolate affected containers
2. Capture forensic snapshots
3. Review database access logs
4. Identify scope of exposure
5. Execute data breach notification procedures

**Infrastructure Compromise**:
1. Isolate affected containers from network
2. Capture container state for analysis
3. Review docker logs and host logs
4. Rebuild containers from clean images
5. Rotate all credentials and secrets

## Compliance Considerations

### GDPR Requirements

**Personal Data Handling**:
- User email addresses (identifiable)
- User names (potentially identifiable)
- IP addresses in logs (identifiable)
- Authentication timestamps (behavioral data)

**Required Controls**:
- Right to erasure implementation
- Data export functionality
- Consent management
- Data retention policies
- Privacy policy disclosure

### OWASP Top 10 2021 Mapping

1. **A01:2021 - Broken Access Control**: Sections 2.1, 2.2, 10.2
2. **A02:2021 - Cryptographic Failures**: Sections 1.1, 1.2, 6.1, 6.2
3. **A03:2021 - Injection**: Section 3
4. **A04:2021 - Insecure Design**: Section 10
5. **A05:2021 - Security Misconfiguration**: Sections 7, 8.2, 8.3
6. **A06:2021 - Vulnerable and Outdated Components**: Section 9
7. **A07:2021 - Identification and Authentication Failures**: Sections 1, 5
8. **A08:2021 - Software and Data Integrity Failures**: Section 9.2
9. **A09:2021 - Security Logging and Monitoring Failures**: Incident Response section
10. **A10:2021 - Server-Side Request Forgery**: Not directly applicable (no URL fetching observed)

## Secure Development Lifecycle Integration

### Pre-Commit Controls

```bash
# Security linting
pre-commit install
# Configure hooks for:
# - Secret scanning (detect-secrets, truffleHog)
# - Dependency checking (safety, npm audit)
# - Static analysis (bandit, semgrep)
```

### CI/CD Pipeline Security Gates

**Required Checks**:
1. SAST scan passes (no high/critical findings)
2. Dependency vulnerability scan passes
3. Container image scan passes
4. Unit tests for authorization checks pass
5. Integration tests for authentication pass

**Deployment Controls**:
1. Require manual approval for production
2. Verify environment variable configuration
3. Validate TLS certificate status
4. Confirm backup procedures executed
5. Test rollback procedures

### Security Code Review Checklist

**Authentication/Authorization**:
- [ ] All endpoints have authentication requirements
- [ ] Authorization checks verify resource ownership
- [ ] No hard-coded credentials
- [ ] Password policies enforced
- [ ] Token expiration validated

**Input Validation**:
- [ ] All user input validated
- [ ] Length limits enforced
- [ ] Type checking implemented
- [ ] Special characters sanitized
- [ ] File upload restrictions (if applicable)

**Data Protection**:
- [ ] Sensitive data encrypted in transit (HTTPS)
- [ ] Passwords properly hashed
- [ ] No sensitive data in logs
- [ ] Database connection encrypted
- [ ] API responses filtered (no over-exposure)

**Infrastructure**:
- [ ] Environment variables validated
- [ ] Secrets not in source code
- [ ] Container privileges minimized
- [ ] Network segmentation implemented
- [ ] Health check data minimized

## Continuous Monitoring Requirements

### Metrics to Track

1. **Authentication Metrics**:
   - Failed login rate
   - Account lockout frequency
   - Password reset requests
   - Token validation failures

2. **Authorization Metrics**:
   - Access denied events per user
   - Admin action frequency
   - Cross-user access attempts
   - Permission escalation attempts

3. **Performance Metrics (Security Impact)**:
   - API response times (potential DoS)
   - Database query times (injection attempts)
   - Error rates (exploitation attempts)
   - Request size distribution (payload attacks)

4. **Infrastructure Metrics**:
   - Container restart frequency
   - Database connection failures
   - Certificate expiration countdown
   - Disk space utilization (log injection)

### Alert Thresholds

**Critical Alerts (Immediate Response)**:
- 10+ failed logins per user in 5 minutes
- Privilege escalation attempt detected
- Database credential authentication failure
- Container unexpected restart
- TLS certificate expiration < 7 days

**High Priority Alerts (Response within 1 hour)**:
- 50+ failed logins per IP in 10 minutes
- 5+ authorization failures per user in 5 minutes
- Error rate > 10% on authentication endpoints
- Unusual admin action pattern
- Container health check failures

**Medium Priority Alerts (Response within 4 hours)**:
- Error rate > 5% on any endpoint
- Unusual request size distribution
- Database connection pool exhaustion
- Slow query detected (potential injection)
- Certificate expiration < 30 days

---

**Document Version**: 1.0  
**Last Updated**: 2024  
**Classification**: Internal Security Documentation  
**Review Frequency**: Quarterly or after significant application changes