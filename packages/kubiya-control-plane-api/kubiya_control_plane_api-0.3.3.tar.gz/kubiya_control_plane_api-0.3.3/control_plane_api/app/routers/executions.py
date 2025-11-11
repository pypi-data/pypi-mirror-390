"""
Multi-tenant executions router with Supabase.

This router handles execution queries for the authenticated organization.
Uses Supabase directly to avoid SQLAlchemy enum validation issues.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import asyncio
import json

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase
from control_plane_api.app.lib.temporal_client import get_temporal_client
from control_plane_api.app.lib.redis_client import get_redis_client
from control_plane_api.app.workflows.agent_execution import AgentExecutionWorkflow
from control_plane_api.app.services.agno_service import agno_service

logger = structlog.get_logger()

router = APIRouter()


# Pydantic schemas
class ParticipantResponse(BaseModel):
    """Participant in an execution"""
    id: str
    user_id: str
    user_name: str | None
    user_email: str | None
    user_avatar: str | None
    role: str
    joined_at: str
    last_active_at: str


class ExecutionResponse(BaseModel):
    id: str
    organization_id: str
    execution_type: str
    entity_id: str
    entity_name: str | None
    prompt: str
    system_prompt: str | None
    status: str
    response: str | None
    error_message: str | None
    usage: dict
    execution_metadata: dict
    runner_name: str | None
    user_id: str | None
    user_name: str | None
    user_email: str | None
    user_avatar: str | None
    created_at: str
    started_at: str | None
    completed_at: str | None
    updated_at: str
    participants: List[ParticipantResponse] = Field(default_factory=list)


@router.get("", response_model=List[ExecutionResponse])
async def list_executions(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
    execution_type: str | None = None,
    organization: dict = Depends(get_current_organization),
):
    """List all executions for the organization with optional filtering"""
    try:
        client = get_supabase()

        # Query executions for this organization with participants
        query = client.table("executions").select("*, execution_participants(*)").eq("organization_id", organization["id"])

        if status_filter:
            query = query.eq("status", status_filter.lower())  # Normalize to lowercase
        if execution_type:
            query = query.eq("execution_type", execution_type.upper())

        query = query.order("created_at", desc=True).range(skip, skip + limit - 1)

        result = query.execute()

        if not result or not result.data:
            logger.info("no_executions_found", org_id=organization["id"])
            return []

        executions = []
        for execution in result.data:
            try:
                # Parse participants
                participants_data = execution.get("execution_participants", [])
                participants = []
                for p in participants_data:
                    try:
                        participants.append(ParticipantResponse(
                            id=p["id"],
                            user_id=p["user_id"],
                            user_name=p.get("user_name"),
                            user_email=p.get("user_email"),
                            user_avatar=p.get("user_avatar"),
                            role=p["role"],
                            joined_at=p["joined_at"],
                            last_active_at=p["last_active_at"],
                        ))
                    except Exception as participant_error:
                        logger.warning("failed_to_parse_participant", error=str(participant_error), execution_id=execution.get("id"))
                        # Skip invalid participant, continue with others

                executions.append(
                    ExecutionResponse(
                        id=execution["id"],
                        organization_id=execution["organization_id"],
                        execution_type=execution["execution_type"],
                        entity_id=execution["entity_id"],
                        entity_name=execution.get("entity_name"),
                        prompt=execution.get("prompt", ""),
                        system_prompt=execution.get("system_prompt"),
                        status=execution["status"],
                        response=execution.get("response"),
                        error_message=execution.get("error_message"),
                        usage=execution.get("usage", {}),
                        execution_metadata=execution.get("execution_metadata", {}),
                        runner_name=execution.get("runner_name"),
                        user_id=execution.get("user_id"),
                        user_name=execution.get("user_name"),
                        user_email=execution.get("user_email"),
                        user_avatar=execution.get("user_avatar"),
                        created_at=execution["created_at"],
                        started_at=execution.get("started_at"),
                        completed_at=execution.get("completed_at"),
                        updated_at=execution["updated_at"],
                        participants=participants,
                    )
                )
            except Exception as execution_error:
                logger.error("failed_to_parse_execution", error=str(execution_error), execution_id=execution.get("id"))
                # Skip invalid execution, continue with others

        logger.info(
            "executions_listed_successfully",
            count=len(executions),
            org_id=organization["id"],
        )

        return executions

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "executions_list_failed",
            error=str(e),
            error_type=type(e).__name__,
            org_id=organization["id"]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list executions: {str(e)}"
        )


@router.get("/{execution_id}", response_model=ExecutionResponse)
async def get_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get a specific execution by ID"""
    try:
        client = get_supabase()

        result = (
            client.table("executions")
            .select("*")
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Execution not found")

        execution_data = result.data

        return ExecutionResponse(
            id=execution_data["id"],
            organization_id=execution_data["organization_id"],
            execution_type=execution_data["execution_type"],
            entity_id=execution_data["entity_id"],
            entity_name=execution_data.get("entity_name"),
            prompt=execution_data.get("prompt", ""),
            system_prompt=execution_data.get("system_prompt"),
            status=execution_data["status"],
            response=execution_data.get("response"),
            error_message=execution_data.get("error_message"),
            usage=execution_data.get("usage", {}),
            execution_metadata=execution_data.get("execution_metadata", {}),
            runner_name=execution_data.get("runner_name"),
            user_id=execution_data.get("user_id"),
            user_name=execution_data.get("user_name"),
            user_email=execution_data.get("user_email"),
            user_avatar=execution_data.get("user_avatar"),
            created_at=execution_data["created_at"],
            started_at=execution_data.get("started_at"),
            completed_at=execution_data.get("completed_at"),
            updated_at=execution_data["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("execution_get_failed", error=str(e), execution_id=execution_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get execution: {str(e)}"
        )


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Delete an execution"""
    try:
        client = get_supabase()

        result = (
            client.table("executions")
            .delete()
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Execution not found")

        logger.info("execution_deleted", execution_id=execution_id, org_id=organization["id"])

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("execution_delete_failed", error=str(e), execution_id=execution_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete execution: {str(e)}"
        )


class ExecutionUpdate(BaseModel):
    """Update execution fields - used by workers to update execution status"""
    status: str | None = None
    started_at: str | None = None
    completed_at: str | None = None
    response: str | None = None
    error_message: str | None = None
    usage: dict | None = None
    execution_metadata: dict | None = None


@router.patch("/{execution_id}", response_model=ExecutionResponse)
async def update_execution(
    execution_id: str,
    execution_update: ExecutionUpdate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Update execution status and results.

    This endpoint is primarily used by workers to update execution status,
    results, usage metrics, and metadata during execution.
    """
    try:
        client = get_supabase()

        # Build update dict - only include provided fields
        update_data = {}

        if execution_update.status is not None:
            update_data["status"] = execution_update.status.lower()  # Normalize to lowercase

        if execution_update.started_at is not None:
            update_data["started_at"] = execution_update.started_at

        if execution_update.completed_at is not None:
            update_data["completed_at"] = execution_update.completed_at

        if execution_update.response is not None:
            update_data["response"] = execution_update.response

        if execution_update.error_message is not None:
            update_data["error_message"] = execution_update.error_message

        if execution_update.usage is not None:
            update_data["usage"] = execution_update.usage

        if execution_update.execution_metadata is not None:
            update_data["execution_metadata"] = execution_update.execution_metadata

        # Always update updated_at
        update_data["updated_at"] = datetime.utcnow().isoformat()

        # Update execution
        result = (
            client.table("executions")
            .update(update_data)
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Execution not found")

        execution_data = result.data[0]

        logger.info(
            "execution_updated",
            execution_id=execution_id,
            org_id=organization["id"],
            fields_updated=list(update_data.keys()),
        )

        return ExecutionResponse(
            id=execution_data["id"],
            organization_id=execution_data["organization_id"],
            execution_type=execution_data["execution_type"],
            entity_id=execution_data["entity_id"],
            entity_name=execution_data.get("entity_name"),
            prompt=execution_data.get("prompt", ""),
            system_prompt=execution_data.get("system_prompt"),
            status=execution_data["status"],
            response=execution_data.get("response"),
            error_message=execution_data.get("error_message"),
            usage=execution_data.get("usage", {}),
            execution_metadata=execution_data.get("execution_metadata", {}),
            runner_name=execution_data.get("runner_name"),
            user_id=execution_data.get("user_id"),
            user_name=execution_data.get("user_name"),
            user_email=execution_data.get("user_email"),
            user_avatar=execution_data.get("user_avatar"),
            created_at=execution_data["created_at"],
            started_at=execution_data.get("started_at"),
            completed_at=execution_data.get("completed_at"),
            updated_at=execution_data["updated_at"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("execution_update_failed", error=str(e), execution_id=execution_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update execution: {str(e)}"
        )


class SendMessageRequest(BaseModel):
    """Request to send a message to a running execution"""
    message: str
    role: str = "user"  # user, system, etc.


@router.post("/{execution_id}/message", status_code=status.HTTP_202_ACCEPTED)
async def send_message_to_execution(
    execution_id: str,
    request_body: SendMessageRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Send a followup message to a running execution using Temporal signals.

    This sends a signal to the Temporal workflow, adding the message to the conversation.
    The workflow will process the message and respond accordingly.
    """
    try:
        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Verify the execution belongs to this organization and get execution type
        client = get_supabase()
        result = (
            client.table("executions")
            .select("id, organization_id, status, execution_type")
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Execution not found")

        # Construct workflow ID based on execution type
        execution_type = result.data.get("execution_type", "AGENT")
        if execution_type == "TEAM":
            workflow_id = f"team-execution-{execution_id}"
        else:
            workflow_id = f"agent-execution-{execution_id}"

        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Import ChatMessage from workflow
        from control_plane_api.app.workflows.agent_execution import ChatMessage
        from datetime import datetime, timezone

        # Create the message with user attribution from JWT token
        message = ChatMessage(
            role=request_body.role,
            content=request_body.message,
            timestamp=datetime.now(timezone.utc).isoformat(),
            user_id=organization.get("user_id"),
            user_name=organization.get("user_name"),
            user_email=organization.get("user_email"),
            user_avatar=organization.get("user_avatar"),  # Now available from JWT via auth middleware
        )

        # Send signal to workflow
        await workflow_handle.signal(AgentExecutionWorkflow.add_message, message)

        # Add user as participant if not already added (multiplayer support)
        user_id = organization.get("user_id")
        if user_id:
            try:
                # Check if participant already exists
                existing = (
                    client.table("execution_participants")
                    .select("id")
                    .eq("execution_id", execution_id)
                    .eq("user_id", user_id)
                    .execute()
                )

                if not existing.data or len(existing.data) == 0:
                    # Add as new participant (collaborator role)
                    import uuid
                    client.table("execution_participants").insert({
                        "id": str(uuid.uuid4()),
                        "execution_id": execution_id,
                        "organization_id": organization["id"],
                        "user_id": user_id,
                        "user_name": organization.get("user_name"),
                        "user_email": organization.get("user_email"),
                        "user_avatar": organization.get("user_avatar"),
                        "role": "collaborator",
                    }).execute()
                    logger.info(
                        "participant_added",
                        execution_id=execution_id,
                        user_id=user_id,
                    )
                else:
                    # Update last_active_at for existing participant
                    client.table("execution_participants").update({
                        "last_active_at": datetime.now(timezone.utc).isoformat(),
                    }).eq("execution_id", execution_id).eq("user_id", user_id).execute()
            except Exception as participant_error:
                logger.warning(
                    "failed_to_add_participant",
                    error=str(participant_error),
                    execution_id=execution_id,
                )
                # Don't fail the whole request if participant tracking fails

        logger.info(
            "message_sent_to_execution",
            execution_id=execution_id,
            org_id=organization["id"],
            role=request_body.role,
        )

        return {
            "success": True,
            "execution_id": execution_id,
            "message": "Message sent to workflow",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "send_message_failed",
            error=str(e),
            execution_id=execution_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send message: {str(e)}"
        )


@router.post("/{execution_id}/pause")
async def pause_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Pause an active execution by sending a signal to the Temporal workflow.

    This is triggered when the user clicks the PAUSE button in the UI.
    The workflow will stop processing but remain active and can be resumed.
    """
    try:
        logger.info(
            "pause_execution_requested",
            execution_id=execution_id,
            org_id=organization["id"]
        )

        # Get execution from Supabase
        client = get_supabase()
        result = (
            client.table("executions")
            .select("id, status, execution_type")
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        execution = result.data
        current_status = execution["status"]

        # Check if execution can be paused
        if current_status not in ["running", "waiting_for_input"]:
            logger.warning(
                "pause_execution_invalid_status",
                execution_id=execution_id,
                status=current_status
            )
            return {
                "success": False,
                "error": f"Execution cannot be paused (status: {current_status})",
                "execution_id": execution_id,
                "status": current_status,
            }

        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Determine workflow ID based on execution type
        execution_type = execution.get("execution_type", "AGENT")
        workflow_id = f"team-execution-{execution_id}" if execution_type == "TEAM" else f"agent-execution-{execution_id}"

        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Send pause signal to workflow
        await workflow_handle.signal(AgentExecutionWorkflow.pause_execution)

        # Update execution status to paused in Supabase
        (
            client.table("executions")
            .update({
                "status": "paused",
                "updated_at": datetime.utcnow().isoformat(),
            })
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        # Emit system message to Redis for UI display
        redis_client = get_redis_client()
        if redis_client:
            try:
                import time
                user_name = organization.get("user_name", "User")
                current_timestamp = datetime.utcnow().isoformat()
                message_id = f"{execution_id}_pause_{int(time.time() * 1000000)}"

                # Create message event - format matches what streaming endpoint expects
                pause_message_event = {
                    "event_type": "message",
                    "data": {
                        "role": "system",
                        "content": f"⏸️ Execution paused by {user_name}",
                        "timestamp": current_timestamp,
                        "message_id": message_id,
                    },
                    "timestamp": current_timestamp,
                    "execution_id": execution_id,
                }

                redis_key = f"execution:{execution_id}:events"
                await redis_client.lpush(redis_key, json.dumps(pause_message_event))
                await redis_client.ltrim(redis_key, 0, 999)
                await redis_client.expire(redis_key, 3600)

                # Also update status event
                status_event = {
                    "event_type": "status",
                    "data": {"status": "paused", "execution_id": execution_id},
                    "timestamp": current_timestamp,
                    "execution_id": execution_id,
                }
                await redis_client.lpush(redis_key, json.dumps(status_event))

                logger.debug("pause_event_published_to_redis", execution_id=execution_id)
            except Exception as redis_error:
                logger.warning("failed_to_publish_pause_event", error=str(redis_error), execution_id=execution_id)

        logger.info(
            "execution_paused_successfully",
            execution_id=execution_id,
            workflow_id=workflow_id
        )

        return {
            "success": True,
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "message": "Execution paused successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "pause_execution_error",
            execution_id=execution_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to pause execution: {str(e)}"
        )


@router.post("/{execution_id}/resume")
async def resume_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Resume a paused execution by sending a signal to the Temporal workflow.

    This is triggered when the user clicks the RESUME button in the UI.
    The workflow will continue processing from where it was paused.
    """
    try:
        logger.info(
            "resume_execution_requested",
            execution_id=execution_id,
            org_id=organization["id"]
        )

        # Get execution from Supabase
        client = get_supabase()
        result = (
            client.table("executions")
            .select("id, status, execution_type")
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        execution = result.data
        current_status = execution["status"]

        # Check if execution is paused
        if current_status != "paused":
            logger.warning(
                "resume_execution_not_paused",
                execution_id=execution_id,
                status=current_status
            )
            return {
                "success": False,
                "error": f"Execution is not paused (status: {current_status})",
                "execution_id": execution_id,
                "status": current_status,
            }

        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Determine workflow ID based on execution type
        execution_type = execution.get("execution_type", "AGENT")
        workflow_id = f"team-execution-{execution_id}" if execution_type == "TEAM" else f"agent-execution-{execution_id}"

        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Send resume signal to workflow
        await workflow_handle.signal(AgentExecutionWorkflow.resume_execution)

        # Update execution status back to running/waiting in Supabase
        # The workflow will determine the correct status
        (
            client.table("executions")
            .update({
                "status": "running",  # Workflow will update to correct status
                "updated_at": datetime.utcnow().isoformat(),
            })
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        # Emit system message to Redis for UI display
        redis_client = get_redis_client()
        if redis_client:
            try:
                import time
                user_name = organization.get("user_name", "User")
                current_timestamp = datetime.utcnow().isoformat()
                message_id = f"{execution_id}_resume_{int(time.time() * 1000000)}"

                # Create message event - format matches what streaming endpoint expects
                resume_message_event = {
                    "event_type": "message",
                    "data": {
                        "role": "system",
                        "content": f"▶️ Execution resumed by {user_name}",
                        "timestamp": current_timestamp,
                        "message_id": message_id,
                    },
                    "timestamp": current_timestamp,
                    "execution_id": execution_id,
                }

                redis_key = f"execution:{execution_id}:events"
                await redis_client.lpush(redis_key, json.dumps(resume_message_event))
                await redis_client.ltrim(redis_key, 0, 999)
                await redis_client.expire(redis_key, 3600)

                # Also update status event
                status_event = {
                    "event_type": "status",
                    "data": {"status": "running", "execution_id": execution_id},
                    "timestamp": current_timestamp,
                    "execution_id": execution_id,
                }
                await redis_client.lpush(redis_key, json.dumps(status_event))

                logger.debug("resume_event_published_to_redis", execution_id=execution_id)
            except Exception as redis_error:
                logger.warning("failed_to_publish_resume_event", error=str(redis_error), execution_id=execution_id)

        logger.info(
            "execution_resumed_successfully",
            execution_id=execution_id,
            workflow_id=workflow_id
        )

        return {
            "success": True,
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "message": "Execution resumed successfully",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "resume_execution_error",
            execution_id=execution_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to resume execution: {str(e)}"
        )


@router.post("/{execution_id}/cancel")
async def cancel_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Cancel an active execution by calling Temporal's workflow cancellation.

    This is triggered when the user clicks the STOP button in the UI.
    It uses Temporal's built-in cancellation which is fast and returns immediately.
    """
    try:
        from temporalio.client import WorkflowHandle

        logger.info(
            "cancel_execution_requested",
            execution_id=execution_id,
            org_id=organization["id"]
        )

        # Get execution from Supabase
        client = get_supabase()
        result = (
            client.table("executions")
            .select("id, status, execution_type")
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Execution not found"
            )

        execution = result.data
        current_status = execution["status"]

        # Check if execution is still running
        if current_status not in ["running", "waiting_for_input"]:
            logger.warning(
                "cancel_execution_not_running",
                execution_id=execution_id,
                status=current_status
            )
            return {
                "success": False,
                "error": f"Execution is not running (status: {current_status})",
                "execution_id": execution_id,
                "status": current_status,
            }

        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Determine workflow ID based on execution type
        execution_type = execution.get("execution_type", "AGENT")
        workflow_id = f"team-execution-{execution_id}" if execution_type == "TEAM" else f"agent-execution-{execution_id}"

        workflow_handle: WorkflowHandle = temporal_client.get_workflow_handle(
            workflow_id=workflow_id
        )

        # Use Temporal's built-in workflow cancellation
        # This is fast and returns immediately
        try:
            # Send cancel signal to the workflow
            # This returns immediately - it doesn't wait for the workflow to finish
            await workflow_handle.cancel()

            # Update execution status to cancelled in Supabase
            update_result = (
                client.table("executions")
                .update({
                    "status": "cancelled",
                    "completed_at": datetime.utcnow().isoformat(),
                    "error_message": "Cancelled by user",
                    "updated_at": datetime.utcnow().isoformat(),
                })
                .eq("id", execution_id)
                .eq("organization_id", organization["id"])
                .execute()
            )

            # Emit system message to Redis for UI display
            redis_client = get_redis_client()
            if redis_client:
                try:
                    import time
                    user_name = organization.get("user_name", "User")
                    current_timestamp = datetime.utcnow().isoformat()
                    message_id = f"{execution_id}_cancel_{int(time.time() * 1000000)}"

                    # Create message event - format matches what streaming endpoint expects
                    cancel_message_event = {
                        "event_type": "message",
                        "data": {
                            "role": "system",
                            "content": f"🛑 Execution stopped by {user_name}",
                            "timestamp": current_timestamp,
                            "message_id": message_id,
                        },
                        "timestamp": current_timestamp,
                        "execution_id": execution_id,
                    }

                    redis_key = f"execution:{execution_id}:events"
                    await redis_client.lpush(redis_key, json.dumps(cancel_message_event))
                    await redis_client.ltrim(redis_key, 0, 999)
                    await redis_client.expire(redis_key, 3600)

                    # Also update status event
                    status_event = {
                        "event_type": "status",
                        "data": {"status": "cancelled", "execution_id": execution_id},
                        "timestamp": current_timestamp,
                        "execution_id": execution_id,
                    }
                    await redis_client.lpush(redis_key, json.dumps(status_event))

                    logger.debug("cancel_event_published_to_redis", execution_id=execution_id)
                except Exception as redis_error:
                    logger.warning("failed_to_publish_cancel_event", error=str(redis_error), execution_id=execution_id)

            logger.info(
                "execution_cancelled_successfully",
                execution_id=execution_id,
                workflow_id=workflow_id
            )

            return {
                "success": True,
                "execution_id": execution_id,
                "workflow_id": workflow_id,
                "message": "Execution cancelled successfully",
            }

        except Exception as cancel_error:
            logger.error(
                "cancel_workflow_error",
                execution_id=execution_id,
                error=str(cancel_error)
            )

            # Mark as cancelled in database anyway (user intent matters)
            (
                client.table("executions")
                .update({
                    "status": "cancelled",
                    "completed_at": datetime.utcnow().isoformat(),
                    "error_message": f"Cancelled: {str(cancel_error)}",
                    "updated_at": datetime.utcnow().isoformat(),
                })
                .eq("id", execution_id)
                .eq("organization_id", organization["id"])
                .execute()
            )

            return {
                "success": True,  # User intent succeeded
                "execution_id": execution_id,
                "message": "Execution marked as cancelled",
                "warning": str(cancel_error),
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "cancel_execution_error",
            execution_id=execution_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel execution: {str(e)}"
        )


@router.get("/{execution_id}/session")
async def get_session_history(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Retrieve session history with Redis caching for hot loading.

    Workers GET session messages before each run to restore conversation context.

    Performance strategy:
    1. Check Redis cache first (hot path - milliseconds)
    2. Fall back to Supabase if not cached (cold path - ~50ms)
    3. Cache the result in Redis for next access
    """
    import json
    try:
        session_id = execution_id
        redis_key = f"session:{session_id}"

        # Try Redis first for hot loading
        redis_client = get_redis_client()
        if redis_client:
            try:
                cached_session = await redis_client.get(redis_key)
                if cached_session:
                    session_data = json.loads(cached_session)
                    logger.info(
                        "session_cache_hit",
                        execution_id=execution_id,
                        message_count=session_data.get("message_count", 0)
                    )
                    return session_data
            except Exception as redis_error:
                logger.warning("session_cache_error", error=str(redis_error))
                # Continue to DB fallback

        # Redis miss or unavailable - load from Supabase
        client = get_supabase()

        result = (
            client.table("sessions")
            .select("*")
            .eq("execution_id", execution_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Session not found")

        session_record = result.data
        messages = session_record.get("messages", [])

        session_data = {
            "session_id": session_record.get("session_id", execution_id),
            "execution_id": execution_id,
            "messages": messages,
            "message_count": len(messages),
            "metadata": session_record.get("metadata", {}),
        }

        # Cache in Redis for next access (TTL: 1 hour)
        if redis_client:
            try:
                await redis_client.setex(
                    redis_key,
                    3600,  # 1 hour TTL
                    json.dumps(session_data)
                )
                logger.info(
                    "session_cached",
                    execution_id=execution_id,
                    message_count=len(messages)
                )
            except Exception as cache_error:
                logger.warning("session_cache_write_error", error=str(cache_error))

        logger.info(
            "session_history_retrieved_from_supabase",
            execution_id=execution_id,
            session_id=session_record.get("session_id"),
            message_count=len(messages)
        )

        return session_data

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "failed_to_retrieve_session_history",
            execution_id=execution_id,
            error=str(e)
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve session history: {str(e)}"
        )


@router.post("/{execution_id}/session", status_code=status.HTTP_201_CREATED)
async def persist_session_history(
    execution_id: str,
    session_data: dict,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Persist session history from worker to Control Plane database.

    Worker POSTs session messages after each run completion.
    This ensures history is available even when worker is offline.

    Sessions are stored in Supabase for fast loading by the UI streaming endpoint.
    """
    try:
        client = get_supabase()

        session_id = session_data.get("session_id", execution_id)
        user_id = session_data.get("user_id")
        messages = session_data.get("messages", [])
        metadata = session_data.get("metadata", {})

        logger.info(
            "persisting_session_history",
            execution_id=execution_id,
            session_id=session_id,
            user_id=user_id,
            message_count=len(messages),
            org_id=organization["id"],
        )

        # Upsert to Supabase sessions table
        # This matches what the streaming endpoint expects to load
        session_record = {
            "execution_id": execution_id,
            "session_id": session_id,
            "organization_id": organization["id"],
            "user_id": user_id,
            "messages": messages,
            "metadata": metadata,
            "updated_at": datetime.utcnow().isoformat(),
        }

        result = (
            client.table("sessions")
            .upsert(session_record, on_conflict="execution_id")
            .execute()
        )

        if not result.data:
            logger.error(
                "session_upsert_failed",
                execution_id=execution_id,
                session_id=session_id
            )
            return {
                "success": False,
                "error": "Failed to upsert session to database"
            }

        logger.info(
            "session_persisted_to_supabase",
            execution_id=execution_id,
            session_id=session_id,
            message_count=len(messages),
        )

        # Cache in Redis for hot loading on next access
        import json

        redis_client = get_redis_client()
        if redis_client:
            try:
                redis_key = f"session:{session_id}"
                cache_data = {
                    "session_id": session_id,
                    "execution_id": execution_id,
                    "messages": messages,
                    "message_count": len(messages),
                }
                await redis_client.setex(
                    redis_key,
                    3600,  # 1 hour TTL
                    json.dumps(cache_data)
                )
                logger.info(
                    "session_cached_on_write",
                    execution_id=execution_id,
                    message_count=len(messages)
                )
            except Exception as cache_error:
                logger.warning("session_cache_write_error_on_persist", error=str(cache_error))
                # Don't fail persistence if caching fails

        return {
            "success": True,
            "execution_id": execution_id,
            "session_id": session_id,
            "persisted_messages": len(messages),
        }

    except Exception as e:
        logger.error(
            "session_persistence_failed",
            error=str(e),
            execution_id=execution_id,
        )
        return {
            "success": False,
            "error": str(e),
        }


@router.post("/{execution_id}/mark-done", status_code=status.HTTP_202_ACCEPTED)
async def mark_execution_as_done(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Mark an execution as done, signaling the workflow to complete.

    This sends a signal to the Temporal workflow to indicate the user is finished
    with the conversation. The workflow will complete gracefully after this signal.
    """
    try:
        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Verify the execution belongs to this organization and get execution type
        client = get_supabase()
        result = (
            client.table("executions")
            .select("id, organization_id, status, execution_type")
            .eq("id", execution_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Execution not found")

        # Construct workflow ID based on execution type
        execution_type = result.data.get("execution_type", "AGENT")
        if execution_type == "TEAM":
            workflow_id = f"team-execution-{execution_id}"
        else:
            workflow_id = f"agent-execution-{execution_id}"

        workflow_handle = temporal_client.get_workflow_handle(workflow_id)

        # Send mark_as_done signal to workflow
        await workflow_handle.signal(AgentExecutionWorkflow.mark_as_done)

        logger.info(
            "execution_marked_as_done",
            execution_id=execution_id,
            org_id=organization["id"],
        )

        return {
            "success": True,
            "execution_id": execution_id,
            "message": "Execution marked as done, workflow will complete",
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "mark_as_done_failed",
            error=str(e),
            execution_id=execution_id,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark execution as done: {str(e)}"
        )


class StreamingEventRequest(BaseModel):
    """Request to publish a streaming event to Redis for real-time UI updates"""
    event_type: str  # "status", "message", "tool_started", "tool_completed", "error"
    data: dict  # Event payload
    timestamp: str | None = None


@router.post("/{execution_id}/events", status_code=status.HTTP_202_ACCEPTED)
async def publish_execution_event(
    execution_id: str,
    event: StreamingEventRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Publish a streaming event to Redis for real-time UI updates.

    This endpoint is used by workers to send real-time events (tool execution, status updates, etc.)
    that are streamed to the UI via SSE without waiting for Temporal workflow completion.

    Events are stored in Redis list: execution:{execution_id}:events
    TTL: 1 hour (events are temporary, final state persists in database)
    """
    try:
        redis_client = get_redis_client()
        if not redis_client:
            # Redis not configured - skip streaming but don't fail
            logger.warning("redis_not_configured_for_streaming", execution_id=execution_id)
            return {"success": True, "message": "Redis not configured, event skipped"}

        # Skip database verification for performance - authentication already validates organization
        # Streaming events are temporary (1hr TTL) and don't need strict validation
        # The worker is already authenticated via API key which validates organization

        # Build event payload
        event_data = {
            "event_type": event.event_type,
            "data": event.data,
            "timestamp": event.timestamp or datetime.utcnow().isoformat(),
            "execution_id": execution_id,
        }

        # Push event to Redis list (most recent at head) - this must be FAST
        redis_key = f"execution:{execution_id}:events"
        await redis_client.lpush(redis_key, json.dumps(event_data))

        # Keep only last 1000 events (prevent memory issues)
        await redis_client.ltrim(redis_key, 0, 999)

        # Set TTL: 1 hour (events are temporary)
        await redis_client.expire(redis_key, 3600)

        # Also publish to pub/sub channel for real-time streaming
        # This allows connected SSE clients to receive updates instantly
        pubsub_channel = f"execution:{execution_id}:stream"
        try:
            await redis_client.publish(pubsub_channel, json.dumps(event_data))
        except Exception as pubsub_error:
            # Don't fail if pub/sub fails - the list storage is the primary mechanism
            logger.debug("pubsub_publish_failed", error=str(pubsub_error), execution_id=execution_id[:8])

        logger.info(
            "execution_event_published",
            execution_id=execution_id[:8],
            event_type=event.event_type,
        )

        return {
            "success": True,
            "execution_id": execution_id,
            "event_type": event.event_type,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "publish_event_failed",
            error=str(e),
            execution_id=execution_id,
            event_type=event.event_type,
        )
        # Don't fail the worker if streaming fails - it's not critical
        return {
            "success": False,
            "error": str(e),
            "message": "Event publishing failed but execution continues"
        }


@router.get("/{execution_id}/stream")
async def stream_execution(
    execution_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Stream execution updates using Server-Sent Events (SSE).

    This endpoint combines two sources for real-time updates:
    1. Redis streaming events (from worker activities) - sub-second latency
    2. Temporal workflow queries (for state consistency) - 200ms polling

    The Redis events provide instant tool execution updates, while Temporal
    ensures we never miss state changes even if Redis is unavailable.

    SSE format:
    - data: {json object with execution status, messages, tool calls}
    - event: status|message|tool_started|tool_completed|error|done
    """

    async def generate_sse():
        """Generate Server-Sent Events from Agno session and Temporal workflow state"""
        import time
        start_time = time.time()

        try:
            # Get Temporal client
            t0 = time.time()
            temporal_client = await get_temporal_client()
            logger.info("timing_temporal_client", duration_ms=int((time.time() - t0) * 1000), execution_id=execution_id)

            # Check Redis cache first for execution_type (fast, sub-millisecond)
            execution_type = None
            redis_client = get_redis_client()

            if redis_client:
                try:
                    t0 = time.time()
                    # Check if we have metadata event in Redis
                    redis_key = f"execution:{execution_id}:events"
                    redis_events = await redis_client.lrange(redis_key, 0, -1)

                    # Look for metadata event with execution_type
                    if redis_events:
                        for event_json in redis_events:
                            try:
                                event_data = json.loads(event_json)
                                if event_data.get("event_type") == "metadata" and event_data.get("data", {}).get("execution_type"):
                                    execution_type = event_data["data"]["execution_type"]
                                    logger.info("timing_redis_cache_hit", duration_ms=int((time.time() - t0) * 1000), execution_id=execution_id, execution_type=execution_type)
                                    break
                            except json.JSONDecodeError:
                                continue
                except Exception as redis_error:
                    logger.warning("redis_cache_lookup_failed", error=str(redis_error), execution_id=execution_id)

            # Fall back to database if not in cache
            if not execution_type:
                t0 = time.time()
                client = get_supabase()
                exec_result = (
                    client.table("executions")
                    .select("id, execution_type")
                    .eq("id", execution_id)
                    .eq("organization_id", organization["id"])
                    .single()
                    .execute()
                )
                logger.info("timing_db_query_fallback", duration_ms=int((time.time() - t0) * 1000), execution_id=execution_id)

                if not exec_result.data:
                    raise HTTPException(status_code=404, detail="Execution not found")

                execution_type = exec_result.data.get("execution_type", "AGENT")

            # Construct workflow ID based on execution type
            # Team executions use "team-execution-{id}", agent executions use "agent-execution-{id}"
            if execution_type == "TEAM":
                workflow_id = f"team-execution-{execution_id}"
            else:
                workflow_id = f"agent-execution-{execution_id}"

            workflow_handle = temporal_client.get_workflow_handle(workflow_id)

            logger.info(
                "execution_stream_connecting",
                execution_id=execution_id,
                execution_type=execution_type,
                workflow_id=workflow_id,
            )

            last_status = None
            last_message_count = 0
            last_keepalive = asyncio.get_event_loop().time()
            last_redis_event_index = -1  # Track which Redis events we've sent
            consecutive_failures = 0  # Track consecutive workflow query failures
            worker_down_mode = False  # Track if we're in worker-down fallback mode
            last_db_poll = 0  # Track last database poll time

            # Check if worker is ACTIVELY processing by checking Temporal workflow execution status
            # This is much more performant than querying workflow state - it's just a metadata lookup
            # We only stream from Redis if workflow is RUNNING at Temporal level (worker is active)
            # Otherwise, we load from database (workflow completed/failed/no active worker)
            is_workflow_running = False
            try:
                t0 = time.time()
                description = await workflow_handle.describe()
                # Temporal execution status: RUNNING, COMPLETED, FAILED, CANCELLED, TERMINATED, TIMED_OUT, CONTINUED_AS_NEW
                # Use .name to get just the enum name (e.g., "RUNNING") without the class prefix
                temporal_status_name = description.status.name
                is_workflow_running = temporal_status_name == "RUNNING"
                logger.info(
                    "initial_workflow_status",
                    execution_id=execution_id,
                    temporal_status=temporal_status_name,
                    temporal_status_full=str(description.status),
                    is_running=is_workflow_running,
                    duration_ms=int((time.time() - t0) * 1000)
                )
            except Exception as describe_error:
                # If we can't describe workflow, assume it's not running
                logger.warning("initial_workflow_describe_failed", execution_id=execution_id, error=str(describe_error))
                is_workflow_running = False

            # ALWAYS load historical messages from database first
            # This ensures UI sees conversation history even when connecting mid-execution
            # In streaming mode, we'll then continue with Redis for real-time updates
            t0 = time.time()
            try:
                # Read session from Control Plane database (where worker persists)
                client = get_supabase()
                session_result = (
                    client.table("sessions")
                        .select("messages")
                        .eq("execution_id", execution_id)
                        .order("updated_at", desc=True)
                        .limit(1)
                        .execute()
                )

                session_messages = []
                if session_result.data and len(session_result.data) > 0:
                    messages_data = session_result.data[0].get("messages", [])
                    # Convert dict messages to objects with attributes
                    from dataclasses import dataclass, field
                    from typing import Optional as Opt

                    @dataclass
                    class SessionMessage:
                        role: str
                        content: str
                        timestamp: Opt[str] = None
                        user_id: Opt[str] = None
                        user_name: Opt[str] = None
                        user_email: Opt[str] = None
                        user_avatar: Opt[str] = None

                    session_messages = [SessionMessage(**msg) for msg in messages_data]

                if session_messages:
                    logger.info(
                        "sending_session_history_on_connect",
                        execution_id=execution_id,
                        message_count=len(session_messages)
                    )

                    # Send all existing messages immediately
                    for msg in session_messages:
                        msg_data = {
                            "role": msg.role,
                            "content": msg.content,
                            "timestamp": msg.timestamp,  # Already in ISO format from database
                        }
                        # Include user attribution if available
                        if msg.user_id:
                            msg_data["user_id"] = msg.user_id
                            msg_data["user_name"] = msg.user_name
                            msg_data["user_email"] = msg.user_email
                            msg_data["user_avatar"] = msg.user_avatar
                        yield f"event: message\n"
                        yield f"data: {json.dumps(msg_data)}\n\n"

                    last_message_count = len(session_messages)

                logger.info("timing_session_history_load", duration_ms=int((time.time() - t0) * 1000), execution_id=execution_id, message_count=last_message_count)

            except Exception as session_error:
                    logger.warning(
                        "failed_to_load_session_history",
                        execution_id=execution_id,
                        error=str(session_error),
                        duration_ms=int((time.time() - t0) * 1000)
                    )
                    # Continue even if session loading fails - workflow state will still work

            while True:
                # Check if client disconnected
                if await request.is_disconnected():
                    logger.info("execution_stream_disconnected", execution_id=execution_id)
                    break

                # Send keepalive comment every 15 seconds to prevent timeout
                current_time = asyncio.get_event_loop().time()
                if current_time - last_keepalive > 15:
                    yield ": keepalive\n\n"
                    last_keepalive = current_time

                # FIRST: Check Redis for NEW real-time streaming events (sub-second latency)
                # ONLY if workflow is actively running (worker is connected and processing)
                # We track which events we've sent to avoid re-sending
                if is_workflow_running and redis_client:
                    try:
                        redis_key = f"execution:{execution_id}:events"
                        # Get the total count of events in Redis
                        total_events = await redis_client.llen(redis_key)

                        if total_events and total_events > (last_redis_event_index + 1):
                            # There are new events we haven't sent yet
                            logger.debug(
                                "redis_new_events_found",
                                execution_id=execution_id,
                                total=total_events,
                                last_index=last_redis_event_index
                            )

                            # Get all events (they're in reverse chronological order from LPUSH)
                            all_redis_events = await redis_client.lrange(redis_key, 0, -1)

                            if all_redis_events:
                                # Reverse to get chronological order (oldest first)
                                chronological_events = list(reversed(all_redis_events))

                                # Send only NEW events we haven't sent yet
                                for i in range(last_redis_event_index + 1, len(chronological_events)):
                                    event_json = chronological_events[i]

                                    try:
                                        event_data = json.loads(event_json)
                                        event_type = event_data.get("event_type", "message")

                                        # For message events with wrapped data (pause/resume/cancel system messages),
                                        # extract just the message data. For other events, send as-is.
                                        if event_type == "message" and "data" in event_data and isinstance(event_data["data"], dict) and "role" in event_data["data"]:
                                            # This is a new-style system message with role/content in data field
                                            payload = event_data["data"]
                                        else:
                                            # This is an existing event format - send the whole event_data
                                            payload = event_data

                                        # Stream the event to UI
                                        yield f"event: {event_type}\n"
                                        yield f"data: {json.dumps(payload)}\n\n"

                                        last_redis_event_index = i

                                        logger.debug(
                                            "redis_event_streamed",
                                            execution_id=execution_id,
                                            event_type=event_type,
                                            index=i
                                        )

                                    except json.JSONDecodeError:
                                        logger.warning("invalid_redis_event_json", event=event_json[:100])
                                        continue

                    except Exception as redis_error:
                        logger.error("redis_event_read_failed", error=str(redis_error), execution_id=execution_id)
                        # Continue with Temporal polling even if Redis fails

                try:
                    # SECOND: Check Temporal workflow execution status (lightweight metadata lookup)
                    t0 = time.time()
                    description = await workflow_handle.describe()
                    temporal_status = description.status.name  # Get enum name (e.g., "RUNNING")
                    describe_duration = int((time.time() - t0) * 1000)

                    # Log slow describe calls (>100ms)
                    if describe_duration > 100:
                        logger.warning("slow_temporal_describe", duration_ms=describe_duration, execution_id=execution_id)

                    # Update is_workflow_running based on Temporal execution status
                    # Only stream from Redis when workflow is actively being processed by a worker
                    previous_running_state = is_workflow_running
                    is_workflow_running = temporal_status == "RUNNING"

                    # Log when streaming mode changes
                    if previous_running_state != is_workflow_running:
                        logger.info(
                            "streaming_mode_changed",
                            execution_id=execution_id,
                            temporal_status=temporal_status,
                            is_workflow_running=is_workflow_running,
                            mode="redis_streaming" if is_workflow_running else "database_only"
                        )

                    # If workflow finished, send appropriate event and exit
                    if temporal_status in ["COMPLETED", "FAILED", "TERMINATED", "CANCELLED"]:
                        # Query workflow state one final time to get the complete results
                        try:
                            state = await workflow_handle.query(AgentExecutionWorkflow.get_state)

                            if temporal_status in ["COMPLETED", "TERMINATED"]:
                                done_data = {
                                    "execution_id": execution_id,
                                    "status": "completed",
                                    "response": state.current_response,
                                    "usage": state.usage,
                                    "metadata": state.metadata,
                                }
                                yield f"event: done\n"
                                yield f"data: {json.dumps(done_data)}\n\n"
                            else:  # FAILED or CANCELLED
                                error_data = {
                                    "error": state.error_message or f"Workflow {temporal_status.lower()}",
                                    "execution_id": execution_id,
                                    "status": "failed",
                                }
                                if state.metadata.get("error_type"):
                                    error_data["error_type"] = state.metadata["error_type"]
                                yield f"event: error\n"
                                yield f"data: {json.dumps(error_data)}\n\n"
                        except Exception as final_query_error:
                            # If we can't query for final state, fall back to database
                            logger.warning("final_state_query_failed", execution_id=execution_id, error=str(final_query_error))

                            # Try to get final status from database
                            try:
                                exec_result = (
                                    client.table("executions")
                                    .select("status, response, error_message, usage, execution_metadata")
                                    .eq("id", execution_id)
                                    .single()
                                    .execute()
                                )

                                if exec_result.data:
                                    if temporal_status in ["COMPLETED", "TERMINATED"]:
                                        done_data = {
                                            "execution_id": execution_id,
                                            "status": exec_result.data.get("status", "completed"),
                                            "response": exec_result.data.get("response"),
                                            "usage": exec_result.data.get("usage", {}),
                                            "metadata": exec_result.data.get("execution_metadata", {}),
                                        }
                                        yield f"event: done\n"
                                        yield f"data: {json.dumps(done_data)}\n\n"
                                    else:
                                        error_data = {
                                            "error": exec_result.data.get("error_message") or f"Workflow {temporal_status.lower()}",
                                            "execution_id": execution_id,
                                            "status": exec_result.data.get("status", "failed"),
                                        }
                                        yield f"event: error\n"
                                        yield f"data: {json.dumps(error_data)}\n\n"
                                else:
                                    yield f"event: done\n"
                                    yield f"data: {json.dumps({'execution_id': execution_id, 'workflow_status': temporal_status})}\n\n"
                            except Exception as db_error:
                                logger.error("database_fallback_failed", execution_id=execution_id, error=str(db_error))
                                yield f"event: done\n"
                                yield f"data: {json.dumps({'execution_id': execution_id, 'workflow_status': temporal_status})}\n\n"
                        break

                    # THIRD: Query workflow state for application-level details (messages, usage, etc.)
                    # Only do this if workflow is still running to get incremental updates
                    try:
                        state = await workflow_handle.query(AgentExecutionWorkflow.get_state)

                        # Reset failure counter on successful query
                        if consecutive_failures > 0:
                            logger.info(
                                "workflow_query_recovered",
                                execution_id=execution_id,
                                failures=consecutive_failures
                            )
                        consecutive_failures = 0
                        worker_down_mode = False

                        # Send status update if changed
                        if state.status != last_status:
                            yield f"event: status\n"
                            yield f"data: {json.dumps({'status': state.status, 'execution_id': execution_id})}\n\n"
                            last_status = state.status

                            logger.info(
                                "execution_status_update",
                                execution_id=execution_id,
                                status=state.status
                            )

                        # Send new messages incrementally
                        # Skip assistant messages - they're already streamed via message_chunk events
                        if len(state.messages) > last_message_count:
                            new_messages = state.messages[last_message_count:]
                            for msg in new_messages:
                                # Skip assistant messages to prevent duplicates with chunk streaming
                                if msg.role == "assistant":
                                    continue

                                msg_data = {
                                    "role": msg.role,
                                    "content": msg.content,
                                    "timestamp": msg.timestamp,
                                }
                                if msg.tool_name:
                                    msg_data["tool_name"] = msg.tool_name
                                    msg_data["tool_input"] = msg.tool_input
                                    msg_data["tool_output"] = msg.tool_output
                                # Include user attribution for messages
                                if hasattr(msg, 'user_id') and msg.user_id:
                                    msg_data["user_id"] = msg.user_id
                                    msg_data["user_name"] = msg.user_name
                                    msg_data["user_email"] = msg.user_email
                                    msg_data["user_avatar"] = msg.user_avatar

                                yield f"event: message\n"
                                yield f"data: {json.dumps(msg_data)}\n\n"

                            last_message_count = len(state.messages)

                    except Exception as query_error:
                        # Workflow query failed - track failures and switch to database fallback
                        consecutive_failures += 1
                        error_msg = str(query_error)

                        # Detect worker down condition
                        is_worker_down = "no poller seen" in error_msg or "workflow not found" in error_msg

                        if consecutive_failures >= 3 and not worker_down_mode:
                            worker_down_mode = True
                            logger.warning(
                                "worker_down_detected_switching_to_database_mode",
                                execution_id=execution_id,
                                failures=consecutive_failures,
                                error=error_msg
                            )

                        # In worker down mode, poll database for updates
                        if worker_down_mode:
                            current_time = time.time()
                            # Poll database every 2 seconds when worker is down
                            if current_time - last_db_poll >= 2.0:
                                try:
                                    # Check execution status from database
                                    exec_result = (
                                        client.table("executions")
                                        .select("status, response, error_message")
                                        .eq("id", execution_id)
                                        .single()
                                        .execute()
                                    )

                                    if exec_result.data:
                                        db_status = exec_result.data.get("status")

                                        # Send status update if changed
                                        if db_status and db_status != last_status:
                                            yield f"event: status\n"
                                            yield f"data: {json.dumps({'status': db_status, 'execution_id': execution_id, 'source': 'database'})}\n\n"
                                            last_status = db_status

                                            logger.info(
                                                "database_status_update",
                                                execution_id=execution_id,
                                                status=db_status
                                            )

                                        # Check if execution finished
                                        if db_status in ["completed", "failed", "cancelled"]:
                                            if db_status == "completed":
                                                done_data = {
                                                    "execution_id": execution_id,
                                                    "status": db_status,
                                                    "response": exec_result.data.get("response"),
                                                }
                                                yield f"event: done\n"
                                                yield f"data: {json.dumps(done_data)}\n\n"
                                            else:
                                                error_data = {
                                                    "error": exec_result.data.get("error_message") or f"Execution {db_status}",
                                                    "execution_id": execution_id,
                                                    "status": db_status,
                                                }
                                                yield f"event: error\n"
                                                yield f"data: {json.dumps(error_data)}\n\n"
                                            break

                                    # Check for new session messages
                                    session_result = (
                                        client.table("sessions")
                                        .select("messages")
                                        .eq("execution_id", execution_id)
                                        .single()
                                        .execute()
                                    )

                                    if session_result.data:
                                        db_messages = session_result.data.get("messages", [])
                                        if len(db_messages) > last_message_count:
                                            new_messages = db_messages[last_message_count:]
                                            for msg_dict in new_messages:
                                                yield f"event: message\n"
                                                yield f"data: {json.dumps(msg_dict)}\n\n"
                                            last_message_count = len(db_messages)

                                            logger.info(
                                                "database_messages_update",
                                                execution_id=execution_id,
                                                new_messages=len(new_messages)
                                            )

                                    last_db_poll = current_time

                                except Exception as db_poll_error:
                                    logger.error(
                                        "database_poll_failed",
                                        execution_id=execution_id,
                                        error=str(db_poll_error)
                                    )
                        else:
                            # Still trying to connect to worker - log but don't switch modes yet
                            logger.debug(
                                "workflow_query_failed",
                                execution_id=execution_id,
                                failures=consecutive_failures,
                                error=error_msg
                            )

                    # Poll every 200ms for real-time updates when worker is up
                    # Poll every 500ms when in worker down mode (database polling)
                    await asyncio.sleep(0.5 if worker_down_mode else 0.2)

                except Exception as error:
                    # Critical error (e.g., workflow describe failed)
                    logger.error(
                        "critical_streaming_error",
                        execution_id=execution_id,
                        error=str(error)
                    )
                    # Back off and retry
                    await asyncio.sleep(1.0)

        except Exception as e:
            logger.error("execution_stream_error", error=str(e), execution_id=execution_id)
            yield f"event: error\n"
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        generate_sse(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable nginx buffering
        }
    )
