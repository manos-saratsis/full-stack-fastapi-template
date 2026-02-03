# CycloneDX SBOM Generation and Management

## Overview

This document provides comprehensive guidance for generating and maintaining Software Bill of Materials (SBOM) in CycloneDX format for the full-stack FastAPI application. The system includes both backend Python dependencies and frontend JavaScript dependencies, requiring a unified approach to SBOM generation, vulnerability scanning, license compliance, and validation.

## Dependency Inventory

### Backend Python Dependencies

**Source:** `backend/pyproject.toml`

#### Production Dependencies

| Component | Version Constraint | Purpose |
|-----------|-------------------|---------|
| fastapi[standard] | >=0.114.2,<1.0.0 | Core web framework |
| python-multipart | >=0.0.7,<1.0.0 | Form data parsing |
| email-validator | >=2.1.0.post1,<3.0.0.0 | Email validation |
| passlib[bcrypt] | >=1.7.4,<2.0.0 | Password hashing |
| tenacity | >=8.2.3,<9.0.0 | Retry logic |
| pydantic | >2.0 | Data validation |
| emails | >=0.6,<1.0 | Email functionality |
| jinja2 | >=3.1.4,<4.0.0 | Template engine |
| alembic | >=1.12.1,<2.0.0 | Database migrations |
| httpx | >=0.25.1,<1.0.0 | HTTP client |
| psycopg[binary] | >=3.1.13,<4.0.0 | PostgreSQL adapter |
| sqlmodel | >=0.0.21,<1.0.0 | SQL ORM |
| bcrypt | ==4.3.0 | Cryptographic hashing (pinned) |
| pydantic-settings | >=2.2.1,<3.0.0 | Settings management |
| sentry-sdk[fastapi] | >=1.40.6,<2.0.0 | Error tracking |
| pyjwt | >=2.8.0,<3.0.0 | JWT token handling |

#### Development Dependencies

| Component | Version Constraint | Purpose |
|-----------|-------------------|---------|
| pytest | >=7.4.3,<8.0.0 | Testing framework |
| mypy | >=1.8.0,<2.0.0 | Type checking |
| ruff | >=0.2.2,<1.0.0 | Linting and formatting |
| pre-commit | >=3.6.2,<4.0.0 | Git hooks |
| types-passlib | >=1.7.7.20240106,<2.0.0.0 | Type stubs |
| coverage | >=7.4.3,<8.0.0 | Code coverage |

**Python Version Requirement:** `>=3.10,<4.0`

### Frontend JavaScript Dependencies

**Source:** `frontend/package.json`

#### Production Dependencies

| Component | Version | Purpose |
|-----------|---------|---------|
| @chakra-ui/react | ^3.8.0 | UI component library |
| @emotion/react | ^11.14.0 | CSS-in-JS styling |
| @tanstack/react-query | ^5.28.14 | Data fetching/caching |
| @tanstack/react-query-devtools | ^5.74.9 | Query debugging tools |
| @tanstack/react-router | 1.19.1 | Routing library |
| axios | 1.9.0 | HTTP client |
| form-data | 4.0.2 | Form data handling |
| next-themes | ^0.4.6 | Theme management |
| react | ^18.2.0 | Core UI framework |
| react-dom | ^18.2.0 | React DOM renderer |
| react-error-boundary | ^5.0.0 | Error handling |
| react-hook-form | 7.49.3 | Form management |
| react-icons | ^5.5.0 | Icon library |

#### Development Dependencies

| Component | Version | Purpose |
|-----------|---------|---------|
| @biomejs/biome | 1.9.4 | Linting and formatting |
| @hey-api/openapi-ts | ^0.57.0 | OpenAPI client generation |
| @playwright/test | ^1.52.0 | End-to-end testing |
| @tanstack/router-devtools | 1.19.1 | Router debugging |
| @tanstack/router-vite-plugin | 1.19.0 | Vite integration |
| @types/node | ^22.15.3 | Node.js type definitions |
| @types/react | ^18.2.37 | React type definitions |
| @types/react-dom | ^18.2.15 | React DOM type definitions |
| @vitejs/plugin-react-swc | ^3.9.0 | React plugin for Vite |
| dotenv | ^16.4.5 | Environment variable management |
| typescript | ^5.2.2 | TypeScript compiler |
| vite | ^6.3.4 | Build tool |

## CycloneDX SBOM Generation

### Backend SBOM Generation (Python)

#### Using CycloneDX Python Tool

**Installation:**
```bash
pip install cyclonedx-bom
```

**Generate SBOM from pyproject.toml:**
```bash
# Navigate to backend directory
cd backend

# Generate SBOM in JSON format
cyclonedx-py poetry -o sbom-backend.json --format json

# Generate SBOM in XML format
cyclonedx-py poetry -o sbom-backend.xml --format xml
```

**Alternative: Using pip-audit with CycloneDX output:**
```bash
# Install pip-audit
pip install pip-audit

# Generate SBOM with vulnerability data
pip-audit --format cyclonedx-json --output sbom-backend-vuln.json
```

#### SBOM Metadata Configuration

**Component Definition:**
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:<generate-unique-uuid>",
  "version": 1,
  "metadata": {
    "component": {
      "type": "application",
      "name": "fastapi-backend",
      "version": "0.1.0",
      "description": "FastAPI backend application",
      "licenses": [
        {
          "license": {
            "id": "PROPRIETARY"
          }
        }
      ],
      "purl": "pkg:pypi/app@0.1.0"
    },
    "tools": [
      {
        "vendor": "CycloneDX",
        "name": "cyclonedx-python",
        "version": "latest"
      }
    ]
  }
}
```

### Frontend SBOM Generation (JavaScript)

#### Using CycloneDX Node Module

**Installation:**
```bash
npm install -g @cyclonedx/cyclonedx-npm
```

**Generate SBOM from package.json:**
```bash
# Navigate to frontend directory
cd frontend

# Generate SBOM in JSON format
cyclonedx-npm --output-file sbom-frontend.json --output-format json

# Generate SBOM in XML format
cyclonedx-npm --output-file sbom-frontend.xml --output-format xml

# Include development dependencies
cyclonedx-npm --output-file sbom-frontend-full.json --output-format json --package-lock-only false
```

**Alternative: Using npm sbom command (npm 9+):**
```bash
npm sbom --sbom-format cyclonedx --output sbom-frontend.json
```

#### SBOM Metadata Configuration

**Component Definition:**
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:<generate-unique-uuid>",
  "version": 1,
  "metadata": {
    "component": {
      "type": "application",
      "name": "frontend",
      "version": "0.0.0",
      "description": "React frontend application",
      "licenses": [
        {
          "license": {
            "id": "PROPRIETARY"
          }
        }
      ],
      "purl": "pkg:npm/frontend@0.0.0"
    }
  }
}
```

### Unified SBOM Generation

#### Merging Backend and Frontend SBOMs

**Using CycloneDX CLI:**
```bash
# Install CycloneDX CLI
npm install -g @cyclonedx/cyclonedx-cli

# Merge SBOMs
cyclonedx-cli merge \
  --input-files sbom-backend.json sbom-frontend.json \
  --output-file sbom-unified.json \
  --format json
```

**Manual Merge Structure:**
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:<unique-uuid>",
  "version": 1,
  "metadata": {
    "component": {
      "type": "application",
      "name": "full-stack-fastapi-template",
      "version": "0.1.0",
      "description": "Full-stack application with FastAPI backend and React frontend"
    }
  },
  "components": [
    {
      "type": "application",
      "name": "backend",
      "bom-ref": "backend-component",
      "components": []
    },
    {
      "type": "application",
      "name": "frontend",
      "bom-ref": "frontend-component",
      "components": []
    }
  ],
  "dependencies": []
}
```

## Vulnerability Scanning Integration

### Backend Vulnerability Scanning

#### Using pip-audit

**Command:**
```bash
cd backend

# Scan dependencies for vulnerabilities
pip-audit --format json --output vulnerabilities-backend.json

# Generate SBOM with vulnerability annotations
pip-audit --format cyclonedx-json --output sbom-backend-vuln.json

# Scan with specific severity threshold
pip-audit --vulnerability-service osv --format json
```

**Critical Dependencies for Security Monitoring:**

- **bcrypt==4.3.0**: Pinned for passlib compatibility - monitor for security updates
- **pyjwt>=2.8.0**: JWT handling - critical for authentication security
- **passlib[bcrypt]>=1.7.4**: Password hashing - requires regular updates
- **fastapi[standard]>=0.114.2**: Core framework - monitor for security patches
- **psycopg[binary]>=3.1.13**: Database connection - SQL injection prevention

#### Using Safety

**Command:**
```bash
# Install Safety
pip install safety

# Scan dependencies
safety check --json --output vulnerabilities-safety.json

# Scan with SBOM generation
safety check --output cyclonedx --save-as sbom-safety.json
```

### Frontend Vulnerability Scanning

#### Using npm audit

**Command:**
```bash
cd frontend

# Audit dependencies
npm audit --json > vulnerabilities-frontend.json

# Audit with specific severity
npm audit --audit-level=moderate

# Generate audit report
npm audit --production
```

**Critical Dependencies for Security Monitoring:**

- **axios@1.9.0**: HTTP client - monitor for SSRF and request smuggling vulnerabilities
- **react@^18.2.0**: Core framework - XSS prevention updates
- **react-dom@^18.2.0**: DOM renderer - XSS prevention updates
- **@tanstack/react-query@^5.28.14**: Data fetching - ensure secure request handling

#### Using Snyk

**Command:**
```bash
# Install Snyk CLI
npm install -g snyk

# Authenticate
snyk auth

# Test dependencies
snyk test --json > vulnerabilities-snyk.json

# Monitor project
snyk monitor

# Generate SBOM with Snyk data
snyk sbom --format cyclonedx1.4+json > sbom-snyk.json
```

### Integrating Vulnerability Data into SBOM

**CycloneDX Vulnerability Extension:**
```json
{
  "vulnerabilities": [
    {
      "bom-ref": "vulnerability-1",
      "id": "CVE-XXXX-XXXXX",
      "source": {
        "name": "NVD",
        "url": "https://nvd.nist.gov/"
      },
      "ratings": [
        {
          "source": {
            "name": "NVD"
          },
          "score": 7.5,
          "severity": "high",
          "method": "CVSSv3"
        }
      ],
      "affects": [
        {
          "ref": "pkg:pypi/component@version"
        }
      ]
    }
  ]
}
```

## License Compliance Tracking

### Backend License Detection

#### Using pip-licenses

**Installation and Usage:**
```bash
# Install pip-licenses
pip install pip-licenses

# Generate license report
cd backend
pip-licenses --format json --output-file licenses-backend.json

# Generate with package URLs
pip-licenses --format json --with-urls --output-file licenses-backend-full.json

# Check for specific license types
pip-licenses --summary
```

**Known License Considerations:**

- **FastAPI**: MIT License - permissive
- **Pydantic**: MIT License - permissive
- **SQLModel**: MIT License - permissive
- **Alembic**: MIT License - permissive
- **Passlib**: BSD License - permissive
- **bcrypt**: Apache 2.0 License - permissive
- **Sentry SDK**: BSD-2-Clause License - permissive

#### License Data in CycloneDX

**Structure:**
```json
{
  "components": [
    {
      "name": "fastapi",
      "version": "0.114.2",
      "licenses": [
        {
          "license": {
            "id": "MIT",
            "url": "https://opensource.org/licenses/MIT"
          }
        }
      ]
    }
  ]
}
```

### Frontend License Detection

#### Using license-checker

**Installation and Usage:**
```bash
# Install license-checker
npm install -g license-checker

# Generate license report
cd frontend
license-checker --json --out licenses-frontend.json

# Check for specific licenses
license-checker --onlyAllow "MIT;Apache-2.0;BSD-2-Clause;BSD-3-Clause;ISC"

# Detailed report with package paths
license-checker --json --relativeLicensePath --out licenses-frontend-full.json
```

**Known License Considerations:**

- **React**: MIT License - permissive
- **@chakra-ui/react**: MIT License - permissive
- **@tanstack/react-query**: MIT License - permissive
- **@tanstack/react-router**: MIT License - permissive
- **axios**: MIT License - permissive
- **TypeScript**: Apache 2.0 License - permissive
- **Vite**: MIT License - permissive

#### Using npm-license-crawler

**Command:**
```bash
npm install -g npm-license-crawler

cd frontend
npm-license-crawler --json licenses-crawler.json --onlyDirectDependencies
```

### License Compliance Automation

**Script for Combined License Check:**
```bash
#!/bin/bash

# Check backend licenses
cd backend
pip-licenses --fail-on "GPL;AGPL;LGPL" --format json --output-file licenses-backend.json

# Check frontend licenses  
cd ../frontend
license-checker --failOn "GPL;AGPL;LGPL" --json --out licenses-frontend.json

# Exit with error if forbidden licenses found
echo "License compliance check completed"
```

## SBOM Validation Procedures

### Validation Tools

#### CycloneDX CLI Validation

**Command:**
```bash
# Install validator
npm install -g @cyclonedx/cyclonedx-cli

# Validate SBOM against schema
cyclonedx-cli validate --input-file sbom-unified.json --input-format json --spec-version 1.5

# Validate with specific schema version
cyclonedx-cli validate --input-file sbom-backend.xml --input-format xml --spec-version 1.5
```

#### Python Validation Script

**Using cyclonedx-python-lib:**
```python
from cyclonedx.model.bom import Bom
from cyclonedx.output.json import JsonV1Dot5
from cyclonedx.validation.json import JsonStrictValidator
import json

def validate_sbom(sbom_file):
    """Validate CycloneDX SBOM file"""
    with open(sbom_file, 'r') as f:
        sbom_data = json.load(f)
    
    validator = JsonStrictValidator(JsonV1Dot5)
    validation_errors = validator.validate_str(json.dumps(sbom_data))
    
    if validation_errors:
        print(f"Validation errors found: {validation_errors}")
        return False
    else:
        print("SBOM validation successful")
        return True

# Usage
validate_sbom('sbom-unified.json')
```

### Validation Checklist

#### Required Fields

- [ ] `bomFormat`: Must be "CycloneDX"
- [ ] `specVersion`: Must match CycloneDX specification (e.g., "1.5")
- [ ] `serialNumber`: Unique URN in format `urn:uuid:<uuid>`
- [ ] `version`: Integer version of the BOM
- [ ] `metadata.component`: Application metadata
- [ ] `components`: Array of all dependencies

#### Component Requirements

For each component:
- [ ] `type`: Component type (library, application, framework)
- [ ] `name`: Component name
- [ ] `version`: Semantic version
- [ ] `purl`: Package URL if available
- [ ] `licenses`: License information
- [ ] `hashes`: File integrity hashes (SHA-256, SHA-512)

#### Dependency Graph Validation

```bash
# Verify dependency relationships
cyclonedx-cli analyze --input-file sbom-unified.json

# Check for circular dependencies
cyclonedx-cli validate --input-file sbom-unified.json --fail-on-errors
```

### Automated Validation Pipeline

**GitHub Actions Workflow Example:**
```yaml
name: SBOM Validation

on:
  pull_request:
    paths:
      - 'backend/pyproject.toml'
      - 'frontend/package.json'
      - 'sbom-*.json'

jobs:
  validate-sbom:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Install CycloneDX CLI
        run: npm install -g @cyclonedx/cyclonedx-cli
      
      - name: Validate Backend SBOM
        run: cyclonedx-cli validate --input-file sbom-backend.json
      
      - name: Validate Frontend SBOM
        run: cyclonedx-cli validate --input-file sbom-frontend.json
      
      - name: Validate Unified SBOM
        run: cyclonedx-cli validate --input-file sbom-unified.json
```

## Automated SBOM Generation Workflow

### CI/CD Integration

#### GitHub Actions Complete Workflow

```yaml
name: Generate and Validate SBOM

on:
  push:
    branches: [main]
  schedule:
    - cron: '0 0 * * 0'  # Weekly on Sunday

jobs:
  generate-sbom:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'
      
      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18'
      
      - name: Install Backend Dependencies
        run: |
          cd backend
          pip install cyclonedx-bom pip-audit
      
      - name: Generate Backend SBOM
        run: |
          cd backend
          cyclonedx-py poetry -o sbom-backend.json --format json
          pip-audit --format cyclonedx-json --output sbom-backend-vuln.json
      
      - name: Install Frontend Dependencies
        run: |
          cd frontend
          npm install -g @cyclonedx/cyclonedx-npm
      
      - name: Generate Frontend SBOM
        run: |
          cd frontend
          npm install
          cyclonedx-npm --output-file sbom-frontend.json --output-format json
      
      - name: Install CycloneDX CLI
        run: npm install -g @cyclonedx/cyclonedx-cli
      
      - name: Merge SBOMs
        run: |
          cyclonedx-cli merge \
            --input-files backend/sbom-backend.json frontend/sbom-frontend.json \
            --output-file sbom-unified.json
      
      - name: Validate SBOM
        run: cyclonedx-cli validate --input-file sbom-unified.json
      
      - name: Upload SBOM Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: sbom-files
          path: |
            backend/sbom-backend*.json
            frontend/sbom-frontend.json
            sbom-unified.json
      
      - name: Scan for Vulnerabilities
        run: |
          cd backend
          pip-audit --format json --output vulnerabilities.json
          cd ../frontend
          npm audit --json > vulnerabilities.json
      
      - name: Upload Vulnerability Reports
        uses: actions/upload-artifact@v4
        with:
          name: vulnerability-reports
          path: |
            backend/vulnerabilities.json
            frontend/vulnerabilities.json
```

### Local Development Script

**Script: `scripts/generate-sbom.sh`**
```bash
#!/bin/bash
set -e

echo "=== Generating SBOM for Full-Stack Application ==="

# Backend SBOM
echo "Generating backend SBOM..."
cd backend
python -m pip install cyclonedx-bom pip-audit
cyclonedx-py poetry -o sbom-backend.json --format json
pip-audit --format cyclonedx-json --output sbom-backend-vuln.json
cd ..

# Frontend SBOM
echo "Generating frontend SBOM..."
cd frontend
npm install -g @cyclonedx/cyclonedx-npm
cyclonedx-npm --output-file sbom-frontend.json --output-format json
cd ..

# Merge SBOMs
echo "Merging SBOMs..."
npm install -g @cyclonedx/cyclonedx-cli
cyclonedx-cli merge \
  --input-files backend/sbom-backend.json frontend/sbom-frontend.json \
  --output-file sbom-unified.json

# Validate
echo "Validating unified SBOM..."
cyclonedx-cli validate --input-file sbom-unified.json

echo "=== SBOM generation complete ==="
echo "Files generated:"
echo "  - backend/sbom-backend.json"
echo "  - backend/sbom-backend-vuln.json"
echo "  - frontend/sbom-frontend.json"
echo "  - sbom-unified.json"
```

### Scheduled Updates

**Cron Job for Regular SBOM Updates:**
```bash
# Add to crontab: Update SBOM weekly
0 0 * * 0 cd /path/to/project && ./scripts/generate-sbom.sh && git add sbom-*.json && git commit -m "chore: Update SBOM" && git push
```

## SBOM Storage and Distribution

### Version Control

**Git Configuration (.gitignore exceptions):**
```gitignore
# Include SBOM files in version control
!sbom-*.json
!sbom-*.xml

# Exclude temporary vulnerability reports
vulnerabilities-*.json
```

### Artifact Repository

**Upload to Artifact Repository:**
```bash
# Example: Upload to Nexus
curl -u user:password \
  --upload-file sbom-unified.json \
  https://nexus.example.com/repository/sbom/full-stack-fastapi-template/0.1.0/sbom.json

# Example: Upload to Artifactory
curl -u user:password \
  -T sbom-unified.json \
  "https://artifactory.example.com/artifactory/sbom-repo/full-stack-fastapi-template/0.1.0/sbom.json"
```

### Container Image Integration

**Dockerfile Addition:**
```dockerfile
# Add SBOM to container image
FROM python:3.10-slim

# ... application setup ...

COPY sbom-unified.json /app/sbom.json

LABEL org.opencontainers.image.sbom='{"format":"cyclonedx","version":"1.5","path":"/app/sbom.json"}'
```

## Security-Specific Considerations

### Pinned Dependencies

**Backend - bcrypt pinning:**
- **Component**: bcrypt==4.3.0
- **Reason**: Compatibility with passlib until latest version support
- **Security Impact**: Monitor bcrypt security advisories closely
- **Action**: Review bcrypt updates and test passlib compatibility regularly

**Frontend - Exact versions:**
- **axios**: 1.9.0 (exact version)
- **form-data**: 4.0.2 (exact version)
- **react-hook-form**: 7.49.3 (exact version)
- **Action**: Monitor for security patches and update systematically

### Critical Security Components

**Authentication & Authorization:**
```json
{
  "security-critical-components": [
    {
      "name": "pyjwt",
      "version": ">=2.8.0",
      "purpose": "JWT token generation and validation",
      "risk": "HIGH - Authentication bypass if vulnerable"
    },
    {
      "name": "passlib",
      "version": ">=1.7.4",
      "purpose": "Password hashing",
      "risk": "HIGH - Password compromise if vulnerable"
    },
    {
      "name": "bcrypt",
      "version": "4.3.0",
      "purpose": "Cryptographic hashing",
      "risk": "HIGH - Password security"
    }
  ]
}
```

**Data Protection:**
```json
{
  "data-protection-components": [
    {
      "name": "psycopg",
      "version": ">=3.1.13",
      "purpose": "PostgreSQL database driver",
      "risk": "HIGH - SQL injection if vulnerable"
    },
    {
      "name": "sqlmodel",
      "version": ">=0.0.21",
      "purpose": "SQL ORM",
      "risk": "MEDIUM - Data exposure if misconfigured"
    }
  ]
}
```

**Network Security:**
```json
{
  "network-security-components": [
    {
      "name": "axios",
      "version": "1.9.0",
      "purpose": "HTTP client",
      "risk": "HIGH - SSRF, request smuggling"
    },
    {
      "name": "httpx",
      "version": ">=0.25.1",
      "purpose": "HTTP client",
      "risk": "HIGH - SSRF, request smuggling"
    }
  ]
}
```

### Vulnerability Response Procedures

**Critical Vulnerability Response:**
1. **Detection**: Automated scanning detects CVE
2. **Assessment**: Review SBOM to identify affected components
3. **Impact Analysis**: Check security-critical-components list
4. **Patch Priority**:
   - HIGH risk: Patch within 24 hours
   - MEDIUM risk: Patch within 7 days
   - LOW risk: Include in next scheduled update

**Update Workflow:**
```bash
# 1. Identify vulnerable component
pip-audit --format json | jq '.vulnerabilities[] | select(.id=="CVE-XXXX-XXXXX")'

# 2. Update dependency
# Backend: Update version in pyproject.toml
# Frontend: npm update <package>

# 3. Regenerate SBOM
./scripts/generate-sbom.sh

# 4. Validate changes
cyclonedx-cli validate --input-file sbom-unified.json

# 5. Re-scan for vulnerabilities
pip-audit && npm audit
```

## SBOM Maintenance Schedule

### Regular Activities

**Daily:**
- Automated vulnerability scanning on CI/CD pipeline
- Monitor security advisories for critical components

**Weekly:**
- Generate fresh SBOM from current dependencies
- Review and triage new vulnerability findings
- Update vulnerability annotations in SBOM

**Monthly:**
- Comprehensive license compliance audit
- Review pinned dependencies for security updates
- Update SBOM specification version if needed
- Generate SBOM diff report for change tracking

**Quarterly:**
- Full dependency tree analysis
- Security audit of all production dependencies
- Review and update forbidden license list
- SBOM format validation against latest specification

### Change Management

**When to Update SBOM:**
1. New dependency added to pyproject.toml or package.json
2. Dependency version updated
3. Security patch applied
4. License information changes
5. Application version bump (metadata.component.version)

**SBOM Versioning:**
```json
{
  "version": 1,
  "metadata": {
    "timestamp": "2024-01-01T00:00:00Z",
    "component": {
      "version": "0.1.0"
    }
  }
}
```

Increment SBOM `version` field for each regeneration, maintain `component.version` aligned with application version in pyproject.toml.

## Tools and Dependencies Summary

### Required Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| cyclonedx-bom | Python SBOM generation | `pip install cyclonedx-bom` |
| @cyclonedx/cyclonedx-npm | Node.js SBOM generation | `npm install -g @cyclonedx/cyclonedx-npm` |
| @cyclonedx/cyclonedx-cli | SBOM validation and merging | `npm install -g @cyclonedx/cyclonedx-cli` |
| pip-audit | Python vulnerability scanning | `pip install pip-audit` |
| pip-licenses | Python license detection | `pip install pip-licenses` |
| license-checker | Node.js license detection | `npm install -g license-checker` |

### Optional Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| safety | Python vulnerability database | `pip install safety` |
| snyk | Multi-language security scanning | `npm install -g snyk` |
| grype | Container and filesystem scanning | Download from anchore.io |
| syft | SBOM generation alternative | Download from anchore.io |

## References

- **CycloneDX Specification**: https://cyclonedx.org/specification/overview/
- **Backend Dependencies**: `backend/pyproject.toml`
- **Frontend Dependencies**: `frontend/package.json`
- **Python Version**: >=3.10,<4.0 (from pyproject.toml)
- **Node.js Compatibility**: Implicit from package.json (ESM, modern tooling)
- **Build System**: Hatchling (backend), Vite (frontend)