"""
Task Queues router - Worker queue management for routing work to specific workers.

This router handles task queue CRUD operations and tracks worker availability.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import uuid
import os

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase
from control_plane_api.app.lib.temporal_client import get_temporal_client

logger = structlog.get_logger()

router = APIRouter()


# Pydantic schemas
class TaskQueueCreate(BaseModel):
    name: str = Field(..., description="Queue name (e.g., default, high-priority)", min_length=2, max_length=100)
    display_name: str | None = Field(None, description="User-friendly display name")
    description: str | None = Field(None, description="Queue description")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization")
    settings: dict = Field(default_factory=dict, description="Queue settings")
    priority: int | None = Field(None, ge=1, le=10, description="Priority level (1-10)")
    policy_ids: List[str] = Field(default_factory=list, description="OPA policy IDs")


class TaskQueueUpdate(BaseModel):
    name: str | None = None
    display_name: str | None = None
    description: str | None = None
    tags: List[str] | None = None
    settings: dict | None = None
    status: str | None = None
    priority: int | None = Field(None, ge=1, le=10)
    policy_ids: List[str] | None = None


class TaskQueueResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    display_name: str | None
    description: str | None
    tags: List[str]
    settings: dict
    status: str
    priority: int | None = None
    policy_ids: List[str] = []
    created_at: str
    updated_at: str
    created_by: str | None

    # Temporal Cloud provisioning fields
    worker_token: str | None = None  # UUID token for worker registration
    provisioning_workflow_id: str | None = None  # Temporal workflow ID
    provisioned_at: str | None = None
    error_message: str | None = None
    temporal_namespace_id: str | None = None

    # Worker metrics
    active_workers: int = 0
    idle_workers: int = 0
    busy_workers: int = 0


class WorkerHeartbeatResponse(BaseModel):
    id: str
    organization_id: str
    task_queue_name: str
    worker_id: str
    hostname: str | None
    worker_metadata: dict
    last_heartbeat: str
    status: str
    tasks_processed: int
    current_task_id: str | None
    registered_at: str
    updated_at: str


def ensure_default_queue(organization: dict) -> Optional[dict]:
    """
    Ensure the organization has a default task queue.
    Creates one if it doesn't exist.

    Returns the default queue or None if creation failed.
    """
    try:
        client = get_supabase()

        # Check if default queue exists
        existing = (
            client.table("environments")
            .select("*")
            .eq("organization_id", organization["id"])
            .eq("name", "default")
            .execute()
        )

        if existing.data:
            return existing.data[0]

        # Create default queue
        queue_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        default_queue = {
            "id": queue_id,
            "organization_id": organization["id"],
            "name": "default",
            "display_name": "Default Queue",
            "description": "Default task queue for all workers",
            "tags": [],
            "settings": {},
            "status": "active",
            "created_at": now,
            "updated_at": now,
            "created_by": organization.get("user_id"),
        }

        result = client.table("environments").insert(default_queue).execute()

        if result.data:
            logger.info(
                "default_queue_created",
                queue_id=queue_id,
                org_id=organization["id"],
            )
            return result.data[0]

        return None

    except Exception as e:
        logger.error("ensure_default_queue_failed", error=str(e), org_id=organization.get("id"))
        return None


@router.post("", response_model=TaskQueueResponse, status_code=status.HTTP_201_CREATED)
async def create_task_queue(
    queue_data: TaskQueueCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Create a new task queue.

    If this is the first task queue for the organization, it will trigger
    Temporal Cloud namespace provisioning workflow.
    """
    try:
        client = get_supabase()

        # Check if queue name already exists for this organization
        existing = (
            client.table("environments")
            .select("id")
            .eq("organization_id", organization["id"])
            .eq("name", queue_data.name)
            .execute()
        )

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Task queue with name '{queue_data.name}' already exists"
            )

        # Check if this is the first task queue for this org
        all_queues = (
            client.table("environments")
            .select("id")
            .eq("organization_id", organization["id"])
            .execute()
        )
        is_first_queue = len(all_queues.data or []) == 0

        # Check if namespace already exists
        namespace_result = (
            client.table("temporal_namespaces")
            .select("*")
            .eq("organization_id", organization["id"])
            .execute()
        )
        has_namespace = bool(namespace_result.data)
        needs_provisioning = is_first_queue and not has_namespace

        queue_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Set initial status
        initial_status = "provisioning" if needs_provisioning else "ready"

        queue_record = {
            "id": queue_id,
            "organization_id": organization["id"],
            "name": queue_data.name,
            "display_name": queue_data.display_name or queue_data.name,
            "description": queue_data.description,
            "tags": queue_data.tags,
            "settings": queue_data.settings,
            "status": initial_status,
            "created_at": now,
            "updated_at": now,
            "created_by": organization.get("user_id"),
            "worker_token": str(uuid.uuid4()),  # Generate worker token
        }

        result = client.table("environments").insert(queue_record).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create task queue"
            )

        queue = result.data[0]

        # Trigger namespace provisioning workflow if needed
        if needs_provisioning:
            try:
                from control_plane_api.app.workflows.namespace_provisioning import (
                    ProvisionTemporalNamespaceWorkflow,
                    ProvisionNamespaceInput,
                )

                temporal_client = await get_temporal_client()
                account_id = os.environ.get("TEMPORAL_CLOUD_ACCOUNT_ID", "default-account")

                workflow_input = ProvisionNamespaceInput(
                    organization_id=organization["id"],
                    organization_name=organization.get("name", organization["id"]),
                    task_queue_id=queue_id,
                    account_id=account_id,
                    region=os.environ.get("TEMPORAL_CLOUD_REGION", "aws-us-east-1"),
                )

                # Start provisioning workflow on control plane's task queue
                workflow_handle = await temporal_client.start_workflow(
                    ProvisionTemporalNamespaceWorkflow.run,
                    workflow_input,
                    id=f"provision-namespace-{organization['id']}",
                    task_queue="agent-control-plane",  # Control plane's task queue
                )

                # Update queue with workflow ID
                client.table("environments").update({
                    "provisioning_workflow_id": workflow_handle.id,
                    "updated_at": datetime.utcnow().isoformat(),
                }).eq("id", queue_id).execute()

                queue["provisioning_workflow_id"] = workflow_handle.id

                logger.info(
                    "namespace_provisioning_workflow_started",
                    workflow_id=workflow_handle.id,
                    queue_id=queue_id,
                    org_id=organization["id"],
                )
            except Exception as e:
                logger.error(
                    "failed_to_start_provisioning_workflow",
                    error=str(e),
                    queue_id=queue_id,
                    org_id=organization["id"],
                )
                # Update queue status to error
                client.table("environments").update({
                    "status": "error",
                    "error_message": f"Failed to start provisioning: {str(e)}",
                    "updated_at": datetime.utcnow().isoformat(),
                }).eq("id", queue_id).execute()
                queue["status"] = "error"
                queue["error_message"] = f"Failed to start provisioning: {str(e)}"

        logger.info(
            "task_queue_created",
            queue_id=queue_id,
            queue_name=queue["name"],
            org_id=organization["id"],
            needs_provisioning=needs_provisioning,
        )

        return TaskQueueResponse(
            **queue,
            active_workers=0,
            idle_workers=0,
            busy_workers=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("task_queue_creation_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create task queue: {str(e)}"
        )


@router.get("", response_model=List[TaskQueueResponse])
async def list_task_queues(
    request: Request,
    status_filter: str | None = None,
    organization: dict = Depends(get_current_organization),
):
    """List all task queues in the organization"""
    try:
        client = get_supabase()

        # Ensure default queue exists
        ensure_default_queue(organization)

        # Query queues
        query = client.table("environments").select("*").eq("organization_id", organization["id"])

        if status_filter:
            query = query.eq("status", status_filter)

        query = query.order("created_at", desc=False)
        result = query.execute()

        if not result.data:
            return []

        # Note: Worker stats are now tracked at worker_queue level, not environment level
        # For backward compatibility, we return 0 for environment-level worker counts
        # Use worker_queues endpoints for detailed worker information
        queues = []
        for queue in result.data:
            queues.append(
                TaskQueueResponse(
                    **queue,
                    active_workers=0,
                    idle_workers=0,
                    busy_workers=0,
                )
            )

        logger.info(
            "task_queues_listed",
            count=len(queues),
            org_id=organization["id"],
        )

        return queues

    except Exception as e:
        logger.error("task_queues_list_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list task queues: {str(e)}"
        )


@router.get("/{queue_id}", response_model=TaskQueueResponse)
async def get_task_queue(
    queue_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get a specific task queue by ID"""
    try:
        client = get_supabase()

        result = (
            client.table("environments")
            .select("*")
            .eq("id", queue_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Task queue not found")

        queue = result.data

        # Note: Worker stats are now tracked at worker_queue level
        # Return 0 for environment-level worker counts
        return TaskQueueResponse(
            **queue,
            active_workers=0,
            idle_workers=0,
            busy_workers=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("task_queue_get_failed", error=str(e), queue_id=queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task queue: {str(e)}"
        )


@router.patch("/{queue_id}", response_model=TaskQueueResponse)
async def update_task_queue(
    queue_id: str,
    queue_data: TaskQueueUpdate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Update a task queue"""
    try:
        client = get_supabase()

        # Check if queue exists
        existing = (
            client.table("environments")
            .select("id")
            .eq("id", queue_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not existing.data:
            raise HTTPException(status_code=404, detail="Task queue not found")

        # Build update dict
        update_data = queue_data.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow().isoformat()

        # Update queue
        result = (
            client.table("environments")
            .update(update_data)
            .eq("id", queue_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update task queue"
            )

        queue = result.data[0]

        logger.info(
            "task_queue_updated",
            queue_id=queue_id,
            org_id=organization["id"],
        )

        # Note: Worker stats are now tracked at worker_queue level
        return TaskQueueResponse(
            **queue,
            active_workers=0,
            idle_workers=0,
            busy_workers=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("task_queue_update_failed", error=str(e), queue_id=queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update task queue: {str(e)}"
        )


@router.delete("/{queue_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task_queue(
    queue_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Delete a task queue"""
    try:
        client = get_supabase()

        # Prevent deleting default queue
        queue_check = (
            client.table("environments")
            .select("name")
            .eq("id", queue_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if queue_check.data and queue_check.data.get("name") == "default":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot delete the default queue"
            )

        result = (
            client.table("environments")
            .delete()
            .eq("id", queue_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Task queue not found")

        logger.info("task_queue_deleted", queue_id=queue_id, org_id=organization["id"])

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("task_queue_delete_failed", error=str(e), queue_id=queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete task queue: {str(e)}"
        )


@router.get("/{queue_name}/workers", response_model=List[WorkerHeartbeatResponse])
async def list_queue_workers(
    queue_name: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    List all workers for a specific queue.

    NOTE: This endpoint is deprecated. Workers are now organized by worker_queues.
    Use GET /environments/{env_id}/worker-queues and worker_queues endpoints instead.
    """
    logger.warning(
        "deprecated_endpoint_called",
        endpoint="/task-queues/{queue_name}/workers",
        queue_name=queue_name,
        org_id=organization["id"],
    )

    # Return empty list for backward compatibility
    return []


# Worker Registration

class WorkerCommandResponse(BaseModel):
    """Response with worker registration command"""
    worker_token: str
    task_queue_name: str
    command: str
    command_parts: dict  # Broken down for UI display
    namespace_status: str  # pending, provisioning, ready, error
    can_register: bool
    provisioning_workflow_id: str | None = None


@router.get("/{queue_id}/worker-command", response_model=WorkerCommandResponse)
async def get_worker_registration_command(
    queue_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Get the worker registration command for a task queue.

    Returns the kubiya worker start command with the worker token that users
    should run to start a worker for this task queue.

    The UI should display this in a "Register Worker" dialog when the queue
    is ready, and show provisioning status while the namespace is being created.
    """
    try:
        client = get_supabase()

        # Get task queue
        result = (
            client.table("environments")
            .select("*")
            .eq("id", queue_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Task queue not found")

        queue = result.data
        worker_token = queue.get("worker_token")

        # Generate worker_token if it doesn't exist (for existing queues)
        if not worker_token:
            worker_token = str(uuid.uuid4())
            # Update the queue with the generated token
            client.table("environments").update({
                "worker_token": worker_token,
                "updated_at": datetime.utcnow().isoformat(),
            }).eq("id", queue_id).execute()

            logger.info(
                "worker_token_generated",
                queue_id=queue_id,
                org_id=organization["id"],
            )

        task_queue_name = queue["name"]
        namespace_status = queue.get("status", "unknown")
        provisioning_workflow_id = queue.get("provisioning_workflow_id")

        # Check if namespace is ready
        can_register = namespace_status in ["ready", "active"]

        # Build command
        command = f"kubiya worker start --token {worker_token} --task-queue {task_queue_name}"

        command_parts = {
            "binary": "kubiya",
            "subcommand": "worker start",
            "flags": {
                "--token": worker_token,
                "--task-queue": task_queue_name,
            },
        }

        logger.info(
            "worker_command_retrieved",
            queue_id=queue_id,
            can_register=can_register,
            status=namespace_status,
            org_id=organization["id"],
        )

        return WorkerCommandResponse(
            worker_token=worker_token,
            task_queue_name=task_queue_name,
            command=command,
            command_parts=command_parts,
            namespace_status=namespace_status,
            can_register=can_register,
            provisioning_workflow_id=provisioning_workflow_id,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("worker_command_get_failed", error=str(e), queue_id=queue_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get worker command: {str(e)}"
        )
