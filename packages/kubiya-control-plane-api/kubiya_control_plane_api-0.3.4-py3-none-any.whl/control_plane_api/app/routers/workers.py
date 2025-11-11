"""Workers endpoint - shows registered Temporal workers and handles worker registration"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime
import structlog
import uuid
import json

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.temporal_client import get_temporal_client
from control_plane_api.app.lib.supabase import get_supabase
from control_plane_api.app.lib.redis_client import get_redis_client

logger = structlog.get_logger()

router = APIRouter()


class WorkerInfo(BaseModel):
    """Worker information"""
    identity: str
    last_access_time: str | None
    rate_per_second: float | None


class TaskQueueInfo(BaseModel):
    """Task queue with worker information"""
    task_queue: str
    organization_id: str
    runner_name: str
    workers: List[WorkerInfo]
    worker_count: int
    approximate_backlog_count: int | None


@router.get("", response_model=List[TaskQueueInfo])
async def list_workers(
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    List registered Temporal workers for the organization.

    This queries Temporal to get all task queues for the organization
    and returns information about registered workers on each queue.

    Task queue naming convention: {organization_id}.{runner_name}
    """
    try:
        temporal_client = await get_temporal_client()
        org_id = organization["id"]

        # Get runners from Kubiya API to know which task queues to check
        from control_plane_api.app.lib.kubiya_client import get_kubiya_client
        kubiya_client = get_kubiya_client()
        token = request.state.kubiya_token

        try:
            runners = await kubiya_client.get_runners(token, org_id)
        except Exception as e:
            logger.warning(
                "failed_to_fetch_kubiya_runners",
                error=str(e),
                org_id=org_id
            )
            # If we can't get runners from Kubiya, fall back to checking common ones
            runners = [{"name": "default"}]

        environments_info = []

        for runner in runners:
            # Runner might be a dict or a string
            if isinstance(runner, dict):
                runner_name = runner.get("name", "default")
            else:
                runner_name = str(runner) if runner else "default"

            task_queue = f"{org_id}.{runner_name}"

            try:
                # Describe the task queue to get worker information
                desc = await temporal_client.describe_task_queue(
                    task_queue=task_queue,
                    task_queue_type=1,  # TaskQueueType.WORKFLOW
                )

                workers = []
                approximate_backlog = None

                # Extract worker information from pollers
                if desc.pollers:
                    for poller in desc.pollers:
                        worker_info = WorkerInfo(
                            identity=poller.identity,
                            last_access_time=poller.last_access_time.isoformat() if poller.last_access_time else None,
                            rate_per_second=poller.rate_per_second if hasattr(poller, 'rate_per_second') else None,
                        )
                        workers.append(worker_info)

                # Get approximate backlog count if available
                if hasattr(desc, 'approximate_backlog_count'):
                    approximate_backlog = desc.approximate_backlog_count

                task_queue_info = TaskQueueInfo(
                    task_queue=task_queue,
                    organization_id=org_id,
                    runner_name=runner_name,
                    workers=workers,
                    worker_count=len(workers),
                    approximate_backlog_count=approximate_backlog,
                )

                environments_info.append(task_queue_info)

                logger.info(
                    "task_queue_described",
                    task_queue=task_queue,
                    worker_count=len(workers),
                    org_id=org_id,
                )

            except Exception as e:
                # Task queue might not exist yet if no worker has registered
                logger.debug(
                    "task_queue_not_found",
                    task_queue=task_queue,
                    error=str(e),
                    org_id=org_id,
                )
                # Add empty task queue info
                task_queue_info = TaskQueueInfo(
                    task_queue=task_queue,
                    organization_id=org_id,
                    runner_name=runner_name,
                    workers=[],
                    worker_count=0,
                    approximate_backlog_count=None,
                )
                environments_info.append(task_queue_info)

        logger.info(
            "workers_listed",
            org_id=org_id,
            task_queue_count=len(environments_info),
            total_workers=sum(tq.worker_count for tq in environments_info),
        )

        return environments_info

    except Exception as e:
        logger.error(
            "workers_list_failed",
            error=str(e),
            org_id=organization["id"]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list workers: {str(e)}"
        )


@router.get("/{runner_name}", response_model=TaskQueueInfo)
async def get_workers_for_runner(
    runner_name: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Get worker information for a specific runner.

    Args:
        runner_name: The runner name (e.g., "default", "production-runner")
    """
    try:
        temporal_client = await get_temporal_client()
        org_id = organization["id"]
        task_queue = f"{org_id}.{runner_name}"

        try:
            # Describe the task queue
            desc = await temporal_client.describe_task_queue(
                task_queue=task_queue,
                task_queue_type=1,  # TaskQueueType.WORKFLOW
            )

            workers = []
            approximate_backlog = None

            # Extract worker information
            if desc.pollers:
                for poller in desc.pollers:
                    worker_info = WorkerInfo(
                        identity=poller.identity,
                        last_access_time=poller.last_access_time.isoformat() if poller.last_access_time else None,
                        rate_per_second=poller.rate_per_second if hasattr(poller, 'rate_per_second') else None,
                    )
                    workers.append(worker_info)

            if hasattr(desc, 'approximate_backlog_count'):
                approximate_backlog = desc.approximate_backlog_count

            task_queue_info = TaskQueueInfo(
                task_queue=task_queue,
                organization_id=org_id,
                runner_name=runner_name,
                workers=workers,
                worker_count=len(workers),
                approximate_backlog_count=approximate_backlog,
            )

            logger.info(
                "workers_fetched_for_runner",
                runner_name=runner_name,
                worker_count=len(workers),
                org_id=org_id,
            )

            return task_queue_info

        except Exception as e:
            logger.warning(
                "task_queue_not_found",
                task_queue=task_queue,
                error=str(e),
                org_id=org_id,
            )
            # Return empty worker info if task queue doesn't exist
            return TaskQueueInfo(
                task_queue=task_queue,
                organization_id=org_id,
                runner_name=runner_name,
                workers=[],
                worker_count=0,
                approximate_backlog_count=None,
            )

    except Exception as e:
        logger.error(
            "workers_fetch_failed",
            error=str(e),
            runner_name=runner_name,
            org_id=organization["id"]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch workers: {str(e)}"
        )


# Worker Registration for Decoupled Architecture


class WorkerRegistrationRequest(BaseModel):
    """Worker registration request"""
    environment_name: str  # Task queue / environment name worker wants to join
    hostname: Optional[str] = None
    worker_metadata: Dict[str, Any] = {}


class WorkerRegistrationResponse(BaseModel):
    """Worker registration response with all config needed"""
    worker_id: str  # Unique worker ID
    worker_token: str  # Token for this worker (from environment)
    environment_name: str  # Task queue name (format: org_id.environment)
    temporal_namespace: str
    temporal_host: str
    temporal_api_key: str
    organization_id: str
    control_plane_url: str


class WorkerHeartbeatRequest(BaseModel):
    """Worker heartbeat request"""
    worker_id: str
    environment_name: str
    status: str = "active"  # active, idle, busy
    tasks_processed: int = 0
    current_task_id: Optional[str] = None
    worker_metadata: Dict[str, Any] = {}


@router.post("/register", response_model=WorkerRegistrationResponse)
async def register_worker(
    registration: WorkerRegistrationRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Register a new worker with the control plane.

    This endpoint is called by workers on startup to get their configuration.
    The worker authenticates using KUBIYA_API_KEY (same auth as other API calls).

    Returns:
        All configuration needed for worker to connect to Temporal and operate:
        - worker_id: Unique ID for this worker instance
        - worker_token: Environment's worker token
        - environment_name: Formatted task queue name (org_id.environment)
        - temporal_namespace, temporal_host, temporal_api_key: Temporal Cloud config
        - organization_id: Organization ID
        - control_plane_url: URL to send heartbeats
    """
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Look up the environment by name
        env_result = (
            client.table("environments")
            .select("*")
            .eq("organization_id", org_id)
            .eq("name", registration.environment_name)
            .execute()
        )

        # If environment doesn't exist, create it
        if not env_result.data or len(env_result.data) == 0:
            logger.info(
                "creating_environment_for_worker",
                environment_name=registration.environment_name,
                org_id=org_id,
            )

            # Generate worker token for this environment (UUID format)
            worker_token = str(uuid.uuid4())

            # Create the environment
            new_env = {
                "id": str(uuid.uuid4()),
                "organization_id": org_id,
                "name": registration.environment_name,
                "worker_token": worker_token,
                "status": "active",  # Mark as active immediately
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            env_create_result = (
                client.table("environments")
                .insert(new_env)
                .execute()
            )

            environment = env_create_result.data[0]

            logger.info(
                "environment_created_for_worker",
                environment_name=registration.environment_name,
                environment_id=environment["id"],
                org_id=org_id,
            )
        else:
            environment = env_result.data[0]

        # Check if environment is ready
        if environment.get("status") not in ["ready", "active"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Environment is not ready (status: {environment.get('status')}). "
                       f"Please wait for provisioning to complete."
            )

        # TEMPORARY: Skip provisioning and use fixed namespace + admin API key
        # Get temporal namespace for this organization
        import os

        # Use fixed namespace for testing
        namespace = {
            "namespace_name": "agent-control-plane.lpagu",
            "api_key_encrypted": os.getenv("TEMPORAL_CLOUD_ADMIN_TOKEN", ""),
            "status": "ready"
        }

        logger.info(
            "using_fixed_namespace_for_testing",
            namespace_name=namespace["namespace_name"],
            org_id=org_id,
        )

        # Generate worker ID
        worker_id = str(uuid.uuid4())

        # Create worker record in database
        worker_record = {
            "id": worker_id,  # Use id as primary key
            "worker_id": worker_id,  # Also set worker_id (has NOT NULL constraint)
            "organization_id": org_id,
            "environment_name": registration.environment_name,
            "worker_token": environment.get("worker_token"),
            "hostname": registration.hostname,
            "worker_metadata": registration.worker_metadata,
            "status": "active",
            "tasks_processed": 0,
            "registered_at": datetime.utcnow().isoformat(),
            "last_heartbeat": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        client.table("worker_heartbeats").insert(worker_record).execute()

        # Format task queue name: org_id.environment_name
        task_queue_name = f"{org_id}.{registration.environment_name}"

        # Get Temporal Cloud configuration
        import os
        temporal_host = os.getenv("TEMPORAL_HOST", "us-east-1.aws.api.temporal.io:7233")

        # Decrypt API key from namespace (TODO: implement proper decryption)
        temporal_api_key = namespace.get("api_key_encrypted", "")

        # Get control plane URL from environment or construct from request
        control_plane_url = os.getenv("CONTROL_PLANE_URL")
        if not control_plane_url:
            # Construct from request if not set
            control_plane_url = f"{request.url.scheme}://{request.url.netloc}"

        logger.info(
            "worker_registered",
            worker_id=worker_id,
            environment_name=registration.environment_name,
            task_queue=task_queue_name,
            org_id=org_id,
        )

        return WorkerRegistrationResponse(
            worker_id=worker_id,
            worker_token=environment.get("worker_token"),
            environment_name=task_queue_name,  # Return formatted name
            temporal_namespace=namespace.get("namespace_name"),
            temporal_host=temporal_host,
            temporal_api_key=temporal_api_key,
            organization_id=org_id,
            control_plane_url=control_plane_url,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "worker_registration_failed",
            error=str(e),
            environment_name=registration.environment_name,
            org_id=organization["id"]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to register worker: {str(e)}"
        )


@router.post("/heartbeat", status_code=status.HTTP_204_NO_CONTENT)
async def worker_heartbeat(
    heartbeat: WorkerHeartbeatRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Receive heartbeat from a worker.

    OPTIMIZATION: Uses Redis for scalable heartbeat storage instead of database.
    Database writes are expensive and heartbeats happen every 30s per worker.

    Workers should call this endpoint periodically (e.g., every 30 seconds) to:
    - Confirm they're still alive
    - Update their status (active, idle, busy)
    - Report tasks processed
    - Update metadata
    """
    try:
        org_id = organization["id"]
        redis_client = get_redis_client()

        if not redis_client:
            # Redis not available - log warning but don't fail (graceful degradation)
            logger.warning(
                "worker_heartbeat_redis_unavailable",
                worker_id=heartbeat.worker_id,
                org_id=org_id,
            )
            return None

        # Build heartbeat data for Redis
        heartbeat_data = {
            "worker_id": heartbeat.worker_id,
            "organization_id": org_id,
            "environment_name": heartbeat.environment_name,
            "status": heartbeat.status,
            "tasks_processed": heartbeat.tasks_processed,
            "current_task_id": heartbeat.current_task_id,
            "last_heartbeat": datetime.utcnow().isoformat(),
            "metadata": heartbeat.worker_metadata,
        }

        # Store in Redis with 5-minute TTL (if worker crashes, heartbeat expires)
        redis_key = f"worker:{heartbeat.worker_id}:heartbeat"
        await redis_client.set(redis_key, json.dumps(heartbeat_data), ex=300)

        logger.debug(
            "worker_heartbeat_received",
            worker_id=heartbeat.worker_id,
            status=heartbeat.status,
            environment_name=heartbeat.environment_name,
            org_id=org_id,
        )

        return None

    except Exception as e:
        logger.error(
            "worker_heartbeat_failed",
            error=str(e),
            worker_id=heartbeat.worker_id,
            org_id=organization["id"]
        )
        # Don't fail the worker if heartbeat fails - graceful degradation
        return None


# Worker ID-based endpoints (new architecture)


class WorkerStartRequest(BaseModel):
    """Request to start a worker and fetch its config"""
    system_info: Dict[str, Any] = {}


class WorkerConfigResponse(BaseModel):
    """Worker configuration response"""
    worker_id: str
    worker_queue_name: str
    environment_name: str
    task_queue_name: str  # Full: org.env.worker_queue
    temporal_namespace: str
    temporal_host: str
    temporal_api_key: str
    organization_id: str
    control_plane_url: str
    heartbeat_interval: int = 30
    # LiteLLM configuration
    litellm_api_url: str
    litellm_api_key: str


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
    memory_total: Optional[int] = None  # bytes
    memory_used: Optional[int] = None   # bytes
    memory_percent: Optional[float] = None
    disk_total: Optional[int] = None    # bytes
    disk_used: Optional[int] = None     # bytes
    disk_percent: Optional[float] = None
    uptime_seconds: Optional[float] = None


class WorkerHeartbeatSimple(BaseModel):
    """Simplified heartbeat request (worker_id in URL)"""
    status: str = "active"
    tasks_processed: int = 0
    current_task_id: Optional[str] = None
    worker_metadata: Dict[str, Any] = {}
    system_info: Optional[WorkerSystemInfo] = None
    logs: Optional[List[str]] = None  # Recent log lines since last heartbeat


@router.post("/{worker_id}/start", response_model=WorkerConfigResponse)
async def start_worker(
    worker_id: str,
    start_request: WorkerStartRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Start a worker and fetch its configuration.

    This endpoint is called by workers on startup with just worker_id and API key.
    It returns all necessary configuration for the worker to connect to Temporal.

    Args:
        worker_id: Worker ID (UUID created in UI)
        start_request: System information from worker

    Returns:
        Complete worker configuration including Temporal credentials
    """
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Look up worker in database
        worker_result = (
            client.table("worker_heartbeats")
            .select("*")
            .eq("id", worker_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if not worker_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Worker '{worker_id}' not found"
            )

        worker = worker_result.data

        # Get worker queue separately
        if not worker.get("worker_queue_id"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Worker has no queue assigned"
            )

        queue_result = (
            client.table("worker_queues")
            .select("*")
            .eq("id", worker["worker_queue_id"])
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if not queue_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Worker queue not found"
            )

        worker_queue = queue_result.data
        worker_queue_name = worker_queue["name"]

        # Get environment separately
        environment_name = "default"
        if worker_queue.get("environment_id"):
            env_result = (
                client.table("environments")
                .select("name")
                .eq("id", worker_queue["environment_id"])
                .eq("organization_id", org_id)
                .maybe_single()
                .execute()
            )
            if env_result.data:
                environment_name = env_result.data["name"]

        # TEMPORARY: Skip database lookup and use fixed namespace + admin API key
        import os

        # Use fixed namespace for testing
        namespace = {
            "namespace_name": "agent-control-plane.lpagu",
            "api_key_encrypted": os.getenv("TEMPORAL_CLOUD_ADMIN_TOKEN", ""),
            "status": "ready"
        }

        logger.info(
            "using_fixed_namespace_for_testing",
            namespace_name=namespace["namespace_name"],
            worker_id=worker_id,
            org_id=org_id,
        )

        # Update worker with system info and mark as starting
        update_data = {
            "worker_metadata": {
                **worker.get("worker_metadata", {}),
                **start_request.system_info,
                "last_start": datetime.utcnow().isoformat(),
            },
            "status": "active",
            "last_heartbeat": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        }

        client.table("worker_heartbeats").update(update_data).eq("id", worker_id).execute()

        # Build full task queue name
        task_queue_name = f"{org_id}.{environment_name}.{worker_queue_name}"

        # Get Temporal Cloud configuration
        import os
        temporal_host = os.getenv("TEMPORAL_HOST", "us-east-1.aws.api.temporal.io:7233")
        temporal_api_key = namespace.get("api_key_encrypted", "")

        # Get control plane URL
        control_plane_url = os.getenv("CONTROL_PLANE_URL")
        if not control_plane_url:
            control_plane_url = f"{request.url.scheme}://{request.url.netloc}"

        # Get LiteLLM configuration from environment
        litellm_api_url = os.getenv("LITELLM_API_URL", "https://api.openai.com/v1")
        litellm_api_key = os.getenv("LITELLM_API_KEY", "")

        logger.info(
            "worker_config_fetched",
            worker_id=worker_id,
            task_queue=task_queue_name,
            environment=environment_name,
            worker_queue=worker_queue_name,
            org_id=org_id,
        )

        return WorkerConfigResponse(
            worker_id=worker_id,
            worker_queue_name=worker_queue_name,
            environment_name=environment_name,
            task_queue_name=task_queue_name,
            temporal_namespace=namespace.get("namespace_name"),
            temporal_host=temporal_host,
            temporal_api_key=temporal_api_key,
            organization_id=org_id,
            control_plane_url=control_plane_url,
            heartbeat_interval=worker_queue.get("heartbeat_interval", 30),
            litellm_api_url=litellm_api_url,
            litellm_api_key=litellm_api_key,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "worker_start_failed",
            error=str(e),
            worker_id=worker_id,
            org_id=organization.get("id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start worker: {str(e)}"
        )


@router.post("/{worker_id}/heartbeat", status_code=status.HTTP_204_NO_CONTENT)
async def worker_heartbeat_simple(
    worker_id: str,
    heartbeat: WorkerHeartbeatSimple,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Receive heartbeat from a worker (simplified version with worker_id in URL).

    OPTIMIZATION: Uses Redis for scalable heartbeat storage instead of database.
    Database writes are expensive and heartbeats happen every 30s per worker.
    Redis provides sub-millisecond writes and automatic TTL expiration.

    Args:
        worker_id: Worker ID (UUID)
        heartbeat: Heartbeat data
    """
    try:
        org_id = organization["id"]
        redis_client = get_redis_client()

        if not redis_client:
            # Redis not available - log warning but don't fail (graceful degradation)
            logger.warning(
                "worker_heartbeat_redis_unavailable",
                worker_id=worker_id,
                org_id=org_id,
            )
            return None

        # Build heartbeat data for Redis
        heartbeat_data = {
            "worker_id": worker_id,
            "organization_id": org_id,
            "status": heartbeat.status,
            "tasks_processed": heartbeat.tasks_processed,
            "current_task_id": heartbeat.current_task_id,
            "last_heartbeat": datetime.utcnow().isoformat(),
            "metadata": heartbeat.worker_metadata,
        }

        if heartbeat.system_info:
            heartbeat_data["system_info"] = heartbeat.system_info.dict(exclude_none=True)

        # Handle logs - fetch from Redis and append new logs
        redis_key = f"worker:{worker_id}:heartbeat"
        if heartbeat.logs:
            try:
                # Get existing heartbeat data to retrieve logs
                existing_data = await redis_client.get(redis_key)
                if existing_data:
                    existing_heartbeat = json.loads(existing_data)
                    existing_logs = existing_heartbeat.get("logs", [])
                    all_logs = existing_logs + heartbeat.logs
                    heartbeat_data["logs"] = all_logs[-100:]  # Keep last 100 lines
                else:
                    heartbeat_data["logs"] = heartbeat.logs[-100:]
            except Exception as log_error:
                logger.warning("heartbeat_log_merge_failed", error=str(log_error))
                heartbeat_data["logs"] = heartbeat.logs[-100:]

        # Store in Redis with 5-minute TTL (if worker crashes, heartbeat expires)
        # TTL is 10x the heartbeat interval (30s * 10 = 300s) for safety
        await redis_client.set(redis_key, json.dumps(heartbeat_data), ex=300)

        logger.debug(
            "worker_heartbeat_received",
            worker_id=worker_id,
            status=heartbeat.status,
            org_id=org_id,
        )

        return None

    except Exception as e:
        logger.error(
            "worker_heartbeat_failed",
            error=str(e),
            worker_id=worker_id,
            org_id=organization.get("id")
        )
        # Don't fail the worker if heartbeat fails - graceful degradation
        return None


class WorkerDisconnectRequest(BaseModel):
    """Worker disconnect request"""
    reason: str = "shutdown"  # shutdown, error, crash, etc.
    exit_code: Optional[int] = None
    error_message: Optional[str] = None


@router.post("/{worker_id}/disconnect", status_code=status.HTTP_204_NO_CONTENT)
async def worker_disconnect(
    worker_id: str,
    disconnect: WorkerDisconnectRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Mark a worker as disconnected/offline.

    This endpoint is called by workers when they:
    - Shut down gracefully (Ctrl+C)
    - Exit due to an error
    - Crash unexpectedly (via atexit handler)

    Args:
        worker_id: Worker ID (UUID)
        disconnect: Disconnect details (reason, exit code, error)
    """
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Update worker status to disconnected in database
        update_data = {
            "status": "disconnected",
            "last_heartbeat": datetime.utcnow().isoformat(),
            "worker_metadata": {
                "disconnect_reason": disconnect.reason,
                "disconnect_time": datetime.utcnow().isoformat(),
                "exit_code": disconnect.exit_code,
                "error_message": disconnect.error_message,
            },
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = (
            client.table("worker_heartbeats")
            .update(update_data)
            .eq("id", worker_id)
            .eq("organization_id", org_id)
            .execute()
        )

        if not result.data:
            logger.warning(
                "worker_disconnect_not_found",
                worker_id=worker_id,
                org_id=org_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Worker not found"
            )

        # IMPORTANT: Also remove from Redis immediately so UI updates instantly
        redis_client = get_redis_client()
        if redis_client:
            redis_key = f"worker:{worker_id}:heartbeat"
            try:
                # Delete the heartbeat key from Redis
                await redis_client.delete(redis_key)
                logger.info(
                    "worker_removed_from_redis",
                    worker_id=worker_id,
                    redis_key=redis_key
                )
            except Exception as redis_error:
                # Log but don't fail the disconnect
                logger.warning(
                    "redis_delete_failed",
                    error=str(redis_error),
                    worker_id=worker_id
                )

        logger.info(
            "worker_disconnected",
            worker_id=worker_id,
            reason=disconnect.reason,
            exit_code=disconnect.exit_code,
            org_id=org_id,
        )

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "worker_disconnect_failed",
            error=str(e),
            worker_id=worker_id,
            org_id=organization.get("id")
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process disconnect: {str(e)}"
        )
