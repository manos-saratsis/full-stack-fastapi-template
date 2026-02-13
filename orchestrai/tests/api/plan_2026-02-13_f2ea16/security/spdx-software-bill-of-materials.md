# SPDX Software Bill of Materials

## Document Information

**SPDX Version:** SPDX-2.3  
**Data License:** CC0-1.0  
**SPDX Identifier:** SPDXRef-DOCUMENT  
**Document Name:** full-stack-fastapi-template-sbom  
**Document Namespace:** https://github.com/manos-saratsis/full-stack-fastapi-template/sbom-2024  
**Creator:** Tool: SBOM Generator  
**Created:** 2024-01-01T00:00:00Z

## Package Information

### Root Package

**Package Name:** full-stack-fastapi-template  
**SPDX Identifier:** SPDXRef-Package-Root  
**Package Version:** 0.1.0  
**Package Supplier:** Organization: manos-saratsis  
**Package Download Location:** https://github.com/manos-saratsis/full-stack-fastapi-template  
**Files Analyzed:** true  
**Package Verification Code:** (excluded from runtime generation)  
**Concluded License:** MIT  
**Declared License:** MIT  
**License File:** LICENSE  
**Copyright Text:** Copyright (c) 2019 Sebastián Ramírez  
**Package Summary:** Full-stack FastAPI template with React frontend and PostgreSQL backend

---

## Backend Dependencies (Python)

### 1. FastAPI

**Package Name:** fastapi  
**SPDX Identifier:** SPDXRef-Package-fastapi  
**Package Version:** >=0.114.2,<1.0.0  
**Package Supplier:** Organization: tiangolo  
**Package Download Location:** https://pypi.org/project/fastapi  
**Concluded License:** MIT  
**Package Purpose:** APPLICATION  
**Package Summary:** Modern web framework for building APIs with Python  
**Source File:** backend/pyproject.toml  
**Comment:** Includes standard dependencies

### 2. Python Multipart

**Package Name:** python-multipart  
**SPDX Identifier:** SPDXRef-Package-python-multipart  
**Package Version:** >=0.0.7,<1.0.0  
**Package Supplier:** NOASSERTION  
**Package Download Location:** https://pypi.org/project/python-multipart  
**Concluded License:** Apache-2.0  
**Package Purpose:** LIBRARY  
**Package Summary:** Parser for multipart/form-data  
**Source File:** backend/pyproject.toml

### 3. Email Validator

**Package Name:** email-validator  
**SPDX Identifier:** SPDXRef-Package-email-validator  
**Package Version:** >=2.1.0.post1,<3.0.0.0  
**Package Supplier:** NOASSERTION  
**Package Download Location:** https://pypi.org/project/email-validator  
**Concluded License:** CC0-1.0  
**Package Purpose:** LIBRARY  
**Package Summary:** Email address validation library  
**Source File:** backend/pyproject.toml

### 4. Passlib

**Package Name:** passlib  
**SPDX Identifier:** SPDXRef-Package-passlib  
**Package Version:** >=1.7.4,<2.0.0  
**Package Supplier:** NOASSERTION  
**Package Download Location:** https://pypi.org/project/passlib  
**Concluded License:** BSD-3-Clause  
**Package Purpose:** LIBRARY  
**Package Summary:** Password hashing library with bcrypt support  
**Source File:** backend/pyproject.toml  
**Comment:** Includes bcrypt extra for password hashing

### 5. Bcrypt

**Package Name:** bcrypt  
**SPDX Identifier:** SPDXRef-Package-bcrypt  
**Package Version:** 4.3.0  
**Package Supplier:** Organization: pyca  
**Package Download Location:** https://pypi.org/project/bcrypt  
**Concluded License:** Apache-2.0  
**Package Purpose:** LIBRARY  
**Package Summary:** Modern password hashing for software and servers  
**Source File:** backend/pyproject.toml  
**Comment:** Pinned version until passlib supports latest

### 6. Tenacity

**Package Name:** tenacity  
**SPDX Identifier:** SPDXRef-Package-tenacity  
**Package Version:** >=8.2.3,<9.0.0  
**Package Supplier:** NOASSERTION  
**Package Download Location:** https://pypi.org/project/tenacity  
**Concluded License:** Apache-2.0  
**Package Purpose:** LIBRARY  
**Package Summary:** Retry library for Python  
**Source File:** backend/pyproject.toml

### 7. Pydantic

**Package Name:** pydantic  
**SPDX Identifier:** SPDXRef-Package-pydantic  
**Package Version:** >2.0  
**Package Supplier:** Organization: pydantic  
**Package Download Location:** https://pypi.org/project/pydantic  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Data validation using Python type annotations  
**Source File:** backend/pyproject.toml

### 8. Pydantic Settings

**Package Name:** pydantic-settings  
**SPDX Identifier:** SPDXRef-Package-pydantic-settings  
**Package Version:** >=2.2.1,<3.0.0  
**Package Supplier:** Organization: pydantic  
**Package Download Location:** https://pypi.org/project/pydantic-settings  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Settings management using Pydantic  
**Source File:** backend/pyproject.toml

### 9. Emails

**Package Name:** emails  
**SPDX Identifier:** SPDXRef-Package-emails  
**Package Version:** >=0.6,<1.0  
**Package Supplier:** NOASSERTION  
**Package Download Location:** https://pypi.org/project/emails  
**Concluded License:** BSD-3-Clause  
**Package Purpose:** LIBRARY  
**Package Summary:** Email sending library  
**Source File:** backend/pyproject.toml

### 10. Jinja2

**Package Name:** jinja2  
**SPDX Identifier:** SPDXRef-Package-jinja2  
**Package Version:** >=3.1.4,<4.0.0  
**Package Supplier:** Organization: pallets  
**Package Download Location:** https://pypi.org/project/jinja2  
**Concluded License:** BSD-3-Clause  
**Package Purpose:** LIBRARY  
**Package Summary:** Template engine for Python  
**Source File:** backend/pyproject.toml

### 11. Alembic

**Package Name:** alembic  
**SPDX Identifier:** SPDXRef-Package-alembic  
**Package Version:** >=1.12.1,<2.0.0  
**Package Supplier:** Organization: sqlalchemy  
**Package Download Location:** https://pypi.org/project/alembic  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Database migration tool for SQLAlchemy  
**Source File:** backend/pyproject.toml

### 12. HTTPX

**Package Name:** httpx  
**SPDX Identifier:** SPDXRef-Package-httpx  
**Package Version:** >=0.25.1,<1.0.0  
**Package Supplier:** Organization: encode  
**Package Download Location:** https://pypi.org/project/httpx  
**Concluded License:** BSD-3-Clause  
**Package Purpose:** LIBRARY  
**Package Summary:** HTTP client for Python  
**Source File:** backend/pyproject.toml

### 13. Psycopg

**Package Name:** psycopg  
**SPDX Identifier:** SPDXRef-Package-psycopg  
**Package Version:** >=3.1.13,<4.0.0  
**Package Supplier:** Organization: psycopg  
**Package Download Location:** https://pypi.org/project/psycopg  
**Concluded License:** LGPL-3.0-only  
**Package Purpose:** LIBRARY  
**Package Summary:** PostgreSQL database adapter for Python  
**Source File:** backend/pyproject.toml  
**Comment:** Includes binary extra for compiled C extension

### 14. SQLModel

**Package Name:** sqlmodel  
**SPDX Identifier:** SPDXRef-Package-sqlmodel  
**Package Version:** >=0.0.21,<1.0.0  
**Package Supplier:** Organization: tiangolo  
**Package Download Location:** https://pypi.org/project/sqlmodel  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** SQL databases in Python with type annotations  
**Source File:** backend/pyproject.toml

### 15. Sentry SDK

**Package Name:** sentry-sdk  
**SPDX Identifier:** SPDXRef-Package-sentry-sdk  
**Package Version:** >=1.40.6,<2.0.0  
**Package Supplier:** Organization: getsentry  
**Package Download Location:** https://pypi.org/project/sentry-sdk  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Error tracking and performance monitoring  
**Source File:** backend/pyproject.toml  
**Comment:** Includes fastapi integration

### 16. PyJWT

**Package Name:** pyjwt  
**SPDX Identifier:** SPDXRef-Package-pyjwt  
**Package Version:** >=2.8.0,<3.0.0  
**Package Supplier:** Organization: jpadilla  
**Package Download Location:** https://pypi.org/project/pyjwt  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** JSON Web Token implementation in Python  
**Source File:** backend/pyproject.toml

---

## Backend Development Dependencies

### 17. Pytest

**Package Name:** pytest  
**SPDX Identifier:** SPDXRef-Package-pytest  
**Package Version:** >=7.4.3,<8.0.0  
**Package Supplier:** Organization: pytest-dev  
**Package Download Location:** https://pypi.org/project/pytest  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Testing framework for Python  
**Source File:** backend/pyproject.toml  
**Comment:** Development dependency only

### 18. MyPy

**Package Name:** mypy  
**SPDX Identifier:** SPDXRef-Package-mypy  
**Package Version:** >=1.8.0,<2.0.0  
**Package Supplier:** Organization: python  
**Package Download Location:** https://pypi.org/project/mypy  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Static type checker for Python  
**Source File:** backend/pyproject.toml  
**Comment:** Development dependency only, strict mode enabled

### 19. Ruff

**Package Name:** ruff  
**SPDX Identifier:** SPDXRef-Package-ruff  
**Package Version:** >=0.2.2,<1.0.0  
**Package Supplier:** Organization: astral-sh  
**Package Download Location:** https://pypi.org/project/ruff  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Fast Python linter  
**Source File:** backend/pyproject.toml  
**Comment:** Development dependency only

### 20. Pre-commit

**Package Name:** pre-commit  
**SPDX Identifier:** SPDXRef-Package-pre-commit  
**Package Version:** >=3.6.2,<4.0.0  
**Package Supplier:** Organization: pre-commit  
**Package Download Location:** https://pypi.org/project/pre-commit  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Framework for managing git pre-commit hooks  
**Source File:** backend/pyproject.toml  
**Comment:** Development dependency only

### 21. Types Passlib

**Package Name:** types-passlib  
**SPDX Identifier:** SPDXRef-Package-types-passlib  
**Package Version:** >=1.7.7.20240106,<2.0.0.0  
**Package Supplier:** Organization: python  
**Package Download Location:** https://pypi.org/project/types-passlib  
**Concluded License:** Apache-2.0  
**Package Purpose:** LIBRARY  
**Package Summary:** Type stubs for passlib  
**Source File:** backend/pyproject.toml  
**Comment:** Development dependency only

### 22. Coverage

**Package Name:** coverage  
**SPDX Identifier:** SPDXRef-Package-coverage  
**Package Version:** >=7.4.3,<8.0.0  
**Package Supplier:** Organization: nedbat  
**Package Download Location:** https://pypi.org/project/coverage  
**Concluded License:** Apache-2.0  
**Package Purpose:** LIBRARY  
**Package Summary:** Code coverage measurement for Python  
**Source File:** backend/pyproject.toml  
**Comment:** Development dependency only

---

## Frontend Dependencies (JavaScript/TypeScript)

### 23. React

**Package Name:** react  
**SPDX Identifier:** SPDXRef-Package-react  
**Package Version:** ^18.2.0  
**Package Supplier:** Organization: facebook  
**Package Download Location:** https://www.npmjs.com/package/react  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** JavaScript library for building user interfaces  
**Source File:** frontend/package.json

### 24. React DOM

**Package Name:** react-dom  
**SPDX Identifier:** SPDXRef-Package-react-dom  
**Package Version:** ^18.2.0  
**Package Supplier:** Organization: facebook  
**Package Download Location:** https://www.npmjs.com/package/react-dom  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** React rendering for web browsers  
**Source File:** frontend/package.json

### 25. Chakra UI React

**Package Name:** @chakra-ui/react  
**SPDX Identifier:** SPDXRef-Package-chakra-ui-react  
**Package Version:** ^3.8.0  
**Package Supplier:** Organization: chakra-ui  
**Package Download Location:** https://www.npmjs.com/package/@chakra-ui/react  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Component library for React applications  
**Source File:** frontend/package.json

### 26. Emotion React

**Package Name:** @emotion/react  
**SPDX Identifier:** SPDXRef-Package-emotion-react  
**Package Version:** ^11.14.0  
**Package Supplier:** Organization: emotion-js  
**Package Download Location:** https://www.npmjs.com/package/@emotion/react  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** CSS-in-JS library for React  
**Source File:** frontend/package.json

### 27. TanStack React Query

**Package Name:** @tanstack/react-query  
**SPDX Identifier:** SPDXRef-Package-tanstack-react-query  
**Package Version:** ^5.28.14  
**Package Supplier:** Organization: tanstack  
**Package Download Location:** https://www.npmjs.com/package/@tanstack/react-query  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Data synchronization library for React  
**Source File:** frontend/package.json

### 28. TanStack React Query DevTools

**Package Name:** @tanstack/react-query-devtools  
**SPDX Identifier:** SPDXRef-Package-tanstack-react-query-devtools  
**Package Version:** ^5.74.9  
**Package Supplier:** Organization: tanstack  
**Package Download Location:** https://www.npmjs.com/package/@tanstack/react-query-devtools  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Development tools for React Query  
**Source File:** frontend/package.json

### 29. TanStack React Router

**Package Name:** @tanstack/react-router  
**SPDX Identifier:** SPDXRef-Package-tanstack-react-router  
**Package Version:** 1.19.1  
**Package Supplier:** Organization: tanstack  
**Package Download Location:** https://www.npmjs.com/package/@tanstack/react-router  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Type-safe routing for React applications  
**Source File:** frontend/package.json

### 30. Axios

**Package Name:** axios  
**SPDX Identifier:** SPDXRef-Package-axios  
**Package Version:** 1.9.0  
**Package Supplier:** Organization: axios  
**Package Download Location:** https://www.npmjs.com/package/axios  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Promise-based HTTP client for browsers and Node.js  
**Source File:** frontend/package.json

### 31. Form Data

**Package Name:** form-data  
**SPDX Identifier:** SPDXRef-Package-form-data  
**Package Version:** 4.0.2  
**Package Supplier:** NOASSERTION  
**Package Download Location:** https://www.npmjs.com/package/form-data  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Library to create multipart/form-data streams  
**Source File:** frontend/package.json

### 32. Next Themes

**Package Name:** next-themes  
**SPDX Identifier:** SPDXRef-Package-next-themes  
**Package Version:** ^0.4.6  
**Package Supplier:** NOASSERTION  
**Package Download Location:** https://www.npmjs.com/package/next-themes  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Theme management for React applications  
**Source File:** frontend/package.json

### 33. React Error Boundary

**Package Name:** react-error-boundary  
**SPDX Identifier:** SPDXRef-Package-react-error-boundary  
**Package Version:** ^5.0.0  
**Package Supplier:** NOASSERTION  
**Package Download Location:** https://www.npmjs.com/package/react-error-boundary  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Error handling wrapper for React components  
**Source File:** frontend/package.json

### 34. React Hook Form

**Package Name:** react-hook-form  
**SPDX Identifier:** SPDXRef-Package-react-hook-form  
**Package Version:** 7.49.3  
**Package Supplier:** Organization: react-hook-form  
**Package Download Location:** https://www.npmjs.com/package/react-hook-form  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Form validation library for React  
**Source File:** frontend/package.json

### 35. React Icons

**Package Name:** react-icons  
**SPDX Identifier:** SPDXRef-Package-react-icons  
**Package Version:** ^5.5.0  
**Package Supplier:** NOASSERTION  
**Package Download Location:** https://www.npmjs.com/package/react-icons  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Icon library for React applications  
**Source File:** frontend/package.json

---

## Frontend Development Dependencies

### 36. Biome

**Package Name:** @biomejs/biome  
**SPDX Identifier:** SPDXRef-Package-biomejs-biome  
**Package Version:** 1.9.4  
**Package Supplier:** Organization: biomejs  
**Package Download Location:** https://www.npmjs.com/package/@biomejs/biome  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Fast formatter and linter for JavaScript/TypeScript  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 37. Hey API OpenAPI TypeScript

**Package Name:** @hey-api/openapi-ts  
**SPDX Identifier:** SPDXRef-Package-hey-api-openapi-ts  
**Package Version:** ^0.57.0  
**Package Supplier:** Organization: hey-api  
**Package Download Location:** https://www.npmjs.com/package/@hey-api/openapi-ts  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** OpenAPI client generator for TypeScript  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 38. Playwright

**Package Name:** @playwright/test  
**SPDX Identifier:** SPDXRef-Package-playwright-test  
**Package Version:** ^1.52.0  
**Package Supplier:** Organization: microsoft  
**Package Download Location:** https://www.npmjs.com/package/@playwright/test  
**Concluded License:** Apache-2.0  
**Package Purpose:** LIBRARY  
**Package Summary:** End-to-end testing framework  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 39. TanStack Router DevTools

**Package Name:** @tanstack/router-devtools  
**SPDX Identifier:** SPDXRef-Package-tanstack-router-devtools  
**Package Version:** 1.19.1  
**Package Supplier:** Organization: tanstack  
**Package Download Location:** https://www.npmjs.com/package/@tanstack/router-devtools  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Development tools for TanStack Router  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 40. TanStack Router Vite Plugin

**Package Name:** @tanstack/router-vite-plugin  
**SPDX Identifier:** SPDXRef-Package-tanstack-router-vite-plugin  
**Package Version:** 1.19.0  
**Package Supplier:** Organization: tanstack  
**Package Download Location:** https://www.npmjs.com/package/@tanstack/router-vite-plugin  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Vite plugin for TanStack Router  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 41. Types Node

**Package Name:** @types/node  
**SPDX Identifier:** SPDXRef-Package-types-node  
**Package Version:** ^22.15.3  
**Package Supplier:** Organization: DefinitelyTyped  
**Package Download Location:** https://www.npmjs.com/package/@types/node  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** TypeScript definitions for Node.js  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 42. Types React

**Package Name:** @types/react  
**SPDX Identifier:** SPDXRef-Package-types-react  
**Package Version:** ^18.2.37  
**Package Supplier:** Organization: DefinitelyTyped  
**Package Download Location:** https://www.npmjs.com/package/@types/react  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** TypeScript definitions for React  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 43. Types React DOM

**Package Name:** @types/react-dom  
**SPDX Identifier:** SPDXRef-Package-types-react-dom  
**Package Version:** ^18.2.15  
**Package Supplier:** Organization: DefinitelyTyped  
**Package Download Location:** https://www.npmjs.com/package/@types/react-dom  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** TypeScript definitions for React DOM  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 44. Vite Plugin React SWC

**Package Name:** @vitejs/plugin-react-swc  
**SPDX Identifier:** SPDXRef-Package-vitejs-plugin-react-swc  
**Package Version:** ^3.9.0  
**Package Supplier:** Organization: vitejs  
**Package Download Location:** https://www.npmjs.com/package/@vitejs/plugin-react-swc  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Vite plugin for React with SWC compiler  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 45. Dotenv

**Package Name:** dotenv  
**SPDX Identifier:** SPDXRef-Package-dotenv  
**Package Version:** ^16.4.5  
**Package Supplier:** NOASSERTION  
**Package Download Location:** https://www.npmjs.com/package/dotenv  
**Concluded License:** BSD-2-Clause  
**Package Purpose:** LIBRARY  
**Package Summary:** Environment variable management  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 46. TypeScript

**Package Name:** typescript  
**SPDX Identifier:** SPDXRef-Package-typescript  
**Package Version:** ^5.2.2  
**Package Supplier:** Organization: microsoft  
**Package Download Location:** https://www.npmjs.com/package/typescript  
**Concluded License:** Apache-2.0  
**Package Purpose:** LIBRARY  
**Package Summary:** TypeScript language compiler  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

### 47. Vite

**Package Name:** vite  
**SPDX Identifier:** SPDXRef-Package-vite  
**Package Version:** ^6.3.4  
**Package Supplier:** Organization: vitejs  
**Package Download Location:** https://www.npmjs.com/package/vite  
**Concluded License:** MIT  
**Package Purpose:** LIBRARY  
**Package Summary:** Frontend build tool and development server  
**Source File:** frontend/package.json  
**Comment:** Development dependency only

---

## Relationships

**Relationship:** SPDXRef-DOCUMENT DESCRIBES SPDXRef-Package-Root  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-fastapi  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-python-multipart  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-email-validator  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-passlib  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-bcrypt  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-tenacity  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-pydantic  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-pydantic-settings  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-emails  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-jinja2  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-alembic  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-httpx  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-psycopg  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-sqlmodel  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-sentry-sdk  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-pyjwt  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-react  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-react-dom  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-chakra-ui-react  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-emotion-react  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-tanstack-react-query  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-tanstack-react-router  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-axios  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-form-data  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-next-themes  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-react-error-boundary  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-react-hook-form  
**Relationship:** SPDXRef-Package-Root CONTAINS SPDXRef-Package-react-icons  
**Relationship:** SPDXRef-Package-passlib DEPENDS_ON SPDXRef-Package-bcrypt  
**Relationship:** SPDXRef-Package-fastapi DEPENDS_ON SPDXRef-Package-pydantic  
**Relationship:** SPDXRef-Package-chakra-ui-react DEPENDS_ON SPDXRef-Package-emotion-react  
**Relationship:** SPDXRef-Package-chakra-ui-react DEPENDS_ON SPDXRef-Package-react  
**Relationship:** SPDXRef-Package-react-dom DEPENDS_ON SPDXRef-Package-react  

---

## Security-Relevant Package Notes

### Authentication & Authorization Components

- **PyJWT (SPDXRef-Package-pyjwt)**: Core component for JWT token generation and validation used in authentication flows
- **Passlib (SPDXRef-Package-passlib)**: Password hashing library with bcrypt support for secure credential storage
- **Bcrypt (SPDXRef-Package-bcrypt)**: Cryptographic hashing algorithm pinned to version 4.3.0 for compatibility

### Data Protection Components

- **Psycopg (SPDXRef-Package-psycopg)**: PostgreSQL adapter with binary extensions for database connectivity and parameterized queries
- **SQLModel (SPDXRef-Package-sqlmodel)**: Type-safe ORM layer preventing SQL injection through parameterized queries
- **Pydantic (SPDXRef-Package-pydantic)**: Input validation framework preventing injection attacks and data corruption

### Network Security Components

- **HTTPX (SPDXRef-Package-httpx)**: HTTP client with TLS/SSL support for secure API communication
- **Axios (SPDXRef-Package-axios)**: Frontend HTTP client for secure API requests with CSRF protection support

### Monitoring & Error Tracking

- **Sentry SDK (SPDXRef-Package-sentry-sdk)**: Error tracking and performance monitoring with FastAPI integration for security event logging

### Security-Critical Version Pins

- **Bcrypt 4.3.0**: Explicitly pinned to ensure compatibility with passlib and maintain consistent password hashing behavior
- **Python >=3.10,<4.0**: Minimum version requirement ensures availability of security features and patches

---

## License Summary

### Production Dependencies by License

**MIT License:**
- fastapi, pydantic, pydantic-settings, alembic, sqlmodel, sentry-sdk, pyjwt
- react, react-dom, @chakra-ui/react, @emotion/react, @tanstack/react-query, @tanstack/react-router, axios, form-data, next-themes, react-error-boundary, react-hook-form, react-icons

**Apache-2.0 License:**
- python-multipart, bcrypt, tenacity

**BSD-3-Clause License:**
- passlib, emails,