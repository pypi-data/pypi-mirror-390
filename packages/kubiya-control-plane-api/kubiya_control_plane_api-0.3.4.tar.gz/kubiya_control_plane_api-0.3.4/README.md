# Kubiya Control Plane

[![PyPI version](https://badge.fury.io/py/kubiya-control-plane-api.svg)](https://badge.fury.io/py/kubiya-control-plane-api)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Multi-tenant AI agent orchestration and management stack**

The Kubiya Control Plane is a production-grade stack for deploying, managing, and scaling AI agents across distributed environments. Deploy anywhere - on-premise, Kubernetes, OpenShift, cloud VMs, or serverless - with complete agent lifecycle management and enterprise-grade reliability.

---

## Table of Contents

- [Features](#features)
- [Quick Start](#quick-start)
- [Installation](#installation)
  - [For API Server Deployment](#for-api-server-deployment)
  - [For Worker Deployment](#for-worker-deployment)
  - [For Development](#for-development)
- [Architecture](#architecture)
- [Documentation](#documentation)
- [Usage](#usage)
  - [Starting the API Server](#starting-the-api-server)
  - [Deploying Workers](#deploying-workers)
  - [Creating an Agent](#creating-an-agent)
  - [Executing Workflows](#executing-workflows)
- [Configuration](#configuration)
- [Deployment](#deployment)
- [Development](#development)
- [Testing](#testing)
- [Contributing](#contributing)
- [License](#license)
- [Support](#support)

---

## Features

### Core Capabilities

- **Multi-Tenant Architecture**: Complete isolation between organizations, projects, and environments
- **Distributed Worker System**: Deploy workers anywhere - on-premise, Kubernetes, OpenShift, cloud VMs
- **Dynamic Configuration**: Workers fetch credentials and configuration from Control Plane at startup
- **Hosted or Self-Hosted**: Use Kubiya's hosted control plane or deploy your own stack
- **Flexible Agent Runtime**: Support for multiple agent types (Agno, Claude Code, OpenAI)
- **Extensible Toolsets**: Plugin-based tool system for agent capabilities
- **Policy Enforcement**: OPA-based governance for agent operations
- **LLM Integration**: Multi-provider support via LiteLLM (OpenAI, Anthropic, Gemini, etc.)
- **Comprehensive APIs**: RESTful APIs for all features
- **Pluggable Orchestration**: Default workflow engine included, bring your own when self-hosting

### Enterprise Features

- **High Availability**: Stateless API servers for horizontal scaling
- **Fault Tolerance**: Durable workflow execution with automatic recovery
- **Observability**: Structured logging, distributed tracing, and metrics
- **Security**: JWT authentication, OPA policies, TLS/mTLS support
- **Multi-Region**: Deploy workers close to data sources, API globally
- **Resource Isolation**: Per-environment task queues and worker pools

---

## Quick Start

### Prerequisites

**For using Kubiya hosted control plane (recommended):**
- **Kubiya Account** - [Contact us to onboard](https://kubiya.ai/contact)
- **Kubiya API Key** - Get your key at [https://compose.kubiya.ai/settings#apiKeys](https://compose.kubiya.ai/settings#apiKeys)
- Python 3.10+ (for running workers)

**For self-hosting the control plane (advanced):**
- Python 3.10 or higher
- PostgreSQL 14+ (or Supabase account)
- Workflow orchestration backend (see [Architecture](docs/ARCHITECTURE.md) for options)

### 5-Minute Setup (Using Kubiya Hosted Control Plane)

The fastest way to get started is using the Kubiya hosted control plane:

```bash
# 1. Install Kubiya CLI
curl -fsSL https://cli.kubiya.ai/install.sh | bash

# 2. Set your API key
export KUBIYA_API_KEY="your-api-key"  # Get from https://compose.kubiya.ai/settings#apiKeys

# 3. Start a worker (connects to hosted control plane automatically)
kubiya worker start --queue-id <your-queue-id>
```

That's it! Your worker is now connected to the Kubiya hosted control plane and ready to execute agent workflows.

**For self-hosting the control plane**, see the [Advanced Setup Guide](docs/QUICKSTART.md#self-hosting).

**What the CLI does for you**:
- ✅ Connects to Kubiya hosted control plane (or custom URL via `--control-plane-url`)
- ✅ Creates Python virtual environment
- ✅ Installs `kubiya-control-plane-api[worker]` package
- ✅ Fetches credentials and configuration dynamically
- ✅ Starts worker process
- ✅ Manages worker lifecycle (start/stop/status/logs)

For detailed guides, see:
- **[Quick Start Guide](docs/QUICKSTART.md)** - Complete setup walkthrough
- **[Worker Deployment](docs/WORKER_DEPLOYMENT.md)** - Advanced deployment options
- **[Kubiya CLI](https://github.com/kubiyabot/cli)** - CLI documentation

---

## Installation

The package uses Python optional dependencies (extras) to install only what you need:

### For API Server Deployment

```bash
pip install kubiya-control-plane-api[api]
```

**Includes**: FastAPI, SQLAlchemy, Supabase, Alembic, Temporal, and all API dependencies.

**Does NOT include**: Worker runtime dependencies.

### For Worker Deployment

```bash
pip install kubiya-control-plane-api[worker]
```

**Includes**: Temporal client, Agno, LiteLLM, and worker runtime dependencies.

**Does NOT include**: FastAPI, SQLAlchemy, Supabase, Alembic, or API server dependencies.

**Benefits**:
- ~50-100MB smaller installation
- Faster deployment
- Reduced attack surface
- Clear separation of concerns

### For Development

```bash
# Clone the repository
git clone https://github.com/kubiyabot/agent-control-plane.git
cd agent-control-plane

# Install with all extras (API, worker, dev, test)
pip install -e ".[all]"

# Or install specific extras
pip install -e ".[api,dev]"    # API server + dev tools
pip install -e ".[worker,test]" # Worker + test tools
```

---

## Architecture

The Kubiya Control Plane is a distributed system that enables AI agents to execute tasks reliably across any infrastructure.

### System Overview

```mermaid
graph TB
    User[👤 User / UI] -->|REST API| CP[Kubiya Control Plane]

    CP[🎯 Kubiya Control Plane<br/>FastAPI + PostgreSQL]
    CP -->|Configuration & Credentials| Worker1[🔧 Worker<br/>On-Premise]
    CP -->|Configuration & Credentials| Worker2[🔧 Worker<br/>Kubernetes]
    CP -->|Configuration & Credentials| Worker3[🔧 Worker<br/>Cloud VM]

    CP -.->|Orchestration Backend| Orchestrator[Workflow Orchestrator]
    Orchestrator -.->|Task Distribution| Worker1
    Orchestrator -.->|Task Distribution| Worker2
    Orchestrator -.->|Task Distribution| Worker3

    Worker1 -->|Execute| Agent1[🤖 AI Agent]
    Worker2 -->|Execute| Agent2[🤖 AI Agent]
    Worker3 -->|Execute| Agent3[🤖 AI Agent]

    style CP fill:#4A90E2,stroke:#2E5C8A,stroke-width:3px,color:#fff
    style Worker1 fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style Worker2 fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style Worker3 fill:#50C878,stroke:#2E7D4E,stroke-width:2px,color:#fff
    style Agent1 fill:#9B59B6,stroke:#6C3483,stroke-width:2px,color:#fff
    style Agent2 fill:#9B59B6,stroke:#6C3483,stroke-width:2px,color:#fff
    style Agent3 fill:#9B59B6,stroke:#6C3483,stroke-width:2px,color:#fff
    style Orchestrator fill:#95A5A6,stroke:#5D6D7E,stroke-width:2px,stroke-dasharray: 5 5
```

### Component Details

**1. Kubiya Control Plane (Hosted or Self-Hosted)**
- Multi-tenant agent management (organizations, projects, environments)
- RESTful APIs for agent creation, configuration, and execution
- Dynamic credential distribution to workers
- Execution tracking and monitoring
- Authentication, authorization, and policy enforcement
- **Default**: Use Kubiya's hosted control plane at `https://control-plane.kubiya.ai`
- **Advanced**: Self-host on your infrastructure (see [Architecture Guide](docs/ARCHITECTURE.md))

**2. Distributed Workers (Your Infrastructure)**
- Execute agent workflows in your environment (on-prem, K8s, OpenShift, cloud)
- Fetch credentials and configuration dynamically from Control Plane
- Support multiple agent runtimes (Agno, Claude Code, OpenAI)
- Behind NAT/firewall friendly (outbound connections only)
- Isolated per environment for security

**3. Workflow Orchestration Backend**
- Coordinates task distribution to workers
- Provides durable execution with automatic retries
- Environment-specific task queues
- **Default**: Managed by Kubiya hosted control plane
- **Advanced**: Bring your own (Temporal, Celery, etc.) when self-hosting

### Worker Startup Flow

```mermaid
sequenceDiagram
    participant CLI as Kubiya CLI
    participant Worker as Worker Process
    participant CP as Kubiya Control Plane
    participant Orch as Orchestration Backend

    CLI->>CLI: 1. Create Python venv
    CLI->>CLI: 2. Install worker package
    CLI->>Worker: 3. Start worker process

    Worker->>CP: 4. POST /worker-queues/{id}/start<br/>(with KUBIYA_API_KEY)
    CP->>Worker: 5. Return credentials:<br/>• orchestrator_host<br/>• orchestrator_api_key<br/>• task_queue_name<br/>• litellm_api_url

    Worker->>Worker: 6. Configure environment
    Worker->>Orch: 7. Connect to orchestrator
    Worker->>Orch: 8. Poll for workflows

    Note over Worker,Orch: Worker ready to execute agent tasks
```

**Key Benefits**:
- ✅ **Simple deployment**: Workers only need an API key - no complex configuration
- ✅ **Secure**: Credentials fetched dynamically, never stored in config files
- ✅ **Flexible**: Deploy workers anywhere - on-premise, cloud, Kubernetes, OpenShift
- ✅ **Scalable**: Add more workers to scale horizontally
- ✅ **Hosted or self-hosted**: Use Kubiya's hosted control plane or run your own

For detailed architecture diagrams and deployment patterns, see [Architecture Guide](docs/ARCHITECTURE.md).

---

## Documentation

### Core Documentation

- **[Quick Start Guide](docs/QUICKSTART.md)** - Get up and running in minutes
- **[Architecture Guide](docs/ARCHITECTURE.md)** - System architecture with diagrams
- **[Worker Deployment](docs/WORKER_DEPLOYMENT.md)** - Worker deployment and management
- **[Documentation Index](docs/README.md)** - Complete documentation index
- **[Kubiya CLI](https://github.com/kubiyabot/cli)** - CLI documentation for worker management

---

## Usage

### Starting the API Server

#### Option 1: Direct Run (Development)

```bash
# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/control_plane"
export TEMPORAL_HOST="localhost:7233"
export TEMPORAL_NAMESPACE="default"
export KUBIYA_API_KEY="your-api-key"
export SECRET_KEY="your-secret-key"

# Run migrations
alembic upgrade head

# Start server
uvicorn control_plane_api.app.main:app --reload --port 7777
```

#### Option 2: Docker Compose (Local Development)

```bash
# Start all services (API, PostgreSQL, Temporal)
docker-compose up

# API available at http://localhost:7777
# Temporal UI at http://localhost:8080
```

#### Option 3: Production Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment options:
- Docker containers with orchestration (ECS, Kubernetes)
- Serverless (Vercel, AWS Lambda)
- Traditional VMs/instances

### Deploying Workers

#### Via CLI (Recommended)

```bash
# Install Kubiya CLI
# See: https://github.com/kubiyabot/cli

# Start worker
export KUBIYA_API_KEY="your-api-key"
kubiya worker start --queue-id <your-queue-id>
```

The CLI will:
1. Create a Python virtual environment
2. Install `kubiya-control-plane-api[worker]`
3. Start the worker process
4. Worker fetches credentials from Control Plane
5. Worker connects to Temporal and starts processing tasks

#### Manual (Advanced)

```bash
# Create venv
python -m venv worker-venv
source worker-venv/bin/activate

# Install worker package
pip install kubiya-control-plane-api[worker]

# Set API key
export KUBIYA_API_KEY="your-api-key"

# Start worker
kubiya-control-plane-worker --queue-id <your-queue-id>
```

### Creating an Agent

```python
import httpx

# Create an agent via API
response = httpx.post(
    "https://control-plane.kubiya.ai/api/v1/agents",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "name": "DevOps Assistant",
        "description": "Helps with Kubernetes and CI/CD tasks",
        "environment_id": "env-123",
        "agent_type": "agno",
        "llm_config": {
            "provider": "anthropic",
            "model": "claude-3-5-sonnet-20241022",
            "temperature": 0.7
        },
        "toolsets": ["kubernetes", "github", "slack"],
        "policies": ["require_approval_for_prod"]
    }
)

agent = response.json()
print(f"Agent created: {agent['id']}")
```

### Executing Workflows

```python
# Execute an agent workflow
response = httpx.post(
    "https://control-plane.kubiya.ai/api/v1/executions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={
        "agent_id": "agent-123",
        "workflow_type": "agent_chat",
        "input": {
            "message": "Deploy the frontend app to staging",
            "context": {
                "environment": "staging",
                "requester": "user@example.com"
            }
        }
    }
)

execution = response.json()
print(f"Execution started: {execution['id']}")
print(f"Status: {execution['status']}")
```

---

## Configuration

### Environment Variables

#### Required (API Server)

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname
# Or for Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=your-supabase-key

# Temporal
TEMPORAL_HOST=your-namespace.tmprl.cloud:7233
TEMPORAL_NAMESPACE=your-namespace

# Authentication
KUBIYA_API_KEY=your-api-key
SECRET_KEY=your-secret-key-for-jwt
```

#### Optional (API Server)

```bash
# Temporal (for mTLS)
TEMPORAL_CLIENT_CERT_PATH=/path/to/client.pem
TEMPORAL_CLIENT_KEY_PATH=/path/to/client.key

# Redis (caching)
REDIS_URL=redis://localhost:6379/0

# LiteLLM Proxy
LITELLM_API_URL=https://llm-proxy.kubiya.ai
LITELLM_API_KEY=your-litellm-key

# Logging
LOG_LEVEL=info
ENVIRONMENT=production

# CORS
CORS_ORIGINS=https://app.kubiya.ai,https://dashboard.kubiya.ai
```

#### Required (Worker)

```bash
# Only need API key - everything else fetched dynamically
KUBIYA_API_KEY=your-api-key

# Optional: Override control plane URL (defaults to production)
CONTROL_PLANE_URL=https://control-plane.kubiya.ai
```

### Configuration Files

Create `.env` file in the project root:

```bash
# Copy example config
cp env.example .env

# Edit with your values
nano .env
```

---

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t kubiya-control-plane-api:latest .

# Run API server
docker run -p 7777:7777 \
  -e DATABASE_URL="postgresql://..." \
  -e TEMPORAL_HOST="..." \
  -e KUBIYA_API_KEY="..." \
  kubiya-control-plane-api:latest
```

### Kubernetes Deployment

```bash
# Install via Helm
helm install kubiya-control-plane ./helm/kubiya-control-plane \
  --set database.url="postgresql://..." \
  --set temporal.host="..." \
  --set kubiya.apiKey="..."
```

### Serverless Deployment (Vercel)

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel deploy

# Set environment variables in Vercel dashboard
```

For detailed deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

---

## Development

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/kubiyabot/agent-control-plane.git
cd agent-control-plane

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install with dev dependencies
pip install -e ".[all]"

# Set up pre-commit hooks
pre-commit install
```

### Running Locally

```bash
# Start local PostgreSQL and Temporal
docker-compose up -d postgres temporal

# Run migrations
alembic upgrade head

# Start API server
uvicorn control_plane_api.app.main:app --reload

# In another terminal, start a worker
export KUBIYA_API_KEY="test-key"
python -m control_plane_api.worker.worker --queue-id test-queue
```

### Code Quality

```bash
# Format code
black .
ruff check . --fix

# Type checking
mypy control_plane_api/

# Linting
ruff check .
```

---

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=control_plane_api --cov-report=html

# Run specific test types
pytest -m unit              # Unit tests only
pytest -m integration       # Integration tests only
pytest -k test_agent        # Tests matching pattern

# Run with verbose output
pytest -v -s
```

### Test Categories

- **Unit Tests**: Fast tests for individual components
- **Integration Tests**: Tests requiring external services
- **E2E Tests**: End-to-end workflow tests

---

## API Endpoints

### Core Resources

```
GET    /api/v1/projects              # List projects
POST   /api/v1/projects              # Create project
GET    /api/v1/projects/{id}         # Get project
PATCH  /api/v1/projects/{id}         # Update project
DELETE /api/v1/projects/{id}         # Delete project

GET    /api/v1/environments          # List environments
POST   /api/v1/environments          # Create environment
GET    /api/v1/environments/{id}     # Get environment
PATCH  /api/v1/environments/{id}     # Update environment
DELETE /api/v1/environments/{id}     # Delete environment

GET    /api/v1/agents                # List agents
POST   /api/v1/agents                # Create agent
GET    /api/v1/agents/{id}           # Get agent
PATCH  /api/v1/agents/{id}           # Update agent
DELETE /api/v1/agents/{id}           # Delete agent

GET    /api/v1/executions            # List executions
POST   /api/v1/executions            # Start execution
GET    /api/v1/executions/{id}       # Get execution status
DELETE /api/v1/executions/{id}       # Cancel execution

POST   /api/v1/worker-queues/{id}/start  # Worker startup (credentials)
```

### Documentation

- **Interactive API Docs**: `http://localhost:7777/api/docs` (Swagger UI)
- **Alternative Docs**: `http://localhost:7777/api/redoc` (ReDoc)
- **OpenAPI Spec**: `http://localhost:7777/openapi.json`

---

## Package Structure

```
control_plane_api/
├── app/                    # API Server (install with [api] extra)
│   ├── main.py            # FastAPI application
│   ├── routers/           # API endpoints
│   ├── models/            # Database models
│   ├── services/          # Business logic
│   ├── lib/               # Client libraries
│   └── middleware/        # Middleware
│
├── worker/                # Worker Runtime (install with [worker] extra)
│   ├── worker.py         # Worker entry point
│   ├── workflows/        # Temporal workflows
│   ├── activities/       # Temporal activities
│   ├── runtimes/         # Agent runtimes
│   └── services/         # Worker services
│
└── tests/                # Tests
    ├── unit/             # Unit tests
    └── integration/      # Integration tests
```

---

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Run code quality checks (`black .`, `ruff check .`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Support

### Documentation

- [Main Documentation](https://docs.kubiya.ai)
- [API Reference](API_REFERENCE.md)
- [Architecture Guide](ARCHITECTURE.md)
- [Deployment Guide](DEPLOYMENT.md)

### Community

- [GitHub Issues](https://github.com/kubiyabot/agent-control-plane/issues) - Bug reports and feature requests
- [GitHub Discussions](https://github.com/kubiyabot/agent-control-plane/discussions) - Questions and discussions
- [Discord Community](https://discord.gg/kubiya) - Real-time chat and support
- [Stack Overflow](https://stackoverflow.com/questions/tagged/kubiya) - Technical Q&A

### Commercial Support

For enterprise support, custom development, and consulting:
- Email: support@kubiya.ai
- Website: https://kubiya.ai
- Schedule a call: https://kubiya.ai/contact

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

---

## Security

For security issues, please email security@kubiya.ai instead of using the issue tracker.

See [SECURITY.md](SECURITY.md) for our security policy and vulnerability disclosure process.

---

## Acknowledgments

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [PostgreSQL](https://www.postgresql.org/) - Reliable relational database
- [SQLAlchemy](https://www.sqlalchemy.org/) - Python SQL toolkit
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [LiteLLM](https://docs.litellm.ai/) - Multi-provider LLM integration
- [Agno](https://github.com/agno-framework/agno) - Agent orchestration framework

**Workflow Orchestration Options**:
- [Temporal](https://temporal.io/) - Default workflow orchestration backend
- Pluggable architecture supports other backends when self-hosting

---

<div align="center">

**[Website](https://kubiya.ai)** • **[Documentation](https://docs.kubiya.ai)** • **[API Reference](API_REFERENCE.md)** • **[Blog](https://kubiya.ai/blog)**

Made with ❤️ by the [Kubiya team](https://kubiya.ai/about)

</div>
