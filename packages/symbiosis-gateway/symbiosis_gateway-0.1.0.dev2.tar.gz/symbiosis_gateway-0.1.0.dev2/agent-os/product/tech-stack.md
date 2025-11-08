# Tech Stack

This document outlines all technology choices for the Symbiosis Gateway project and the rationale behind each selection.

## Framework & Runtime

### Python 3.13
**Purpose:** Main programming language for the AI gateway
**Rationale:** Python is the dominant language in the AI/ML ecosystem with excellent library support for LLM integrations. Version 3.13 provides the latest performance improvements and language features. Strong expertise within the Info Support team in Python for backend services.

### UV
**Purpose:** Package manager, dependency management, virtual environment management, and build tool
**Rationale:** Modern, fast alternative to pip/poetry that handles the entire Python toolchain lifecycle. Simplifies developer setup and CI/CD pipelines by consolidating multiple tools. Significantly faster than traditional Python package managers.

## API & Web Framework

### FastAPI
**Purpose:** REST API framework for the gateway's HTTP endpoints
**Rationale:** Modern, high-performance async framework with automatic OpenAPI documentation generation. Type hints provide excellent developer experience and catch errors early. Built-in request validation and serialization. Industry standard for building Python APIs.

### Typer
**Purpose:** CLI interface for administrative commands
**Rationale:** Built by the same author as FastAPI with similar design philosophy. Provides type-safe CLI argument parsing with excellent help text generation. Enables system administrators to manage the platform via command-line tools.

## Database & ORM

### PostgreSQL
**Purpose:** Primary database for storing configuration, users, projects, API keys, request logs, and metrics
**Rationale:** Robust, enterprise-grade relational database with excellent JSON support for flexible schema evolution. Strong ACID guarantees for financial tracking (cost management). Wide deployment options across cloud providers. Well-supported in Azure (the deployment target).

### SQLModel
**Purpose:** ORM for database interactions
**Rationale:** Combines SQLAlchemy (mature ORM) with Pydantic (validation library used by FastAPI). Provides type-safe database models that integrate seamlessly with FastAPI. Single model definition works for both database schema and API validation.

## Testing & Quality

### Pytest
**Purpose:** Unit testing framework
**Rationale:** Industry-standard testing framework for Python with rich plugin ecosystem. Fixtures provide clean test setup/teardown. Parameterized tests reduce code duplication. Excellent async support for testing FastAPI endpoints.

### Ruff
**Purpose:** Linting and code formatting
**Rationale:** Extremely fast linter and formatter written in Rust that replaces multiple tools (Flake8, Black, isort, etc.). Enforces consistent code style across the codebase. Catches common bugs and anti-patterns. Integrates well with CI/CD pipelines.

## Deployment & Infrastructure

### Azure
**Purpose:** Cloud hosting platform
**Rationale:** Primary cloud provider at Info Support with existing organizational infrastructure and expertise. Provides managed PostgreSQL, container hosting, and identity integration options. Aligns with internal strategic direction.

### GitHub Actions
**Purpose:** CI/CD pipeline automation
**Rationale:** Native integration with GitHub (where the code is hosted). Free for open-source projects. Mature ecosystem of actions for Python, Docker, and Azure deployments. Supports automated testing, linting, and release workflows.

## Observability & Monitoring

### OpenTelemetry
**Purpose:** Telemetry data export for observability
**Rationale:** Vendor-neutral standard for metrics, logs, and traces. Allows integration with any observability platform (Datadog, New Relic, Grafana, etc.). Future-proof approach that doesn't lock into specific monitoring vendors. Essential for enterprise adoption.

## Authentication & Security

### OAuth/OpenID Connect
**Purpose:** User authentication and authorization
**Rationale:** Industry-standard protocols for delegated authentication. Integrates with existing organizational identity providers (Azure AD, Okta, etc.). Avoids building custom authentication system. Supports single sign-on workflows.

## API Integration

### OpenAI SDK Compatibility
**Purpose:** Client-facing API design
**Rationale:** OpenAI's API format has become the de facto standard for LLM interactions. By maintaining compatibility, developers can use existing OpenAI libraries (official SDKs, LangChain, etc.) without code changes. Dramatically reduces adoption friction and learning curve.

## Architecture Patterns

### Proxy Pattern
**Purpose:** Gateway architecture for model provider abstraction
**Rationale:** Virtual API keys abstract the underlying provider, allowing centralized control and monitoring without changing client code. Enables provider switching, cost tracking, and security policies at the gateway level.

### Plugin Architecture
**Purpose:** Model provider integrations
**Rationale:** Each provider (OpenAI, Anthropic, self-hosted) is implemented as a separate module with a common interface. Allows adding new providers without modifying core gateway logic. Simplifies testing and maintenance.

## Development Tools

### Git
**Purpose:** Version control
**Rationale:** Industry standard for source code management. GitHub provides excellent collaboration features, issue tracking, and CI/CD integration.

### Conventional Commits
**Purpose:** Commit message format
**Rationale:** Standardized commit format enables automated changelog generation and semantic versioning. Makes git history more readable and useful for understanding changes.

## Documentation

### Arc42
**Purpose:** Architecture documentation standard
**Rationale:** Well-established template for documenting software architecture. Provides comprehensive structure covering all architectural aspects. Familiar to many developers and architects in the industry.

### Markdown
**Purpose:** Documentation format
**Rationale:** Simple, readable format that works well in version control. Renders nicely on GitHub and in most documentation tools. Low barrier to contribution.
