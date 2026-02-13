# CycloneDX Software Bill of Materials

## Project Information

**Component Name:** full-stack-fastapi-template  
**Component Type:** Application  
**Supplier:** manos-saratsis  
**Version:** 0.1.0 (backend), 0.0.0 (frontend)  
**Description:** Full-stack application with FastAPI backend and React frontend

## SBOM Metadata

**SBOM Format:** CycloneDX  
**Spec Version:** 1.5  
**Serial Number:** urn:uuid:full-stack-fastapi-template-sbom  
**Generation Date:** 2024  
**Document License:** CC0-1.0

---

## Backend Components (Python)

### Runtime Dependencies

#### 1. FastAPI Framework
- **Component:** fastapi
- **Version:** >=0.114.2, <1.0.0
- **Type:** library
- **Package URL:** pkg:pypi/fastapi
- **License:** MIT
- **Purpose:** Web framework and API development
- **Scope:** required
- **Extras:** standard (includes uvicorn, pydantic-settings, and other standard dependencies)

#### 2. Python Multipart
- **Component:** python-multipart
- **Version:** >=0.0.7, <1.0.0
- **Type:** library
- **Package URL:** pkg:pypi/python-multipart
- **License:** Apache-2.0
- **Purpose:** Multipart form data parsing
- **Scope:** required

#### 3. Email Validator
- **Component:** email-validator
- **Version:** >=2.1.0.post1, <3.0.0.0
- **Type:** library
- **Package URL:** pkg:pypi/email-validator
- **License:** CC0-1.0
- **Purpose:** Email address validation
- **Scope:** required

#### 4. Passlib
- **Component:** passlib
- **Version:** >=1.7.4, <2.0.0
- **Type:** library
- **Package URL:** pkg:pypi/passlib
- **License:** BSD-3-Clause
- **Purpose:** Password hashing library
- **Scope:** required
- **Extras:** bcrypt (cryptographic hashing support)

#### 5. Bcrypt
- **Component:** bcrypt
- **Version:** 4.3.0 (pinned)
- **Type:** library
- **Package URL:** pkg:pypi/bcrypt@4.3.0
- **License:** Apache-2.0
- **Purpose:** Cryptographic password hashing
- **Scope:** required
- **Security Note:** Pinned version until passlib supports latest release

#### 6. Tenacity
- **Component:** tenacity
- **Version:** >=8.2.3, <9.0.0
- **Type:** library
- **Package URL:** pkg:pypi/tenacity
- **License:** Apache-2.0
- **Purpose:** Retry logic and resilience patterns
- **Scope:** required

#### 7. Pydantic
- **Component:** pydantic
- **Version:** >2.0
- **Type:** library
- **Package URL:** pkg:pypi/pydantic
- **License:** MIT
- **Purpose:** Data validation and settings management
- **Scope:** required

#### 8. Pydantic Settings
- **Component:** pydantic-settings
- **Version:** >=2.2.1, <3.0.0
- **Type:** library
- **Package URL:** pkg:pypi/pydantic-settings
- **License:** MIT
- **Purpose:** Configuration management
- **Scope:** required

#### 9. Emails
- **Component:** emails
- **Version:** >=0.6, <1.0
- **Type:** library
- **Package URL:** pkg:pypi/emails
- **License:** BSD-2-Clause
- **Purpose:** Email sending functionality
- **Scope:** required

#### 10. Jinja2
- **Component:** jinja2
- **Version:** >=3.1.4, <4.0.0
- **Type:** library
- **Package URL:** pkg:pypi/jinja2
- **License:** BSD-3-Clause
- **Purpose:** Template engine for email templates
- **Scope:** required

#### 11. Alembic
- **Component:** alembic
- **Version:** >=1.12.1, <2.0.0
- **Type:** library
- **Package URL:** pkg:pypi/alembic
- **License:** MIT
- **Purpose:** Database migration management
- **Scope:** required

#### 12. HTTPX
- **Component:** httpx
- **Version:** >=0.25.1, <1.0.0
- **Type:** library
- **Package URL:** pkg:pypi/httpx
- **License:** BSD-3-Clause
- **Purpose:** HTTP client for async requests
- **Scope:** required

#### 13. Psycopg
- **Component:** psycopg
- **Version:** >=3.1.13, <4.0.0
- **Type:** library
- **Package URL:** pkg:pypi/psycopg
- **License:** LGPL-3.0
- **Purpose:** PostgreSQL database adapter
- **Scope:** required
- **Extras:** binary (includes pre-compiled binary package)

#### 14. SQLModel
- **Component:** sqlmodel
- **Version:** >=0.0.21, <1.0.0
- **Type:** library
- **Package URL:** pkg:pypi/sqlmodel
- **License:** MIT
- **Purpose:** SQL database ORM with Pydantic integration
- **Scope:** required

#### 15. Sentry SDK
- **Component:** sentry-sdk
- **Version:** >=1.40.6, <2.0.0
- **Type:** library
- **Package URL:** pkg:pypi/sentry-sdk
- **License:** MIT
- **Purpose:** Error tracking and monitoring
- **Scope:** required
- **Extras:** fastapi (FastAPI integration)

#### 16. PyJWT
- **Component:** pyjwt
- **Version:** >=2.8.0, <3.0.0
- **Type:** library
- **Package URL:** pkg:pypi/pyjwt
- **License:** MIT
- **Purpose:** JSON Web Token implementation for authentication
- **Scope:** required
- **Security Impact:** HIGH - Critical for authentication and authorization

### Development Dependencies

#### 17. Pytest
- **Component:** pytest
- **Version:** >=7.4.3, <8.0.0
- **Type:** library
- **Package URL:** pkg:pypi/pytest
- **License:** MIT
- **Purpose:** Testing framework
- **Scope:** optional (dev)

#### 18. MyPy
- **Component:** mypy
- **Version:** >=1.8.0, <2.0.0
- **Type:** library
- **Package URL:** pkg:pypi/mypy
- **License:** MIT
- **Purpose:** Static type checker
- **Scope:** optional (dev)

#### 19. Ruff
- **Component:** ruff
- **Version:** >=0.2.2, <1.0.0
- **Type:** library
- **Package URL:** pkg:pypi/ruff
- **License:** MIT
- **Purpose:** Python linter and formatter
- **Scope:** optional (dev)

#### 20. Pre-commit
- **Component:** pre-commit
- **Version:** >=3.6.2, <4.0.0
- **Type:** library
- **Package URL:** pkg:pypi/pre-commit
- **License:** MIT
- **Purpose:** Git hooks management
- **Scope:** optional (dev)

#### 21. Types-Passlib
- **Component:** types-passlib
- **Version:** >=1.7.7.20240106, <2.0.0.0
- **Type:** library
- **Package URL:** pkg:pypi/types-passlib
- **License:** Apache-2.0
- **Purpose:** Type stubs for passlib
- **Scope:** optional (dev)

#### 22. Coverage
- **Component:** coverage
- **Version:** >=7.4.3, <8.0.0
- **Type:** library
- **Package URL:** pkg:pypi/coverage
- **License:** Apache-2.0
- **Purpose:** Code coverage measurement
- **Scope:** optional (dev)

---

## Frontend Components (Node.js)

### Runtime Dependencies

#### 23. Chakra UI React
- **Component:** @chakra-ui/react
- **Version:** ^3.8.0
- **Type:** library
- **Package URL:** pkg:npm/%40chakra-ui/react@3.8.0
- **License:** MIT
- **Purpose:** UI component library
- **Scope:** required

#### 24. Emotion React
- **Component:** @emotion/react
- **Version:** ^11.14.0
- **Type:** library
- **Package URL:** pkg:npm/%40emotion/react@11.14.0
- **License:** MIT
- **Purpose:** CSS-in-JS styling library
- **Scope:** required

#### 25. TanStack React Query
- **Component:** @tanstack/react-query
- **Version:** ^5.28.14
- **Type:** library
- **Package URL:** pkg:npm/%40tanstack/react-query@5.28.14
- **License:** MIT
- **Purpose:** Data fetching and caching
- **Scope:** required

#### 26. TanStack React Query DevTools
- **Component:** @tanstack/react-query-devtools
- **Version:** ^5.74.9
- **Type:** library
- **Package URL:** pkg:npm/%40tanstack/react-query-devtools@5.74.9
- **License:** MIT
- **Purpose:** Development tools for React Query
- **Scope:** required

#### 27. TanStack React Router
- **Component:** @tanstack/react-router
- **Version:** 1.19.1 (exact)
- **Type:** library
- **Package URL:** pkg:npm/%40tanstack/react-router@1.19.1
- **License:** MIT
- **Purpose:** Type-safe routing
- **Scope:** required

#### 28. Axios
- **Component:** axios
- **Version:** 1.9.0 (exact)
- **Type:** library
- **Package URL:** pkg:npm/axios@1.9.0
- **License:** MIT
- **Purpose:** HTTP client
- **Scope:** required
- **Security Impact:** MEDIUM - Handles API communication

#### 29. Form Data
- **Component:** form-data
- **Version:** 4.0.2 (exact)
- **Type:** library
- **Package URL:** pkg:npm/form-data@4.0.2
- **License:** MIT
- **Purpose:** Multipart form data handling
- **Scope:** required

#### 30. Next Themes
- **Component:** next-themes
- **Version:** ^0.4.6
- **Type:** library
- **Package URL:** pkg:npm/next-themes@0.4.6
- **License:** MIT
- **Purpose:** Theme management
- **Scope:** required

#### 31. React
- **Component:** react
- **Version:** ^18.2.0
- **Type:** library
- **Package URL:** pkg:npm/react@18.2.0
- **License:** MIT
- **Purpose:** UI framework
- **Scope:** required

#### 32. React DOM
- **Component:** react-dom
- **Version:** ^18.2.0
- **Type:** library
- **Package URL:** pkg:npm/react-dom@18.2.0
- **License:** MIT
- **Purpose:** React renderer for web
- **Scope:** required

#### 33. React Error Boundary
- **Component:** react-error-boundary
- **Version:** ^5.0.0
- **Type:** library
- **Package URL:** pkg:npm/react-error-boundary@5.0.0
- **License:** MIT
- **Purpose:** Error handling component
- **Scope:** required

#### 34. React Hook Form
- **Component:** react-hook-form
- **Version:** 7.49.3 (exact)
- **Type:** library
- **Package URL:** pkg:npm/react-hook-form@7.49.3
- **License:** MIT
- **Purpose:** Form validation and management
- **Scope:** required
- **Security Impact:** MEDIUM - Input validation

#### 35. React Icons
- **Component:** react-icons
- **Version:** ^5.5.0
- **Type:** library
- **Package URL:** pkg:npm/react-icons@5.5.0
- **License:** MIT
- **Purpose:** Icon library
- **Scope:** required

### Development Dependencies

#### 36. Biome
- **Component:** @biomejs/biome
- **Version:** 1.9.4 (exact)
- **Type:** library
- **Package URL:** pkg:npm/%40biomejs/biome@1.9.4
- **License:** MIT
- **Purpose:** Linter and formatter
- **Scope:** optional (dev)

#### 37. Hey API OpenAPI TS
- **Component:** @hey-api/openapi-ts
- **Version:** ^0.57.0
- **Type:** library
- **Package URL:** pkg:npm/%40hey-api/openapi-ts@0.57.0
- **License:** MIT
- **Purpose:** OpenAPI TypeScript client generator
- **Scope:** optional (dev)

#### 38. Playwright
- **Component:** @playwright/test
- **Version:** ^1.52.0
- **Type:** library
- **Package URL:** pkg:npm/%40playwright/test@1.52.0
- **License:** Apache-2.0
- **Purpose:** End-to-end testing
- **Scope:** optional (dev)

#### 39. TanStack Router DevTools
- **Component:** @tanstack/router-devtools
- **Version:** 1.19.1 (exact)
- **Type:** library
- **Package URL:** pkg:npm/%40tanstack/router-devtools@1.19.1
- **License:** MIT
- **Purpose:** Development tools for TanStack Router
- **Scope:** optional (dev)

#### 40. TanStack Router Vite Plugin
- **Component:** @tanstack/router-vite-plugin
- **Version:** 1.19.0 (exact)
- **Type:** library
- **Package URL:** pkg:npm/%40tanstack/router-vite-plugin@1.19.0
- **License:** MIT
- **Purpose:** Vite plugin for TanStack Router
- **Scope:** optional (dev)

#### 41. Types Node
- **Component:** @types/node
- **Version:** ^22.15.3
- **Type:** library
- **Package URL:** pkg:npm/%40types/node@22.15.3
- **License:** MIT
- **Purpose:** TypeScript definitions for Node.js
- **Scope:** optional (dev)

#### 42. Types React
- **Component:** @types/react
- **Version:** ^18.2.37
- **Type:** library
- **Package URL:** pkg:npm/%40types/react@18.2.37
- **License:** MIT
- **Purpose:** TypeScript definitions for React
- **Scope:** optional (dev)

#### 43. Types React DOM
- **Component:** @types/react-dom
- **Version:** ^18.2.15
- **Type:** library
- **Package URL:** pkg:npm/%40types/react-dom@18.2.15
- **License:** MIT
- **Purpose:** TypeScript definitions for React DOM
- **Scope:** optional (dev)

#### 44. Vite Plugin React SWC
- **Component:** @vitejs/plugin-react-swc
- **Version:** ^3.9.0
- **Type:** library
- **Package URL:** pkg:npm/%40vitejs/plugin-react-swc@3.9.0
- **License:** MIT
- **Purpose:** Vite plugin for React with SWC
- **Scope:** optional (dev)

#### 45. Dotenv
- **Component:** dotenv
- **Version:** ^16.4.5
- **Type:** library
- **Package URL:** pkg:npm/dotenv@16.4.5
- **License:** BSD-2-Clause
- **Purpose:** Environment variable management
- **Scope:** optional (dev)

#### 46. TypeScript
- **Component:** typescript
- **Version:** ^5.2.2
- **Type:** library
- **Package URL:** pkg:npm/typescript@5.2.2
- **License:** Apache-2.0
- **Purpose:** TypeScript compiler
- **Scope:** optional (dev)

#### 47. Vite
- **Component:** vite
- **Version:** ^6.3.4
- **Type:** library
- **Package URL:** pkg:npm/vite@6.3.4
- **License:** MIT
- **Purpose:** Build tool and development server
- **Scope:** optional (dev)

---

## Build System Components

### Backend Build System

#### 48. Hatchling
- **Component:** hatchling
- **Type:** build-system
- **Package URL:** pkg:pypi/hatchling
- **License:** MIT
- **Purpose:** Python package build backend
- **Scope:** build
- **Build System Requirement:** Specified in pyproject.toml

---

## Security-Critical Components Summary

### Authentication & Authorization
1. **PyJWT** (>=2.8.0, <3.0.0) - JSON Web Token implementation
2. **Passlib** (>=1.7.4, <2.0.0) - Password hashing
3. **Bcrypt** (4.3.0) - Cryptographic hashing algorithm

### Data Validation & Input Handling
1. **Pydantic** (>2.0) - Backend data validation
2. **Email Validator** (>=2.1.0.post1, <3.0.0.0) - Email validation
3. **React Hook Form** (7.49.3) - Frontend form validation
4. **Python Multipart** (>=0.0.7, <1.0.0) - Multipart data parsing

### Network & Communication
1. **Axios** (1.9.0) - Frontend HTTP client
2. **HTTPX** (>=0.25.1, <1.0.0) - Backend HTTP client
3. **FastAPI** (>=0.114.2, <1.0.0) - Web framework

### Database Security
1. **SQLModel** (>=0.0.21, <1.0.0) - ORM with Pydantic integration
2. **Psycopg** (>=3.1.13, <4.0.0) - PostgreSQL adapter
3. **Alembic** (>=1.12.1, <2.0.0) - Database migrations

---

## Dependency Constraints & Version Pinning

### Pinned Versions (Security-Relevant)
- **bcrypt==4.3.0** - Pinned until passlib compatibility resolved
- **axios@1.9.0** - Exact version for HTTP client
- **react-hook-form@7.49.3** - Exact version for form validation
- **@tanstack/react-router@1.19.1** - Exact version for routing

### Python Version Requirement
- **Requires:** >=3.10, <4.0
- **Target Version:** py310 (configured in ruff)

---

## License Summary

### Backend Licenses
- **MIT:** FastAPI, Pydantic, Pydantic Settings, Alembic, SQLModel, Sentry SDK, PyJWT, Pytest, MyPy, Ruff, Pre-commit, Hatchling
- **Apache-2.0:** Python Multipart, Tenacity, Bcrypt, Types-Passlib, Coverage
- **BSD-3-Clause:** Passlib, Jinja2, HTTPX
- **BSD-2-Clause:** Emails
- **CC0-1.0:** Email Validator
- **LGPL-3.0:** Psycopg

### Frontend Licenses
- **MIT:** Chakra UI, Emotion, TanStack (Query, Router), Axios, Next Themes, React, React DOM, React Error Boundary, React Hook Form, React Icons, Biome, Hey API, TanStack DevTools, Types packages, Vite Plugin, Vite, Hatchling
- **Apache-2.0:** Playwright, TypeScript
- **BSD-2-Clause:** Dotenv

---

## Supply Chain Security Considerations

### High-Risk Components (Require Regular Monitoring)
1. **PyJWT** - Authentication token handling
2. **Bcrypt/Passlib** - Password hashing
3. **Axios** - HTTP client with potential for injection attacks
4. **FastAPI** - Web framework exposure
5. **Psycopg** - Database connection security

### Recommended Actions
1. **Vulnerability Scanning:** Regular CVE monitoring for all components
2. **Update Policy:** Security patches should be applied within 7 days
3. **License Compliance:** Review LGPL-3.0 (Psycopg) for distribution requirements
4. **Dependency Auditing:** Run `pip audit` and `npm audit` regularly
5. **SBOM Updates:** Regenerate SBOM with each dependency version change

### Known Version Constraints
- Bcrypt pinned to 4.3.0 - Monitor passlib releases for compatibility updates
- Python 3.10+ required - Ensure container images meet minimum version
- Node.js version not specified - Should be documented in deployment requirements

---

## CycloneDX JSON Schema Reference

This SBOM follows CycloneDX specification version 1.5. For machine-readable format, convert to JSON or XML using CycloneDX tools with the following structure:

```
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.5",
  "serialNumber": "urn:uuid:full-stack-fastapi-template-sbom",
  "version": 1,
  "metadata": {
    "component": {
      "type": "application",
      "name": "full-stack-fastapi-template",
      "version": "0.1.0"
    }
  },
  "components": [
    // 48 components documented above
  ]
}
```

---

## Maintenance Schedule

- **SBOM Review Frequency:** Monthly or with every dependency update
- **Vulnerability Assessment:** Weekly automated scans
- **License Compliance Review:** Quarterly
- **Dependency Updates:** Follow semantic versioning constraints specified in pyproject.toml and package.json