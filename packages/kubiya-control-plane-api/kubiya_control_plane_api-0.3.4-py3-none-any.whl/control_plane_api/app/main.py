from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from control_plane_api.app.config import settings
from control_plane_api.app.routers import agents, teams, workflows, health, executions, presence, runners, workers, projects, models, models_v2, task_queues, worker_queues, environment_context, team_context, context_manager, skills, skills_definitions, environments, runtimes, secrets, integrations, execution_environment, policies, task_planning, jobs, analytics
from control_plane_api.app.routers import agents_v2  # New multi-tenant agent router

# Configure structured logging
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        getattr(logging, settings.log_level.upper(), logging.INFO)
    ),
    logger_factory=structlog.PrintLoggerFactory(),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for serverless"""
    logger.info(
        "agent_control_plane_starting",
        version=settings.api_version,
        environment=settings.environment
    )
    # No database initialization needed for serverless
    # Supabase client is initialized on-demand
    yield
    logger.info("agent_control_plane_shutting_down")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan,
    # Disable lifespan for Vercel (will be "off" via Mangum)
    openapi_url="/api/openapi.json" if settings.environment != "production" else None,
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url="/api/redoc" if settings.environment != "production" else None,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (all routes under /api/v1)
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(models_v2.router, prefix="/api/v1/models", tags=["Models"])  # LLM models CRUD (database-backed)
app.include_router(runtimes.router, prefix="/api/v1", tags=["Runtimes"])  # Agent runtime types
app.include_router(secrets.router, prefix="/api/v1", tags=["Secrets"])  # Kubiya secrets proxy
app.include_router(integrations.router, prefix="/api/v1", tags=["Integrations"])  # Kubiya integrations proxy
app.include_router(execution_environment.router, prefix="/api/v1", tags=["Execution Environment"])  # Resolved execution environment for workers
app.include_router(projects.router, prefix="/api/v1/projects", tags=["Projects"])  # Multi-project management
app.include_router(environments.router, prefix="/api/v1/environments", tags=["Environments"])  # Environment management
app.include_router(task_queues.router, prefix="/api/v1/task-queues", tags=["Task Queues"])  # Legacy endpoint (use /environments)
app.include_router(worker_queues.router, prefix="/api/v1", tags=["Worker Queues"])  # Worker queue management per environment
app.include_router(environment_context.router, prefix="/api/v1", tags=["Environment Context"])  # Environment context management
app.include_router(team_context.router, prefix="/api/v1", tags=["Team Context"])  # Team context management
app.include_router(context_manager.router, prefix="/api/v1", tags=["Context Manager"])  # Unified context management
app.include_router(skills_definitions.router, prefix="/api/v1/skills", tags=["Tool Sets"])  # Skill definitions and templates (must be before skills.router)
app.include_router(skills.router, prefix="/api/v1/skills", tags=["Tool Sets"])  # Tool sets management
app.include_router(policies.router, prefix="/api/v1/policies", tags=["Policies"])  # Policy management and enforcement
app.include_router(task_planning.router, prefix="/api/v1", tags=["Task Planning"])  # AI-powered task planning
app.include_router(agents_v2.router, prefix="/api/v1/agents", tags=["Agents"])  # Use new multi-tenant router
app.include_router(runners.router, prefix="/api/v1/runners", tags=["Runners"])  # Proxy to Kubiya API
app.include_router(workers.router, prefix="/api/v1/workers", tags=["Workers"])  # Worker registration and heartbeats
app.include_router(teams.router, prefix="/api/v1/teams", tags=["Teams"])
app.include_router(workflows.router, prefix="/api/v1/workflows", tags=["Workflows"])
app.include_router(executions.router, prefix="/api/v1/executions", tags=["Executions"])
app.include_router(presence.router, prefix="/api/v1/presence", tags=["Presence"])
app.include_router(jobs.router, prefix="/api/v1/jobs", tags=["Jobs"])  # Scheduled and webhook-triggered jobs
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])  # Execution metrics and reporting


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Agent Control Plane",
        "version": settings.api_version,
        "environment": settings.environment,
        "docs": "/api/docs" if settings.environment != "production" else None,
    }


@app.get("/api")
async def api_root():
    """API root endpoint"""
    return {
        "message": "Agent Control Plane API",
        "version": settings.api_version,
        "endpoints": {
            "projects": "/api/v1/projects",
            "task_queues": "/api/v1/task-queues",
            "agents": "/api/v1/agents",
            "teams": "/api/v1/teams",
            "skills": "/api/v1/skills",
            "policies": "/api/v1/policies",
            "workflows": "/api/v1/workflows",
            "executions": "/api/v1/executions",
            "presence": "/api/v1/presence",
            "runners": "/api/v1/runners",
            "workers": "/api/v1/workers",
            "models": "/api/v1/models",
            "runtimes": "/api/v1/runtimes",
            "secrets": "/api/v1/secrets",
            "integrations": "/api/v1/integrations",
            "health": "/api/health",
        }
    }
