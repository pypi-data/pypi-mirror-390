# Kubiya Control Plane API

Multi-tenant AI agent orchestration and management platform powered by Temporal workflows.

## Installation

### Basic Installation

```bash
pip install kubiya-control-plane-api
```

### Installation with Extras

Install with development dependencies:

```bash
pip install "kubiya-control-plane-api[dev]"
```

Install with test dependencies:

```bash
pip install "kubiya-control-plane-api[test]"
```

Install with all optional dependencies:

```bash
pip install "kubiya-control-plane-api[all]"
```

## Running for Development

### 1. Clone the repository

```bash
git clone https://github.com/kubiyabot/agent-control-plane.git
cd agent-control-plane
```

### 2. Set up environment variables

Create a `.env` file with the required variables (see below).

### 3. Build an image and run.

```bash
make build

make up
```

The API will be available at `http://localhost:7777/api/docs`

## Running the Worker

The worker processes Temporal workflows for agent execution.

### Using the CLI command

After installing the package, run:

```bash
kubiya-control-plane-worker
```

### Using Python module

```bash
python -m control_plane_api.worker
```

## Required Environment Variables

The following environment variables **must** be set to run the worker:

### Temporal Configuration (Required)

```bash
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default
```

- `TEMPORAL_HOST`: Address of your Temporal server
- `TEMPORAL_NAMESPACE`: Temporal namespace to use

### Database Configuration (Required)

**Option 1: Direct PostgreSQL**

```bash
DATABASE_URL=postgresql://user:password@localhost:5432/control_plane
```

**Option 2: Supabase**

```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
SUPABASE_POSTGRES_URL=postgresql://user:password@host:5432/database
```

You need **either** `DATABASE_URL` **or** all three Supabase variables.

### Temporal Cloud Authentication (If using Temporal Cloud)

If connecting to Temporal Cloud instead of a self-hosted server, you also need **one** of:

**Option A: API Key**

```bash
TEMPORAL_API_KEY=your-temporal-cloud-api-key
```

**Option B: mTLS Certificates**

```bash
TEMPORAL_CLIENT_CERT_PATH=/path/to/cert.pem
TEMPORAL_CLIENT_KEY_PATH=/path/to/key.pem
```

### Quick Start Example

```bash
# 1. Install the package
pip install kubiya-control-plane-api

# 2. Set required environment variables
export TEMPORAL_HOST=localhost:7233
export TEMPORAL_NAMESPACE=default
export DATABASE_URL=postgresql://user:password@localhost:5432/control_plane

# 3. Run the worker
kubiya-control-plane-worker
```

The worker will connect to Temporal and start processing agent execution workflows.
