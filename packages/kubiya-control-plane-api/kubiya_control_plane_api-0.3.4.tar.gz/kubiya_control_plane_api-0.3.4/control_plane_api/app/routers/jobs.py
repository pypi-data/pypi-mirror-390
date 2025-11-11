"""
Jobs router for scheduled and webhook-triggered executions.

This router handles:
- CRUD operations for jobs
- Manual job triggering
- Webhook URL generation and triggering
- Cron schedule management with Temporal
- Job execution history
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from typing import List, Optional
from datetime import datetime, timezone
import structlog
import uuid
import hmac
import hashlib
import secrets
import asyncio

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase
from control_plane_api.app.lib.temporal_client import get_temporal_client
from control_plane_api.app.lib.job_executor import select_worker_queue, substitute_prompt_parameters
from control_plane_api.app.schemas.job_schemas import (
    JobCreate,
    JobUpdate,
    JobResponse,
    JobTriggerRequest,
    JobTriggerResponse,
    JobExecutionHistoryResponse,
    JobExecutionHistoryItem,
    WebhookPayload,
    ExecutionEnvironment,
)
from temporalio.client import Schedule, ScheduleActionStartWorkflow, ScheduleSpec, ScheduleIntervalSpec
from croniter import croniter

logger = structlog.get_logger()

router = APIRouter()


def generate_webhook_secret() -> str:
    """Generate a secure random webhook secret"""
    return secrets.token_urlsafe(32)


def generate_webhook_path() -> str:
    """Generate a unique webhook URL path"""
    return secrets.token_urlsafe(16)


async def start_job_execution(
    job: dict,
    organization_id: str,
    trigger_type: str,
    trigger_metadata: dict,
    parameters: Optional[dict] = None,
) -> tuple[str, str]:
    """
    Start a job execution by directly triggering the appropriate workflow.

    Returns:
        Tuple of (workflow_id, execution_id)
    """
    from control_plane_api.app.lib.supabase import get_supabase

    supabase = get_supabase()
    temporal_client = await get_temporal_client()

    planning_mode = job.get("planning_mode")
    entity_type = job.get("entity_type")
    entity_id = job.get("entity_id")

    # Get the appropriate worker queue based on job configuration
    worker_queue_name, _ = await select_worker_queue(
        organization_id=organization_id,
        executor_type=job.get("executor_type", "auto"),
        worker_queue_name=job.get("worker_queue_name"),
        environment_name=job.get("environment_name"),
    )

    if not worker_queue_name:
        raise ValueError("No workers are currently running for your organization. Please start a worker to execute jobs.")

    # Extract runner_name from worker_queue_name (format: "org_id.runner_name")
    runner_name = worker_queue_name.split(".")[-1] if "." in worker_queue_name else worker_queue_name

    # Get entity name for display
    entity_name = job.get("entity_name")
    if not entity_name and entity_id and entity_type:
        # Try to get entity name from database
        entity_table = f"{entity_type}s"  # agent -> agents, team -> teams
        try:
            entity_result = supabase.table(entity_table).select("name").eq("id", entity_id).single().execute()
            if entity_result.data:
                entity_name = entity_result.data.get("name")
        except Exception as e:
            logger.warning("failed_to_get_entity_name", entity_type=entity_type, entity_id=entity_id, error=str(e))

    # Substitute parameters in prompt template
    prompt = job.get("prompt_template", "")
    if parameters:
        prompt = substitute_prompt_parameters(prompt, parameters)

    # Generate execution ID
    execution_id = str(uuid.uuid4())

    # Determine execution_type based on entity_type
    execution_type_value = entity_type.upper() if entity_type else "AGENT"

    # Map trigger_type to trigger_source
    trigger_source_map = {
        "manual": "job_manual",
        "cron": "job_cron",
        "webhook": "job_webhook",
    }
    trigger_source = trigger_source_map.get(trigger_type, "job_manual")

    # Create placeholder execution record so UI can immediately query it
    # The workflow will update this record with actual execution data
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()

    execution_record = {
        "id": execution_id,
        "organization_id": organization_id,
        "execution_type": execution_type_value,
        "entity_id": entity_id,
        "entity_name": entity_name,
        "runner_name": runner_name,
        "trigger_source": trigger_source,
        "trigger_metadata": {
            "job_id": job["id"],
            "job_name": job.get("name"),
            "trigger_type": trigger_type,
            **trigger_metadata,
        },
        # User attribution from trigger metadata
        "user_id": trigger_metadata.get("user_id"),
        "user_email": trigger_metadata.get("triggered_by") or trigger_metadata.get("user_email"),
        "user_name": trigger_metadata.get("user_name"),
        "user_avatar": trigger_metadata.get("user_avatar"),
        "status": "pending",
        "prompt": prompt if parameters else job.get("prompt_template", ""),
        "created_at": now,
        "updated_at": now,
        "execution_metadata": {
            "job_id": job["id"],
            "job_name": job.get("name"),
            "trigger_type": trigger_type,
            **trigger_metadata,
        },
    }

    # Insert the placeholder record
    supabase.table("executions").insert(execution_record).execute()

    # Create job_executions junction record to track this execution was triggered by a job
    job_execution_record = {
        "id": str(uuid.uuid4()),
        "job_id": job["id"],
        "execution_id": execution_id,
        "organization_id": organization_id,
        "trigger_type": trigger_type,
        "trigger_metadata": trigger_metadata,
        "execution_status": "pending",
        "created_at": now,
    }
    supabase.table("job_executions").insert(job_execution_record).execute()

    logger.info(
        "created_placeholder_execution",
        execution_id=execution_id,
        job_id=job["id"],
        trigger_type=trigger_type,
    )

    # Prepare workflow input based on entity type
    workflow_name = None
    workflow_input = None

    if planning_mode == "predefined_agent" and entity_type == "agent":
        # Start AgentExecutionWorkflow
        workflow_name = "AgentExecutionWorkflow"

        # Get agent details
        agent_result = supabase.table("agents").select("*").eq("id", entity_id).single().execute()
        if not agent_result.data:
            raise ValueError(f"Agent {entity_id} not found")

        agent = agent_result.data
        agent_config = agent.get("configuration", {})

        workflow_input = {
            "execution_id": execution_id,
            "agent_id": entity_id,
            "organization_id": organization_id,
            "prompt": prompt,
            "system_prompt": job.get("system_prompt") or agent_config.get("system_prompt"),
            "model_id": agent.get("model_id"),
            "model_config": agent.get("model_config", {}),
            "agent_config": {**agent_config, **(job.get("config", {}))},
            "mcp_servers": agent_config.get("mcpServers", {}),
            "user_metadata": {
                "job_id": job["id"],
                "job_name": job.get("name"),
                "trigger_type": trigger_type,
                **trigger_metadata,
            },
        }

    elif planning_mode == "predefined_team" and entity_type == "team":
        # Start TeamExecutionWorkflow
        workflow_name = "TeamExecutionWorkflow"

        workflow_input = {
            "execution_id": execution_id,
            "team_id": entity_id,
            "organization_id": organization_id,
            "prompt": prompt,
            "system_prompt": job.get("system_prompt"),
            "config": job.get("config", {}),
            "user_metadata": {
                "job_id": job["id"],
                "job_name": job.get("name"),
                "trigger_type": trigger_type,
                **trigger_metadata,
            },
        }
    else:
        raise ValueError(f"Unsupported planning_mode '{planning_mode}' or entity_type '{entity_type}'")

    # Start the workflow
    # Use standard workflow ID format for consistency with direct agent/team executions
    if entity_type == "agent":
        workflow_id = f"agent-execution-{execution_id}"
    elif entity_type == "team":
        workflow_id = f"team-execution-{execution_id}"
    else:
        # Fallback for other entity types
        workflow_id = f"job-{job['id']}-{trigger_type}-{uuid.uuid4()}"

    await temporal_client.start_workflow(
        workflow_name,
        workflow_input,
        id=workflow_id,
        task_queue=worker_queue_name,
    )

    logger.info(
        "job_execution_started",
        job_id=job["id"],
        workflow_id=workflow_id,
        execution_id=execution_id,
        trigger_type=trigger_type,
        workflow_name=workflow_name,
        worker_queue=worker_queue_name,
    )

    return workflow_id, execution_id


def verify_webhook_signature(payload: bytes, signature: str, secret: str) -> bool:
    """
    Verify HMAC signature for webhook payload.

    Args:
        payload: Raw request body bytes
        signature: Signature from X-Webhook-Signature header
        secret: Webhook secret from database

    Returns:
        True if signature is valid
    """
    expected_signature = hmac.new(
        secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)


async def create_temporal_schedule(
    job_id: str,
    organization_id: str,
    job_data: dict,
    cron_schedule: str,
    cron_timezone: str,
) -> str:
    """
    Create Temporal Schedule for cron-based job.

    The schedule directly triggers AgentExecutionWorkflow or TeamExecutionWorkflow
    based on the job's planning_mode and entity configuration.

    Args:
        job_id: Job ID
        organization_id: Organization ID
        job_data: Complete job data including entity info, prompt, config
        cron_schedule: Cron expression
        cron_timezone: Timezone for schedule

    Returns:
        Temporal Schedule ID
    """
    from control_plane_api.app.lib.supabase import get_supabase

    client = await get_temporal_client()
    supabase = get_supabase()
    schedule_id = f"job-{job_id}"

    try:
        # Determine execution type from planning_mode
        planning_mode = job_data.get("planning_mode")
        entity_type = job_data.get("entity_type")
        entity_id = job_data.get("entity_id")

        # Get the appropriate worker queue based on job configuration
        worker_queue_name, _ = await select_worker_queue(
            organization_id=organization_id,
            executor_type=job_data.get("executor_type", "auto"),
            worker_queue_name=job_data.get("worker_queue_name"),
            environment_name=job_data.get("environment_name"),
        )

        if not worker_queue_name:
            raise ValueError(
                f"No workers are currently running. Please start a worker before creating a cron job."
            )

        logger.info(
            "resolved_worker_queue_for_cron_job",
            job_id=job_id,
            worker_queue=worker_queue_name,
            planning_mode=planning_mode,
            entity_type=entity_type,
        )

        # Prepare workflow input based on entity type
        workflow_name = None
        workflow_input = None

        if planning_mode == "predefined_agent" and entity_type == "agent":
            # Schedule AgentExecutionWorkflow
            workflow_name = "AgentExecutionWorkflow"

            # Get agent details
            agent_result = supabase.table("agents").select("*").eq("id", entity_id).single().execute()
            if not agent_result.data:
                raise ValueError(f"Agent {entity_id} not found")

            agent = agent_result.data
            agent_config = agent.get("configuration", {})

            workflow_input = {
                "execution_id": None,  # Will be generated by workflow
                "agent_id": entity_id,
                "organization_id": organization_id,
                "prompt": job_data.get("prompt_template", ""),
                "system_prompt": job_data.get("system_prompt") or agent_config.get("system_prompt"),
                "model_id": agent.get("model_id"),
                "model_config": agent.get("model_config", {}),
                "agent_config": {**agent_config, **(job_data.get("config", {}))},
                "mcp_servers": agent_config.get("mcpServers", {}),
                "user_metadata": {
                    "job_id": job_id,
                    "job_name": job_data.get("name"),
                    "trigger_type": "cron",
                },
            }

        elif planning_mode == "predefined_team" and entity_type == "team":
            # Schedule TeamExecutionWorkflow
            workflow_name = "TeamExecutionWorkflow"

            workflow_input = {
                "execution_id": None,  # Will be generated by workflow
                "team_id": entity_id,
                "organization_id": organization_id,
                "prompt": job_data.get("prompt_template", ""),
                "system_prompt": job_data.get("system_prompt"),
                "config": job_data.get("config", {}),
                "user_metadata": {
                    "job_id": job_id,
                    "job_name": job_data.get("name"),
                    "trigger_type": "cron",
                },
            }
        else:
            raise ValueError(f"Unsupported planning_mode '{planning_mode}' or entity_type '{entity_type}' for cron jobs")

        # Create schedule action
        action = ScheduleActionStartWorkflow(
            workflow_name,
            workflow_input,
            id=f"job-{job_id}-{{{{SCHEDULE_ID}}}}",
            task_queue=worker_queue_name,
        )

        # Parse cron expression for schedule spec
        # Temporal uses cron format: second minute hour day month day_of_week
        # Standard cron is: minute hour day month day_of_week
        # We need to add "0" for seconds
        temporal_cron = f"0 {cron_schedule}"

        schedule_spec = ScheduleSpec(
            cron_expressions=[temporal_cron],
            time_zone_name=cron_timezone,
        )

        # Create schedule
        await client.create_schedule(
            schedule_id,
            Schedule(
                action=action,
                spec=schedule_spec,
            ),
        )

        logger.info(
            "temporal_schedule_created",
            schedule_id=schedule_id,
            job_id=job_id,
            cron_schedule=cron_schedule,
        )

        return schedule_id

    except Exception as e:
        logger.error(
            "failed_to_create_temporal_schedule",
            error=str(e),
            job_id=job_id,
            cron_schedule=cron_schedule,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create Temporal schedule: {str(e)}"
        )


async def delete_temporal_schedule(schedule_id: str) -> None:
    """Delete Temporal Schedule"""
    client = await get_temporal_client()

    try:
        handle = client.get_schedule_handle(schedule_id)
        await handle.delete()

        logger.info("temporal_schedule_deleted", schedule_id=schedule_id)

    except Exception as e:
        logger.error(
            "failed_to_delete_temporal_schedule",
            error=str(e),
            schedule_id=schedule_id,
        )
        # Don't raise - schedule might not exist


async def pause_temporal_schedule(schedule_id: str) -> None:
    """Pause Temporal Schedule"""
    client = await get_temporal_client()

    try:
        handle = client.get_schedule_handle(schedule_id)
        await handle.pause()

        logger.info("temporal_schedule_paused", schedule_id=schedule_id)

    except Exception as e:
        logger.error(
            "failed_to_pause_temporal_schedule",
            error=str(e),
            schedule_id=schedule_id,
        )
        raise


async def unpause_temporal_schedule(schedule_id: str) -> None:
    """Unpause Temporal Schedule"""
    client = await get_temporal_client()

    try:
        handle = client.get_schedule_handle(schedule_id)
        await handle.unpause()

        logger.info("temporal_schedule_unpaused", schedule_id=schedule_id)

    except Exception as e:
        logger.error(
            "failed_to_unpause_temporal_schedule",
            error=str(e),
            schedule_id=schedule_id,
        )
        raise


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Create a new job.

    Jobs can be triggered via:
    - Cron schedule (requires cron_schedule parameter)
    - Webhook (generates unique webhook URL)
    - Manual API trigger

    **Request Body:**
    - name: Job name
    - trigger_type: "cron", "webhook", or "manual"
    - cron_schedule: Cron expression (required for cron trigger)
    - planning_mode: "on_the_fly", "predefined_agent", "predefined_team", or "predefined_workflow"
    - entity_id: Entity ID (required for predefined modes)
    - prompt_template: Prompt template with {{variable}} placeholders
    - executor_type: "auto", "specific_queue", or "environment"
    """
    client = get_supabase()
    organization_id = organization["id"]

    logger.info(
        "creating_job",
        organization_id=organization_id,
        name=job_data.name,
        trigger_type=job_data.trigger_type,
    )

    try:
        job_id = str(uuid.uuid4())
        now = datetime.now(timezone.utc).isoformat()

        # Generate webhook URL if trigger_type is webhook
        webhook_url_path = None
        webhook_secret = None
        if job_data.trigger_type == "webhook":
            webhook_url_path = f"/api/v1/jobs/webhook/{generate_webhook_path()}"
            webhook_secret = generate_webhook_secret()

        # Prepare job data
        job_record = {
            "id": job_id,
            "organization_id": organization_id,
            "name": job_data.name,
            "description": job_data.description,
            "enabled": job_data.enabled,
            "status": "active" if job_data.enabled else "disabled",
            "trigger_type": job_data.trigger_type,
            "cron_schedule": job_data.cron_schedule,
            "cron_timezone": job_data.cron_timezone or "UTC",
            "webhook_url_path": webhook_url_path,
            "webhook_secret": webhook_secret,
            "temporal_schedule_id": None,
            "planning_mode": job_data.planning_mode,
            "entity_type": job_data.entity_type,
            "entity_id": job_data.entity_id,
            "prompt_template": job_data.prompt_template,
            "system_prompt": job_data.system_prompt,
            "executor_type": job_data.executor_type,
            "worker_queue_name": job_data.worker_queue_name,
            "environment_name": job_data.environment_name,
            "config": job_data.config,
            "execution_environment": job_data.execution_environment.dict() if job_data.execution_environment else {},
            "total_executions": 0,
            "successful_executions": 0,
            "failed_executions": 0,
            "execution_history": [],
            "last_execution_id": None,
            "last_execution_at": None,
            "next_execution_at": None,
            "last_triggered_at": None,
            "created_by": organization.get("user_id"),
            "updated_by": None,
            "created_at": now,
            "updated_at": now,
        }

        # If entity_id is provided, fetch entity name
        if job_data.entity_id and job_data.entity_type:
            table_name = f"{job_data.entity_type}s"
            entity_result = (
                client.table(table_name)
                .select("name")
                .eq("id", job_data.entity_id)
                .eq("organization_id", organization_id)
                .execute()
            )
            if entity_result.data:
                job_record["entity_name"] = entity_result.data[0]["name"]

        # Create Temporal Schedule for cron jobs
        if job_data.trigger_type == "cron" and job_data.enabled:
            temporal_schedule_id = await create_temporal_schedule(
                job_id=job_id,
                organization_id=organization_id,
                job_data=job_record,
                cron_schedule=job_data.cron_schedule,
                cron_timezone=job_data.cron_timezone or "UTC",
            )
            job_record["temporal_schedule_id"] = temporal_schedule_id

            # Calculate next execution time
            cron_iter = croniter(job_data.cron_schedule, datetime.now(timezone.utc))
            next_execution = cron_iter.get_next(datetime)
            job_record["next_execution_at"] = next_execution.isoformat()

        # Insert job into database
        result = client.table("jobs").insert(job_record).execute()

        logger.info(
            "job_created",
            job_id=job_id,
            name=job_data.name,
            trigger_type=job_data.trigger_type,
        )

        # Build response
        job = result.data[0]
        response_data = {**job}

        # Add full webhook URL to response
        if webhook_url_path:
            response_data["webhook_url"] = f"{str(request.base_url).rstrip('')}{webhook_url_path}"

        return JobResponse(**response_data)

    except Exception as e:
        logger.error(
            "failed_to_create_job",
            error=str(e),
            organization_id=organization_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job: {str(e)}"
        )


@router.get("", response_model=List[JobResponse])
async def list_jobs(
    request: Request,
    organization: dict = Depends(get_current_organization),
    enabled: Optional[bool] = None,
    trigger_type: Optional[str] = None,
):
    """
    List all jobs for the organization.

    **Query Parameters:**
    - enabled: Filter by enabled status (true/false)
    - trigger_type: Filter by trigger type ("cron", "webhook", "manual")
    """
    client = get_supabase()
    organization_id = organization["id"]

    try:
        query = client.table("jobs").select("*").eq("organization_id", organization_id)

        if enabled is not None:
            query = query.eq("enabled", enabled)

        if trigger_type:
            query = query.eq("trigger_type", trigger_type)

        result = query.order("created_at", desc=True).execute()

        # Build responses with full webhook URLs
        base_url = str(request.base_url).rstrip("/")
        jobs = []
        for job in result.data:
            job_data = {**job}
            if job.get("webhook_url_path"):
                job_data["webhook_url"] = f"{base_url}{job['webhook_url_path']}"
            jobs.append(JobResponse(**job_data))

        return jobs

    except Exception as e:
        logger.error(
            "failed_to_list_jobs",
            error=str(e),
            organization_id=organization_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list jobs: {str(e)}"
        )


@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get job details by ID"""
    client = get_supabase()
    organization_id = organization["id"]

    try:
        result = (
            client.table("jobs")
            .select("*")
            .eq("id", job_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        job = result.data[0]
        job_data = {**job}

        # Add full webhook URL
        if job.get("webhook_url_path"):
            base_url = str(request.base_url).rstrip("/")
            job_data["webhook_url"] = f"{base_url}{job['webhook_url_path']}"

        return JobResponse(**job_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_get_job",
            error=str(e),
            job_id=job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job: {str(e)}"
        )


@router.patch("/{job_id}", response_model=JobResponse)
async def update_job(
    job_id: str,
    job_data: JobUpdate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Update job configuration.

    **Note:** Updating cron_schedule will recreate the Temporal Schedule.
    """
    client = get_supabase()
    organization_id = organization["id"]

    try:
        # Fetch existing job
        result = (
            client.table("jobs")
            .select("*")
            .eq("id", job_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        existing_job = result.data[0]

        # Build update data
        update_data = {}
        for field, value in job_data.dict(exclude_unset=True).items():
            if value is not None:
                if field == "execution_environment" and isinstance(value, ExecutionEnvironment):
                    update_data[field] = value.dict()
                else:
                    update_data[field] = value

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )

        update_data["updated_by"] = organization.get("user_id")
        update_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        # If entity_id is being updated, fetch entity name
        if "entity_id" in update_data and "entity_type" in update_data:
            entity_type = update_data.get("entity_type", existing_job["entity_type"])
            entity_id = update_data["entity_id"]
            table_name = f"{entity_type}s"
            entity_result = (
                client.table(table_name)
                .select("name")
                .eq("id", entity_id)
                .eq("organization_id", organization_id)
                .execute()
            )
            if entity_result.data:
                update_data["entity_name"] = entity_result.data[0]["name"]

        # Handle cron schedule updates
        if "cron_schedule" in update_data and existing_job["trigger_type"] == "cron":
            # Delete existing schedule
            if existing_job.get("temporal_schedule_id"):
                await delete_temporal_schedule(existing_job["temporal_schedule_id"])

            # Create new schedule if job is enabled
            if existing_job.get("enabled", True):
                # Merge existing job data with updates for schedule
                updated_job_data = {**existing_job, **update_data}

                temporal_schedule_id = await create_temporal_schedule(
                    job_id=job_id,
                    organization_id=organization_id,
                    job_data=updated_job_data,
                    cron_schedule=update_data["cron_schedule"],
                    cron_timezone=update_data.get("cron_timezone", existing_job.get("cron_timezone", "UTC")),
                )
                update_data["temporal_schedule_id"] = temporal_schedule_id

                # Calculate next execution time
                cron_iter = croniter(update_data["cron_schedule"], datetime.now(timezone.utc))
                next_execution = cron_iter.get_next(datetime)
                update_data["next_execution_at"] = next_execution.isoformat()

        # Update job
        result = (
            client.table("jobs")
            .update(update_data)
            .eq("id", job_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        logger.info(
            "job_updated",
            job_id=job_id,
            updated_fields=list(update_data.keys()),
        )

        job = result.data[0]
        job_data_response = {**job}

        # Add full webhook URL
        if job.get("webhook_url_path"):
            base_url = str(request.base_url).rstrip("/")
            job_data_response["webhook_url"] = f"{base_url}{job['webhook_url_path']}"

        return JobResponse(**job_data_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_update_job",
            error=str(e),
            job_id=job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job: {str(e)}"
        )


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_job(
    job_id: str,
    organization: dict = Depends(get_current_organization),
):
    """Delete a job and its Temporal Schedule"""
    client = get_supabase()
    organization_id = organization["id"]

    try:
        # Fetch job to get temporal_schedule_id
        result = (
            client.table("jobs")
            .select("temporal_schedule_id")
            .eq("id", job_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        job = result.data[0]

        # Delete Temporal Schedule
        if job.get("temporal_schedule_id"):
            await delete_temporal_schedule(job["temporal_schedule_id"])

        # Delete job from database
        client.table("jobs").delete().eq("id", job_id).eq("organization_id", organization_id).execute()

        logger.info("job_deleted", job_id=job_id)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_delete_job",
            error=str(e),
            job_id=job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job: {str(e)}"
        )


@router.post("/{job_id}/trigger", response_model=JobTriggerResponse)
async def trigger_job(
    job_id: str,
    trigger_data: JobTriggerRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Manually trigger a job execution.

    **Request Body:**
    - parameters: Dictionary of parameters to substitute in prompt template
    - config_override: Optional config overrides for this execution
    """
    client = get_supabase()
    temporal_client = await get_temporal_client()
    organization_id = organization["id"]

    try:
        # Validate job exists and is enabled
        result = (
            client.table("jobs")
            .select("*")
            .eq("id", job_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        job = result.data[0]

        if not job.get("enabled"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job is disabled"
            )

        # Apply config overrides if provided
        if trigger_data.config_override:
            job = {**job, "config": {**job.get("config", {}), **trigger_data.config_override}}

        # Start the job execution directly (same as UI does)
        workflow_id, execution_id = await start_job_execution(
            job=job,
            organization_id=organization_id,
            trigger_type="manual",
            trigger_metadata={
                "triggered_by": organization.get("user_email"),
                "user_id": organization.get("user_id"),
            },
            parameters=trigger_data.parameters,
        )

        return JobTriggerResponse(
            job_id=job_id,
            workflow_id=workflow_id,
            execution_id=execution_id,
            status="started",
            message="Job execution started successfully",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_trigger_job",
            error=str(e),
            job_id=job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger job: {str(e)}"
        )


@router.post("/{job_id}/enable", response_model=JobResponse)
async def enable_job(
    job_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Enable a job and unpause its Temporal Schedule"""
    client = get_supabase()
    organization_id = organization["id"]

    try:
        # Fetch job
        result = (
            client.table("jobs")
            .select("*")
            .eq("id", job_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        job = result.data[0]

        # Unpause Temporal Schedule if it exists
        if job.get("temporal_schedule_id"):
            await unpause_temporal_schedule(job["temporal_schedule_id"])
        elif job.get("trigger_type") == "cron":
            # Create schedule if it doesn't exist
            temporal_schedule_id = await create_temporal_schedule(
                job_id=job_id,
                organization_id=organization_id,
                job_data=job,
                cron_schedule=job["cron_schedule"],
                cron_timezone=job.get("cron_timezone", "UTC"),
            )

            # Update job with schedule ID
            update_data = {
                "temporal_schedule_id": temporal_schedule_id,
                "enabled": True,
                "status": "active",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }

            # Calculate next execution time
            cron_iter = croniter(job["cron_schedule"], datetime.now(timezone.utc))
            next_execution = cron_iter.get_next(datetime)
            update_data["next_execution_at"] = next_execution.isoformat()

            result = (
                client.table("jobs")
                .update(update_data)
                .eq("id", job_id)
                .eq("organization_id", organization_id)
                .execute()
            )

            job = result.data[0]
        else:
            # Just enable the job
            result = (
                client.table("jobs")
                .update({
                    "enabled": True,
                    "status": "active",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                })
                .eq("id", job_id)
                .eq("organization_id", organization_id)
                .execute()
            )

            job = result.data[0]

        logger.info("job_enabled", job_id=job_id)

        job_data = {**job}
        if job.get("webhook_url_path"):
            base_url = str(request.base_url).rstrip("/")
            job_data["webhook_url"] = f"{base_url}{job['webhook_url_path']}"

        return JobResponse(**job_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_enable_job",
            error=str(e),
            job_id=job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to enable job: {str(e)}"
        )


@router.post("/{job_id}/disable", response_model=JobResponse)
async def disable_job(
    job_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Disable a job and pause its Temporal Schedule"""
    client = get_supabase()
    organization_id = organization["id"]

    try:
        # Fetch job
        result = (
            client.table("jobs")
            .select("*")
            .eq("id", job_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Job {job_id} not found"
            )

        job = result.data[0]

        # Pause Temporal Schedule if it exists
        if job.get("temporal_schedule_id"):
            await pause_temporal_schedule(job["temporal_schedule_id"])

        # Update job status
        result = (
            client.table("jobs")
            .update({
                "enabled": False,
                "status": "disabled",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            })
            .eq("id", job_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        logger.info("job_disabled", job_id=job_id)

        job = result.data[0]
        job_data = {**job}
        if job.get("webhook_url_path"):
            base_url = str(request.base_url).rstrip("/")
            job_data["webhook_url"] = f"{base_url}{job['webhook_url_path']}"

        return JobResponse(**job_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_disable_job",
            error=str(e),
            job_id=job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to disable job: {str(e)}"
        )


@router.get("/{job_id}/executions", response_model=JobExecutionHistoryResponse)
async def get_job_executions(
    job_id: str,
    organization: dict = Depends(get_current_organization),
    limit: int = 50,
    offset: int = 0,
):
    """
    Get execution history for a job.

    **Query Parameters:**
    - limit: Maximum number of executions to return (default: 50)
    - offset: Number of executions to skip (default: 0)
    """
    client = get_supabase()
    organization_id = organization["id"]

    try:
        # Fetch executions from job_executions table with join to executions
        result = (
            client.table("job_executions")
            .select("*, executions(*)")
            .eq("job_id", job_id)
            .eq("organization_id", organization_id)
            .order("created_at", desc=True)
            .range(offset, offset + limit - 1)
            .execute()
        )

        # Count total executions
        count_result = (
            client.table("job_executions")
            .select("id", count="exact")
            .eq("job_id", job_id)
            .eq("organization_id", organization_id)
            .execute()
        )

        executions = []
        for item in result.data:
            execution = item.get("executions", {})
            executions.append(
                JobExecutionHistoryItem(
                    execution_id=execution.get("id"),
                    trigger_type=item.get("trigger_type"),
                    status=execution.get("status"),
                    started_at=execution.get("started_at"),
                    completed_at=execution.get("completed_at"),
                    duration_ms=item.get("execution_duration_ms"),
                    error_message=execution.get("error_message"),
                )
            )

        return JobExecutionHistoryResponse(
            job_id=job_id,
            total_count=count_result.count or 0,
            executions=executions,
        )

    except Exception as e:
        logger.error(
            "failed_to_get_job_executions",
            error=str(e),
            job_id=job_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get job executions: {str(e)}"
        )


@router.post("/webhook/{webhook_path}", response_model=JobTriggerResponse)
async def trigger_webhook(
    webhook_path: str,
    payload: WebhookPayload,
    request: Request,
    x_webhook_signature: Optional[str] = Header(None),
):
    """
    Trigger a job via webhook.

    **Security:**
    - Requires HMAC signature in X-Webhook-Signature header
    - Signature format: hex(HMAC-SHA256(secret, request_body))

    **Request Body:**
    - parameters: Dictionary of parameters to substitute in prompt template
    - config_override: Optional config overrides for this execution
    - metadata: Additional metadata for this trigger
    """
    client = get_supabase()
    temporal_client = await get_temporal_client()

    try:
        # Fetch job by webhook path
        webhook_url_path = f"/api/v1/jobs/webhook/{webhook_path}"
        result = (
            client.table("jobs")
            .select("*")
            .eq("webhook_url_path", webhook_url_path)
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Webhook not found"
            )

        job = result.data[0]

        # Verify webhook signature
        if not x_webhook_signature:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing X-Webhook-Signature header"
            )

        # Get raw request body for signature verification
        body = await request.body()
        if not verify_webhook_signature(body, x_webhook_signature, job["webhook_secret"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid webhook signature"
            )

        # Validate job is enabled
        if not job.get("enabled"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Job is disabled"
            )

        # Apply config overrides if provided
        if payload.config_override:
            job = {**job, "config": {**job.get("config", {}), **payload.config_override}}

        # Start the job execution directly (same as UI does)
        workflow_id, execution_id = await start_job_execution(
            job=job,
            organization_id=job["organization_id"],
            trigger_type="webhook",
            trigger_metadata={
                "webhook_path": webhook_path,
                "metadata": payload.metadata or {},
            },
            parameters=payload.parameters,
        )

        return JobTriggerResponse(
            job_id=job["id"],
            workflow_id=workflow_id,
            execution_id=execution_id,
            status="started",
            message="Job execution started successfully via webhook",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_trigger_webhook",
            error=str(e),
            webhook_path=webhook_path,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger webhook: {str(e)}"
        )
