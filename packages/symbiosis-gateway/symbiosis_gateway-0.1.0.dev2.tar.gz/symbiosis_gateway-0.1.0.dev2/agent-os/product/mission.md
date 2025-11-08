# Product Mission

## Pitch
Symbiosis Gateway is an open-source AI gateway that helps organizations manage their LLM and AI model integrations by providing centralized access control, monitoring, cost management, and security guardrails for safer and more efficient AI-powered applications.

## Users

### Primary Customers
- **Internal Teams at Info Support**: Development teams building LLM-based applications who need reliable, governed access to AI models
- **Enterprise Organizations**: Companies seeking professional, self-hosted solutions for managing AI model access across their IT landscape
- **System Administrators**: IT operations teams responsible for managing access, costs, and compliance for AI services

### User Personas

**LLM Application Developer** (25-45 years)
- **Role:** Software developer building AI-powered applications in Java, C#, Python, or TypeScript
- **Context:** Works on a laptop with access to Info Support systems, prefers to focus on experimentation and development rather than infrastructure configuration
- **Pain Points:** Fragmented access to models, lack of monitoring tools, security concerns, difficulty debugging LLM interactions, time spent on configuration instead of development
- **Goals:** Quick and easy connection to approved LLMs, reliable monitoring for debugging, simple authentication, freedom to experiment without security worries

**System Administrator** (30-50 years)
- **Role:** IT services professional managing access and day-1 support for internal platforms
- **Context:** Busy IT department handling numerous access requests and support tickets
- **Pain Points:** Manual onboarding workflows, time-consuming credit allocation, lack of automation for routine tasks
- **Goals:** Automate user onboarding, enable self-service access requests, reduce manual intervention for routine credit requests, integrate with existing workflows

**Business Unit Manager** (35-55 years)
- **Role:** Manager responsible for approving costs and tracking spending for their business unit
- **Context:** Oversees multiple initiatives and projects, needs visibility into AI-related expenses
- **Pain Points:** Lack of cost visibility, inability to track spending per project, no budget controls, surprise bills
- **Goals:** Clear visibility into LLM spending per project, budget controls and alerts, consolidated reporting for their business unit

## The Problem

### Fragmented and Ungoverned LLM Access
Organizations adopting LLM-based applications face critical challenges with fragmented access, leading to cost overruns, security vulnerabilities, compliance issues, and increased development time. Without centralized governance, companies experience unexpected spending (long chat sessions without limits), security incidents (acceptable use policy violations without debugging capabilities), compliance risks (using unverified model providers), and slower development cycles (lack of proper monitoring tools).

**Our Solution:** Symbiosis Gateway provides a centralized, self-hosted platform that consolidates access to governance-approved LLMs with built-in monitoring, cost management, security guardrails, and compliance controls. By standardizing the approach across all applications, we reduce operational costs, improve security, and accelerate development.

## Differentiators

### True Open-Source and Self-Hosted
Unlike 99% of existing AI gateway products that are fronts for cloud-based solutions with vendor lock-in, we provide a genuinely open-source, self-hosted solution. This gives organizations true independence from cloud vendors, allows customization based on specific needs, and aligns with sovereignty requirements for sensitive data and operations.

### Built for Enterprise Governance
While other tools focus on developer experience alone, Symbiosis Gateway balances developer productivity with enterprise governance needs. We provide self-service workflows that reduce IT burden while maintaining necessary controls for cost management, security, and compliance. This results in faster onboarding, lower operational overhead, and peace of mind for IT leadership.

### OpenAI-Compatible API with Management Layer
We expose an OpenAI-compatible API so developers can use existing OpenAI libraries without code changes, while adding a management layer for virtual API keys, project tracking, and budget controls. This approach eliminates the learning curve for developers while providing centralized visibility and control for administrators.

## Key Features

### Core Features
- **Multi-Provider LLM Support:** Connect to OpenAI (via Azure and direct), Anthropic Claude, and self-hosted open-source models through a single interface
- **Virtual API Keys:** Abstract access to models with project-specific virtual keys that enable tracking and budget management
- **Centralized Monitoring:** Log all requests/responses and record metrics (tokens, latency, requests per minute) with OpenTelemetry export
- **Cost Management:** Track spending per project, set budgets, receive alerts when thresholds are reached

### Collaboration Features
- **Self-Service Onboarding:** Automated access request and approval workflows minimize manual IT intervention
- **OAuth/OpenID Integration:** Seamless authentication with existing organizational identity systems
- **Credit Management:** Self-service credit requests with automated allocation workflows

### Advanced Features
- **Security Guardrails:** Standardized approach to securing LLM applications with shared experience across projects
- **Observability Integration:** Export telemetry data via OpenTelemetry for integration with existing monitoring stacks
- **API-First Management:** Full API access for system administrators to integrate with their own workflows and tooling
- **Business Unit Reporting:** Cost visibility and reporting aggregated by business unit for management oversight
