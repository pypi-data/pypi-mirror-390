"""
Worker Queues router - Manage worker queues within environments.

Each environment can have multiple worker queues for fine-grained worker management.
Task queue naming: {org_id}.{environment_name}.{worker_queue_name}
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import PlainTextResponse
from typing import List, Optional, Literal
from datetime import datetime, timedelta
from pydantic import BaseModel, Field
import structlog
import uuid
import os
import json

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase
from control_plane_api.app.lib.redis_client import get_redis_client

logger = structlog.get_logger()

router = APIRouter()

# Stale worker threshold: 60 seconds (2x the default heartbeat interval of 30s)
STALE_WORKER_THRESHOLD_SECONDS = 60


async def get_active_workers_from_redis(org_id: str, queue_id: Optional[str] = None) -> dict:
    """
    Get active workers from Redis heartbeats.

    Redis heartbeats have automatic TTL (5 minutes), so if a worker hasn't sent a heartbeat
    the key will automatically expire. This eliminates the need to manually mark workers as stale.

    Args:
        org_id: Organization ID
        queue_id: Optional queue ID to filter by

    Returns:
        Dict with worker_id -> heartbeat_data mapping
    """
    redis_client = get_redis_client()

    if not redis_client:
        logger.warning("redis_unavailable_for_worker_query", org_id=org_id)
        return {}

    try:
        # Get all worker heartbeat keys for this org
        # We need to get worker records from DB to map worker_id -> queue_id
        client = get_supabase()
        workers_db = (
            client.table("worker_heartbeats")
            .select("id, worker_queue_id")
            .eq("organization_id", org_id)
            .execute()
        )

        active_workers = {}

        for worker in workers_db.data or []:
            worker_id = worker["id"]
            worker_queue_id = worker.get("worker_queue_id")

            # Skip if queue_id filter is specified and doesn't match
            if queue_id and worker_queue_id != queue_id:
                continue

            # Check if heartbeat exists in Redis (within TTL window)
            redis_key = f"worker:{worker_id}:heartbeat"
            heartbeat_data = await redis_client.get(redis_key)

            if heartbeat_data:
                try:
                    data = json.loads(heartbeat_data)
                    # Check if heartbeat is recent (within threshold)
                    last_heartbeat = datetime.fromisoformat(data.get("last_heartbeat", ""))
                    age_seconds = (datetime.utcnow() - last_heartbeat).total_seconds()

                    if age_seconds <= STALE_WORKER_THRESHOLD_SECONDS:
                        active_workers[worker_id] = {
                            **data,
                            "worker_queue_id": worker_queue_id,
                        }
                except (json.JSONDecodeError, ValueError) as e:
                    logger.warning("invalid_heartbeat_data", worker_id=worker_id, error=str(e))
                    continue

        return active_workers

    except Exception as e:
        logger.error("failed_to_get_active_workers_from_redis", error=str(e), org_id=org_id)
        return {}


# Pydantic schemas
class WorkerQueueCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50, description="Worker queue name (lowercase, no spaces)")
    display_name: Optional[str] = Field(None, description="User-friendly display name")
    description: Optional[str] = Field(None, description="Queue description")
    max_workers: Optional[int] = Field(None, ge=1, description="Max workers allowed (NULL = unlimited)")
    heartbeat_interval: int = Field(30, ge=10, le=300, description="Seconds between heartbeats")
    tags: List[str] = Field(default_factory=list)
    settings: dict = Field(default_factory=dict)


class WorkerQueueUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    display_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    max_workers: Optional[int] = Field(None, ge=1)
    heartbeat_interval: Optional[int] = Field(None, ge=10, le=300)
    tags: Optional[List[str]] = None
    settings: Optional[dict] = None


class WorkerQueueResponse(BaseModel):
    id: str
    organization_id: str
    environment_id: str
    name: str
    display_name: Optional[str]
    description: Optional[str]
    status: str
    max_workers: Optional[int]
    heartbeat_interval: int
    tags: List[str]
    settings: dict
    created_at: str
    updated_at: str
    created_by: Optional[str]
    # Computed
    active_workers: int = 0
    task_queue_name: str  # Full task queue name: org.env.worker_queue


@router.get("/worker-queues", response_model=List[WorkerQueueResponse])
async def list_all_worker_queues(
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """List all worker queues across all environments for the organization"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Get all worker queues for this organization
        result = (
            client.table("worker_queues")
            .select("*, environments(name)")
            .eq("organization_id", org_id)
            .order("created_at", desc=False)
            .execute()
        )

        if not result.data:
            return []

        # Get active workers from Redis (with automatic TTL-based expiration)
        active_workers = await get_active_workers_from_redis(org_id)

        # Count workers per queue
        worker_counts = {}
        for worker_id, worker_data in active_workers.items():
            queue_id = worker_data.get("worker_queue_id")
            if queue_id:
                worker_counts[queue_id] = worker_counts.get(queue_id, 0) + 1

        # Build response
        queues = []
        for queue in result.data:
            # Use queue UUID as task queue name for security
            task_queue_name = queue["id"]
            active_worker_count = worker_counts.get(queue["id"], 0)

            # Get environment name from join
            env_data = queue.get("environments")
            environment_name = env_data.get("name") if env_data else None

            queue_copy = dict(queue)
            queue_copy.pop("environments", None)  # Remove join data

            queues.append(
                WorkerQueueResponse(
                    **queue_copy,
                    active_workers=active_worker_count,
                    task_queue_name=task_queue_name,
                    environment_name=environment_name,
                )
            )

        logger.info(
            "all_worker_queues_listed",
            count=len(queues),
            org_id=org_id,
        )

        return queues

    except HTTPException:
        raise
    except Exception as e:
        logger.error("all_worker_queues_list_failed", error=str(e), org_id=org_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list all worker queues: {str(e)}"
        )


@router.post("/environments/{environment_id}/worker-queues", response_model=WorkerQueueResponse, status_code=status.HTTP_201_CREATED)
async def create_worker_queue(
    environment_id: str,
    queue_data: WorkerQueueCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Create a new worker queue within an environment"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Validate environment exists
        env_result = (
            client.table("environments")
            .select("id, name")
            .eq("id", environment_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if not env_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found"
            )

        environment = env_result.data

        # Check if worker queue name already exists in this environment
        existing = (
            client.table("worker_queues")
            .select("id")
            .eq("environment_id", environment_id)
            .eq("name", queue_data.name)
            .execute()
        )

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Worker queue '{queue_data.name}' already exists in this environment"
            )

        # Create worker queue
        queue_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        queue_record = {
            "id": queue_id,
            "organization_id": org_id,
            "environment_id": environment_id,
            "name": queue_data.name,
            "display_name": queue_data.display_name or queue_data.name,
            "description": queue_data.description,
            "status": "active",
            "max_workers": queue_data.max_workers,
            "heartbeat_interval": queue_data.heartbeat_interval,
            "tags": queue_data.tags,
            "settings": queue_data.settings,
            "created_at": now,
            "updated_at": now,
            "created_by": organization.get("user_id"),
        }

        result = client.table("worker_queues").insert(queue_record).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create worker queue"
            )

        queue = result.data[0]

        # Use queue UUID as task queue name for security (unpredictable)
        task_queue_name = queue_id

        logger.info(
            "worker_queue_created",
            queue_id=queue_id,
            queue_name=queue["name"],
            environment_id=environment_id,
            task_queue_name=task_queue_name,
            org_id=org_id,
        )

        return WorkerQueueResponse(
            **queue,
            active_workers=0,
            task_queue_name=task_queue_name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("worker_queue_creation_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create worker queue: {str(e)}"
        )


@router.get("/environments/{environment_id}/worker-queues", response_model=List[WorkerQueueResponse])
async def list_worker_queues(
    environment_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """List all worker queues in an environment"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Get environment name
        env_result = (
            client.table("environments")
            .select("name")
            .eq("id", environment_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if not env_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Environment not found"
            )

        environment_name = env_result.data["name"]

        # Get worker queues
        result = (
            client.table("worker_queues")
            .select("*")
            .eq("environment_id", environment_id)
            .order("created_at", desc=False)
            .execute()
        )

        if not result.data:
            return []

        # Get active workers from Redis (with automatic TTL-based expiration)
        active_workers = await get_active_workers_from_redis(org_id)

        # Count workers per queue
        worker_counts = {}
        for worker_id, worker_data in active_workers.items():
            queue_id = worker_data.get("worker_queue_id")
            if queue_id:
                worker_counts[queue_id] = worker_counts.get(queue_id, 0) + 1

        # Build response
        queues = []
        for queue in result.data:
            # Use queue UUID as task queue name for security
            task_queue_name = queue["id"]
            active_workers = worker_counts.get(queue["id"], 0)

            queues.append(
                WorkerQueueResponse(
                    **queue,
                    active_workers=active_workers,
                    task_queue_name=task_queue_name,
                )
            )

        logger.info(
            "worker_queues_listed",
            count=len(queues),
            environment_id=environment_id,
            org_id=org_id,
        )

        return queues

    except HTTPException:
        raise
    except Exception as e:
        logger.error("worker_queues_list_failed", error=str(e), environment_id=environment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list worker queues: {str(e)}"
        )


@router.get("/worker-queues/{queue_id}", response_model=WorkerQueueResponse)
async def get_worker_queue(
    queue_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get a specific worker queue by ID"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Get worker queue
        result = (
            client.table("worker_queues")
            .select("*")
            .eq("id", queue_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worker queue not found"
            )

        queue = result.data

        # Get environment name separately
        environment_name = "unknown"
        if queue.get("environment_id"):
            env_result = (
                client.table("environments")
                .select("name")
                .eq("id", queue["environment_id"])
                .eq("organization_id", org_id)
                .maybe_single()
                .execute()
            )
            if env_result.data:
                environment_name = env_result.data["name"]

        # Get active workers from Redis for this specific queue
        active_workers_dict = await get_active_workers_from_redis(org_id, queue_id)
        active_workers = len(active_workers_dict)

        # Remove joined data
        queue.pop("environments", None)

        # Use queue UUID as task queue name for security
        task_queue_name = queue_id

        return WorkerQueueResponse(
            **queue,
            active_workers=active_workers,
            task_queue_name=task_queue_name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("worker_queue_get_failed", error=str(e), queue_id=queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get worker queue: {str(e)}"
        )


@router.patch("/worker-queues/{queue_id}", response_model=WorkerQueueResponse)
async def update_worker_queue(
    queue_id: str,
    queue_data: WorkerQueueUpdate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Update a worker queue"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Check if queue exists
        existing = (
            client.table("worker_queues")
            .select("id, environment_id")
            .eq("id", queue_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if not existing.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worker queue not found"
            )

        # Build update dict
        update_data = queue_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()

        # Update queue
        result = (
            client.table("worker_queues")
            .update(update_data)
            .eq("id", queue_id)
            .eq("organization_id", org_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update worker queue"
            )

        queue = result.data[0]

        # Get environment name and active workers
        env_result = (
            client.table("environments")
            .select("name")
            .eq("id", queue["environment_id"])
            .single()
            .execute()
        )

        environment_name = env_result.data["name"] if env_result.data else "unknown"

        workers_result = (
            client.table("worker_heartbeats")
            .select("id")
            .eq("worker_queue_id", queue_id)
            .in_("status", ["active", "idle", "busy"])
            .execute()
        )

        active_workers = len(workers_result.data or [])
        # Use queue UUID as task queue name for security
        task_queue_name = queue_id

        logger.info(
            "worker_queue_updated",
            queue_id=queue_id,
            org_id=org_id,
        )

        return WorkerQueueResponse(
            **queue,
            active_workers=active_workers,
            task_queue_name=task_queue_name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("worker_queue_update_failed", error=str(e), queue_id=queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update worker queue: {str(e)}"
        )


@router.delete("/worker-queues/{queue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_worker_queue(
    queue_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Delete a worker queue"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Prevent deleting default queue
        queue_check = (
            client.table("worker_queues")
            .select("name")
            .eq("id", queue_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if queue_check.data and queue_check.data.get("name") == "default":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the default worker queue"
            )

        # Check for active workers in Redis
        active_workers = await get_active_workers_from_redis(org_id, queue_id)

        if active_workers:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot delete worker queue with {len(active_workers)} active workers"
            )

        # Delete queue
        result = (
            client.table("worker_queues")
            .delete()
            .eq("id", queue_id)
            .eq("organization_id", org_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worker queue not found"
            )

        logger.info("worker_queue_deleted", queue_id=queue_id, org_id=org_id)

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("worker_queue_delete_failed", error=str(e), queue_id=queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete worker queue: {str(e)}"
        )


@router.get("/worker-queues/{queue_id}/install-script")
async def get_installation_script(
    queue_id: str,
    deployment_type: Literal["docker", "kubernetes", "openshift", "local"] = "local",
    request: Request = None,
    organization: dict = Depends(get_current_organization),
):
    """
    Generate an installation script for setting up a worker for this queue.

    Supports multiple deployment types:
    - local: Python virtual environment setup
    - docker: Docker run command
    - kubernetes: Kubernetes deployment YAML
    - openshift: OpenShift deployment YAML
    """
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Get worker queue details
        result = (
            client.table("worker_queues")
            .select("*")
            .eq("id", queue_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worker queue not found"
            )

        queue = result.data

        # Get environment name separately
        environment_name = "default"
        if queue.get("environment_id"):
            env_result = (
                client.table("environments")
                .select("name")
                .eq("id", queue["environment_id"])
                .eq("organization_id", org_id)
                .maybe_single()
                .execute()
            )
            if env_result.data:
                environment_name = env_result.data["name"]
        queue_name = queue["name"]

        # Get control plane URL
        control_plane_url = os.getenv("CONTROL_PLANE_URL", "https://agent-control-plane.vercel.app")

        # Generate new worker ID
        worker_id = str(uuid.uuid4())

        # Generate script based on deployment type
        if deployment_type == "local":
            script = _generate_local_script(worker_id, control_plane_url)
        elif deployment_type == "docker":
            script = _generate_docker_script(worker_id, control_plane_url, queue_name, environment_name)
        elif deployment_type == "kubernetes":
            script = _generate_kubernetes_script(worker_id, control_plane_url, queue_name, environment_name)
        elif deployment_type == "openshift":
            script = _generate_openshift_script(worker_id, control_plane_url, queue_name, environment_name)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported deployment type: {deployment_type}"
            )

        logger.info(
            "installation_script_generated",
            queue_id=queue_id,
            deployment_type=deployment_type,
            worker_id=worker_id,
            org_id=org_id,
        )

        return PlainTextResponse(content=script, media_type="text/plain")

    except HTTPException:
        raise
    except Exception as e:
        logger.error("installation_script_generation_failed", error=str(e), queue_id=queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate installation script: {str(e)}"
        )


class WorkerStartResponse(BaseModel):
    """Worker start configuration"""
    worker_id: str
    task_queue_name: str  # The queue UUID
    temporal_namespace: str
    temporal_host: str
    temporal_api_key: str
    organization_id: str
    control_plane_url: str
    heartbeat_interval: int
    # LiteLLM configuration for agno workflows/activities
    litellm_api_url: str
    litellm_api_key: str
    # Queue metadata
    queue_name: str
    environment_name: str


@router.post("/worker-queues/{queue_id}/start", response_model=WorkerStartResponse)
async def start_worker_for_queue(
    queue_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Start a worker for a specific queue.

    This endpoint is called by the CLI with: kubiya worker start --queue-id={queue_id}

    Returns all configuration needed for the worker to connect to Temporal.
    """
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Get worker queue - use maybe_single to avoid exception on missing rows
        try:
            result = (
                client.table("worker_queues")
                .select("*")
                .eq("id", queue_id)
                .eq("organization_id", org_id)
                .maybe_single()
                .execute()
            )
        except Exception as db_error:
            # Handle postgrest 204 No Content response (queue not found)
            error_str = str(db_error)
            if "'code': '204'" in error_str or "Missing response" in error_str:
                # Treat 204 as "no data found" rather than an error
                result = type('obj', (object,), {'data': None})()
            else:
                logger.error("database_query_failed", error=str(db_error), queue_id=queue_id)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Database query failed. Please contact support."
                ) from db_error

        if not result or not result.data:
            # Check if queue exists at all (might be in different org)
            check_result = (
                client.table("worker_queues")
                .select("id, organization_id")
                .eq("id", queue_id)
                .maybe_single()
                .execute()
            )

            if check_result and check_result.data:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Worker queue '{queue_id}' not found in your organization"
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Worker queue '{queue_id}' does not exist. Please create a queue from the UI first."
                )

        queue = result.data

        # Get environment/task_queue separately
        if not queue.get("environment_id"):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Worker queue '{queue.get('name', queue_id)}' has no environment configured. Please contact support."
            )

        env_result = (
            client.table("environments")
            .select("name")
            .eq("id", queue["environment_id"])
            .eq("organization_id", org_id)
            .maybe_single()
            .execute()
        )

        if not env_result or not env_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Environment configuration error for queue '{queue.get('name', queue_id)}'. Please contact support."
            )

        environment_name = env_result.data["name"]

        # Check if queue is active
        if queue.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Worker queue is not active (status: {queue.get('status')})"
            )

        # TEMPORARY: Use fixed namespace + admin API key
        import os
        namespace = {
            "namespace_name": "agent-control-plane.lpagu",
            "api_key_encrypted": os.getenv("TEMPORAL_CLOUD_ADMIN_TOKEN", ""),
        }

        # Generate worker ID
        worker_id = str(uuid.uuid4())

        # Create worker heartbeat record
        now = datetime.utcnow().isoformat()
        worker_record = {
            "id": worker_id,
            "worker_id": worker_id,
            "organization_id": org_id,
            "worker_queue_id": queue_id,
            "environment_name": environment_name,
            "status": "active",
            "tasks_processed": 0,
            "registered_at": now,
            "last_heartbeat": now,
            "updated_at": now,
            "worker_metadata": {},
        }

        client.table("worker_heartbeats").insert(worker_record).execute()

        # Get control plane URL
        control_plane_url = os.getenv("CONTROL_PLANE_URL", "https://agent-control-plane.vercel.app")
        temporal_host = os.getenv("TEMPORAL_HOST", "us-east-1.aws.api.temporal.io:7233")

        # Get LiteLLM configuration for agno workflows/activities
        litellm_api_url = os.getenv("LITELLM_API_URL", "https://llm-proxy.kubiya.ai")
        litellm_api_key = os.getenv("LITELLM_API_KEY", "")

        # Task queue name is just the queue UUID for security
        task_queue_name = queue_id

        logger.info(
            "worker_started_for_queue",
            worker_id=worker_id,
            queue_id=queue_id,
            task_queue_name=task_queue_name,
            org_id=org_id,
        )

        return WorkerStartResponse(
            worker_id=worker_id,
            task_queue_name=task_queue_name,
            temporal_namespace=namespace["namespace_name"],
            temporal_host=temporal_host,
            temporal_api_key=namespace["api_key_encrypted"],
            organization_id=org_id,
            control_plane_url=control_plane_url,
            heartbeat_interval=queue.get("heartbeat_interval", 30),
            litellm_api_url=litellm_api_url,
            litellm_api_key=litellm_api_key,
            queue_name=queue["name"],
            environment_name=environment_name,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "worker_start_for_queue_failed",
            error=str(e),
            error_type=type(e).__name__,
            queue_id=queue_id,
            org_id=organization.get("id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start worker due to an internal error. Please try again or contact support. (Error ID: {queue_id[:8]})"
        )


def _generate_local_script(worker_id: str, control_plane_url: str) -> str:
    """Generate a bash script for local Python installation"""
    return f"""#!/bin/bash
# Kubiya Agent Worker - Local Installation Script
# Generated: {datetime.utcnow().isoformat()}

set -e

echo "🚀 Setting up Kubiya Agent Worker..."
echo ""

# Configuration
WORKER_ID="{worker_id}"
CONTROL_PLANE_URL="{control_plane_url}"

# Check if KUBIYA_API_KEY is set
if [ -z "$KUBIYA_API_KEY" ]; then
    echo "❌ Error: KUBIYA_API_KEY environment variable is not set"
    echo "Please set it with: export KUBIYA_API_KEY=your-api-key"
    exit 1
fi

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Found Python $PYTHON_VERSION"

# Create directory
WORKER_DIR="$HOME/.kubiya/workers/$WORKER_ID"
mkdir -p "$WORKER_DIR"
cd "$WORKER_DIR"

echo "✓ Created worker directory: $WORKER_DIR"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install --quiet --upgrade pip
pip install --quiet \\
    temporalio>=1.5.0 \\
    httpx>=0.27.0 \\
    structlog>=24.1.0 \\
    psutil>=5.9.0 \\
    agno-sdk>=0.1.0 \\
    litellm>=1.35.0

echo "✓ Dependencies installed"

# Download worker script
echo "📥 Downloading worker script..."
curl -s -o worker.py https://raw.githubusercontent.com/kubiya-sandbox/orchestrator/main/agent-worker/worker.py

echo "✓ Worker script downloaded"

# Create systemd service file (optional)
cat > kubiya-worker.service <<EOF
[Unit]
Description=Kubiya Agent Worker
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKER_DIR
Environment="WORKER_ID=$WORKER_ID"
Environment="KUBIYA_API_KEY=$KUBIYA_API_KEY"
Environment="CONTROL_PLANE_URL=$CONTROL_PLANE_URL"
ExecStart=$WORKER_DIR/venv/bin/python $WORKER_DIR/worker.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✓ Systemd service file created (optional)"

# Create run script
cat > run.sh <<EOF
#!/bin/bash
cd "$WORKER_DIR"
source venv/bin/activate
export WORKER_ID="$WORKER_ID"
export KUBIYA_API_KEY="$KUBIYA_API_KEY"
export CONTROL_PLANE_URL="$CONTROL_PLANE_URL"
python worker.py
EOF

chmod +x run.sh

echo ""
echo "✅ Installation complete!"
echo ""
echo "To start the worker:"
echo "  cd $WORKER_DIR && ./run.sh"
echo ""
echo "Or to install as a systemd service:"
echo "  sudo cp $WORKER_DIR/kubiya-worker.service /etc/systemd/system/"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable kubiya-worker"
echo "  sudo systemctl start kubiya-worker"
echo ""
"""


def _generate_docker_script(worker_id: str, control_plane_url: str, queue_name: str, environment_name: str) -> str:
    """Generate Docker commands for running the worker"""
    return f"""# Kubiya Agent Worker - Docker Installation
# Generated: {datetime.utcnow().isoformat()}

# Configuration
WORKER_ID="{worker_id}"
CONTROL_PLANE_URL="{control_plane_url}"
QUEUE_NAME="{queue_name}"
ENVIRONMENT_NAME="{environment_name}"

# Make sure to set your API key
# export KUBIYA_API_KEY=your-api-key

# Run with Docker
docker run -d \\
  --name kubiya-worker-{queue_name}-{worker_id[:8]} \\
  --restart unless-stopped \\
  -e WORKER_ID="$WORKER_ID" \\
  -e KUBIYA_API_KEY="$KUBIYA_API_KEY" \\
  -e CONTROL_PLANE_URL="$CONTROL_PLANE_URL" \\
  -e LOG_LEVEL="INFO" \\
  kubiya/agent-worker:latest

# Check logs
# docker logs -f kubiya-worker-{queue_name}-{worker_id[:8]}

# Stop worker
# docker stop kubiya-worker-{queue_name}-{worker_id[:8]}

# Remove worker
# docker rm kubiya-worker-{queue_name}-{worker_id[:8]}

# Docker Compose (save as docker-compose.yml)
cat > docker-compose.yml <<EOF
version: '3.8'

services:
  worker:
    image: kubiya/agent-worker:latest
    container_name: kubiya-worker-{queue_name}
    restart: unless-stopped
    environment:
      - WORKER_ID={worker_id}
      - KUBIYA_API_KEY=${{KUBIYA_API_KEY}}
      - CONTROL_PLANE_URL={control_plane_url}
      - LOG_LEVEL=INFO
    healthcheck:
      test: ["CMD", "python", "-c", "import httpx; httpx.get('{control_plane_url}/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
EOF

# To use docker-compose:
# docker-compose up -d
"""


def _generate_kubernetes_script(worker_id: str, control_plane_url: str, queue_name: str, environment_name: str) -> str:
    """Generate Kubernetes deployment YAML"""
    return f"""# Kubiya Agent Worker - Kubernetes Deployment
# Generated: {datetime.utcnow().isoformat()}
#
# To deploy:
# 1. Create secret: kubectl create secret generic kubiya-worker-secret --from-literal=api-key=YOUR_API_KEY
# 2. Apply this file: kubectl apply -f kubiya-worker.yaml
#
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: kubiya-worker-{queue_name}-config
  labels:
    app: kubiya-worker
    queue: {queue_name}
    environment: {environment_name}
data:
  WORKER_ID: "{worker_id}"
  CONTROL_PLANE_URL: "{control_plane_url}"
  LOG_LEVEL: "INFO"

---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: kubiya-worker-{queue_name}
  labels:
    app: kubiya-worker
    queue: {queue_name}
    environment: {environment_name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: kubiya-worker
      queue: {queue_name}
  template:
    metadata:
      labels:
        app: kubiya-worker
        queue: {queue_name}
        environment: {environment_name}
    spec:
      containers:
      - name: worker
        image: kubiya/agent-worker:latest
        imagePullPolicy: Always
        envFrom:
        - configMapRef:
            name: kubiya-worker-{queue_name}-config
        env:
        - name: KUBIYA_API_KEY
          valueFrom:
            secretKeyRef:
              name: kubiya-worker-secret
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
      restartPolicy: Always

---
apiVersion: v1
kind: Service
metadata:
  name: kubiya-worker-{queue_name}
  labels:
    app: kubiya-worker
    queue: {queue_name}
spec:
  selector:
    app: kubiya-worker
    queue: {queue_name}
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: ClusterIP

---
# Optional: HorizontalPodAutoscaler
# apiVersion: autoscaling/v2
# kind: HorizontalPodAutoscaler
# metadata:
#   name: kubiya-worker-{queue_name}
# spec:
#   scaleTargetRef:
#     apiVersion: apps/v1
#     kind: Deployment
#     name: kubiya-worker-{queue_name}
#   minReplicas: 1
#   maxReplicas: 10
#   metrics:
#   - type: Resource
#     resource:
#       name: cpu
#       target:
#         type: Utilization
#         averageUtilization: 70
"""


class WorkerQueueCommandResponse(BaseModel):
    """Worker queue connection command"""
    queue_id: str
    command: str
    command_parts: dict
    can_register: bool
    queue_status: str
    active_workers: int
    max_workers: Optional[int]


class WorkerSystemInfo(BaseModel):
    """Worker system information"""
    hostname: Optional[str] = None
    platform: Optional[str] = None
    os_name: Optional[str] = None
    os_version: Optional[str] = None
    python_version: Optional[str] = None
    cli_version: Optional[str] = None
    docker_available: Optional[bool] = None
    docker_version: Optional[str] = None
    cpu_count: Optional[int] = None
    cpu_percent: Optional[float] = None
    memory_total: Optional[int] = None
    memory_used: Optional[int] = None
    memory_percent: Optional[float] = None
    disk_total: Optional[int] = None
    disk_used: Optional[int] = None
    disk_percent: Optional[float] = None
    uptime_seconds: Optional[float] = None


class WorkerDetail(BaseModel):
    """Individual worker details"""
    id: str
    worker_id: str
    status: str
    tasks_processed: int
    current_task_id: Optional[str]
    last_heartbeat: str
    registered_at: str
    system_info: Optional[WorkerSystemInfo] = None
    logs: Optional[List[str]] = None
    worker_metadata: dict


@router.get("/worker-queues/{queue_id}/workers", response_model=List[WorkerDetail])
async def list_queue_workers(
    queue_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    List all workers for a specific queue with detailed information.
    """
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Get active workers from Redis for this queue
        active_workers = await get_active_workers_from_redis(org_id, queue_id)

        # Get worker registration details from database (registered_at, worker_id)
        if active_workers:
            db_workers = (
                client.table("worker_heartbeats")
                .select("id, worker_id, registered_at")
                .eq("organization_id", org_id)
                .in_("id", list(active_workers.keys()))
                .execute()
            )
            db_workers_map = {w["id"]: w for w in (db_workers.data or [])}
        else:
            db_workers_map = {}

        workers = []
        for worker_id, heartbeat_data in active_workers.items():
            # Get DB data for registration time
            db_data = db_workers_map.get(worker_id, {})

            # Extract system info and logs from Redis heartbeat data
            metadata = heartbeat_data.get("metadata", {})
            system_info_data = heartbeat_data.get("system_info")
            logs = heartbeat_data.get("logs", [])

            system_info = WorkerSystemInfo(**system_info_data) if system_info_data else None

            workers.append(
                WorkerDetail(
                    id=worker_id,
                    worker_id=db_data.get("worker_id", worker_id),
                    status=heartbeat_data.get("status", "unknown"),
                    tasks_processed=heartbeat_data.get("tasks_processed", 0),
                    current_task_id=heartbeat_data.get("current_task_id"),
                    last_heartbeat=heartbeat_data.get("last_heartbeat", ""),
                    registered_at=db_data.get("registered_at", ""),
                    system_info=system_info,
                    logs=logs,
                    worker_metadata=metadata,
                )
            )

        # Sort by last_heartbeat desc
        workers.sort(key=lambda w: w.last_heartbeat, reverse=True)

        logger.info(
            "queue_workers_listed",
            queue_id=queue_id,
            worker_count=len(workers),
            org_id=org_id,
        )

        return workers

    except HTTPException:
        raise
    except Exception as e:
        logger.error("queue_workers_list_failed", error=str(e), queue_id=queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list queue workers: {str(e)}"
        )


@router.get("/worker-queues/{queue_id}/worker-command", response_model=WorkerQueueCommandResponse)
async def get_worker_queue_command(
    queue_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Get the worker registration command for a specific worker queue.

    Returns the kubiya worker start command with the queue ID that users
    should run to start a worker for this specific queue.
    """
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Get worker queue
        result = (
            client.table("worker_queues")
            .select("*")
            .eq("id", queue_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Worker queue not found")

        queue = result.data
        queue_status = queue.get("status", "unknown")

        # Check if queue is active
        can_register = queue_status == "active"

        # Get active workers from Redis for this specific queue
        active_workers_dict = await get_active_workers_from_redis(org_id, queue_id)
        active_workers = len(active_workers_dict)

        # Build command
        command = f"kubiya worker start --queue-id {queue_id}"

        command_parts = {
            "binary": "kubiya",
            "subcommand": "worker start",
            "flags": {
                "--queue-id": queue_id,
            },
        }

        logger.info(
            "worker_queue_command_retrieved",
            queue_id=queue_id,
            can_register=can_register,
            status=queue_status,
            active_workers=active_workers,
            org_id=org_id,
        )

        return WorkerQueueCommandResponse(
            queue_id=queue_id,
            command=command,
            command_parts=command_parts,
            can_register=can_register,
            queue_status=queue_status,
            active_workers=active_workers,
            max_workers=queue.get("max_workers"),
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("worker_queue_command_failed", error=str(e), queue_id=queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get worker queue command: {str(e)}"
        )


def _generate_openshift_script(worker_id: str, control_plane_url: str, queue_name: str, environment_name: str) -> str:
    """Generate OpenShift deployment YAML"""
    return f"""# Kubiya Agent Worker - OpenShift Deployment
# Generated: {datetime.utcnow().isoformat()}
#
# To deploy:
# 1. Create secret: oc create secret generic kubiya-worker-secret --from-literal=api-key=YOUR_API_KEY
# 2. Apply this file: oc apply -f kubiya-worker.yaml
#
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: kubiya-worker-{queue_name}-config
  labels:
    app: kubiya-worker
    queue: {queue_name}
    environment: {environment_name}
data:
  WORKER_ID: "{worker_id}"
  CONTROL_PLANE_URL: "{control_plane_url}"
  LOG_LEVEL: "INFO"

---
apiVersion: apps.openshift.io/v1
kind: DeploymentConfig
metadata:
  name: kubiya-worker-{queue_name}
  labels:
    app: kubiya-worker
    queue: {queue_name}
    environment: {environment_name}
spec:
  replicas: 1
  selector:
    app: kubiya-worker
    queue: {queue_name}
  template:
    metadata:
      labels:
        app: kubiya-worker
        queue: {queue_name}
        environment: {environment_name}
    spec:
      containers:
      - name: worker
        image: kubiya/agent-worker:latest
        imagePullPolicy: Always
        envFrom:
        - configMapRef:
            name: kubiya-worker-{queue_name}-config
        env:
        - name: KUBIYA_API_KEY
          valueFrom:
            secretKeyRef:
              name: kubiya-worker-secret
              key: api-key
        resources:
          requests:
            memory: "512Mi"
            cpu: "250m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
          timeoutSeconds: 10
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 10
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
      restartPolicy: Always
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
  triggers:
  - type: ConfigChange
  - type: ImageChange
    imageChangeParams:
      automatic: true
      containerNames:
      - worker
      from:
        kind: ImageStreamTag
        name: agent-worker:latest

---
apiVersion: v1
kind: Service
metadata:
  name: kubiya-worker-{queue_name}
  labels:
    app: kubiya-worker
    queue: {queue_name}
spec:
  selector:
    app: kubiya-worker
    queue: {queue_name}
  ports:
  - protocol: TCP
    port: 8080
    targetPort: 8080
  type: ClusterIP

---
# Optional: Route to expose the service
# apiVersion: route.openshift.io/v1
# kind: Route
# metadata:
#   name: kubiya-worker-{queue_name}
#   labels:
#     app: kubiya-worker
#     queue: {queue_name}
# spec:
#   to:
#     kind: Service
#     name: kubiya-worker-{queue_name}
#   port:
#     targetPort: 8080
#   tls:
#     termination: edge
#     insecureEdgeTerminationPolicy: Redirect
"""
