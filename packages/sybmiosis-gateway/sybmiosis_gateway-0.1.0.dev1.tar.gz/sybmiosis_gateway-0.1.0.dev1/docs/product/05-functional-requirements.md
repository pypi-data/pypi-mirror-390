# Functional requirements

This section covers functional requirements. Functional requirements are grouped
per [customer persona](./04-customer-personas.md).

## For developers

### LLM model support

- The gateway must support OpenAI models through Azure
- The gateway must support OpenAI models through OpenAI
- The gateway must support Claude models through Anthropic
- The gateway should support self-hosted open-source models
- The gateway should support models hosted on huggingface.co

### Observability support

- All requests and responses must be logged in the platform.
- Metrics (tokens per request/response, requests per minute, latency) must be recorded in the platform.
- Client metadata must be recorded with requests/responses for traceability.
- Observability data must be exported through OpenTelemetry

### Project configuration

- The gateway must allow the use of virtual API keys to abstract access to models
- The gateway must allow self-service creation of virtual API keys
- The gateway must support tracking information per virtual API key

### SDK support

- The gateway must expose an OpenAI compatible API to clients so we can use the existing OpenAI libraries
- The gateway must provide a client SDK for easy management of configuration data

### Authentication and access

- The gateway must integrate with existing authentication systems via OAuth/OpenID connect

## For system administrators

### User onboarding

- The gateway should be manageable via an API so system administrators can integrate via their own workflows.

### Access management

- The platform must support self-service access requests
- The platform must provide automated approval workflows for access requests
- The platform should minimize manual intervention by IT services

### Credit management

- The platform must allow users to request additional credits through a form
- The platform must support automated credit allocation workflows
- The platform should not require IT services contact for routine credit requests

### Platform management

- The platform must be self-hosted
- The platform must be based on open-source software
- The platform should support deployment to various cloud providers

## For business unit managers

### Cost visibility

- The platform must provide cost tracking per project
- The platform must support reporting on LLM spending per project
- The platform must allow business unit managers to view their total spending

### Cost management

- The platform must provide budget controls per project
- The platform should send alerts when spending thresholds are reached

### Reporting

- The data in the platform must be accessible for reporting using external tools
