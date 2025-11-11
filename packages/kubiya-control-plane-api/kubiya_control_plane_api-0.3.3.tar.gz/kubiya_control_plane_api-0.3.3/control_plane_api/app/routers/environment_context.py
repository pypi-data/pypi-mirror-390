"""
Environment Context router - Manage contextual settings for environments.

Allows attaching knowledge and resources to environments for agent execution context.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import uuid

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase

logger = structlog.get_logger()

router = APIRouter()


# Pydantic schemas
class UpdateEnvironmentContextRequest(BaseModel):
    knowledge_uuids: List[str] = Field(default_factory=list, description="Array of knowledge UUIDs")
    resource_ids: List[str] = Field(default_factory=list, description="Array of resource IDs from Meilisearch")


class EnvironmentContextResponse(BaseModel):
    id: str
    environment_id: str
    organization_id: str
    knowledge_uuids: List[str]
    resource_ids: List[str]
    created_at: str
    updated_at: str


@router.get("/environments/{environment_id}/context", response_model=EnvironmentContextResponse)
async def get_environment_context(
    environment_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get context configuration for an environment"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Verify environment exists
        env_result = (
            client.table("environments")
            .select("id")
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

        # Get or create context
        context_result = (
            client.table("environment_contexts")
            .select("*")
            .eq("environment_id", environment_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if context_result.data:
            return EnvironmentContextResponse(**context_result.data)

        # Create default context if it doesn't exist
        context_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        default_context = {
            "id": context_id,
            "environment_id": environment_id,
            "organization_id": org_id,
            "knowledge_uuids": [],
            "resource_ids": [],
            "created_at": now,
            "updated_at": now,
        }

        result = client.table("environment_contexts").insert(default_context).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create environment context"
            )

        logger.info(
            "environment_context_created",
            environment_id=environment_id,
            org_id=org_id,
        )

        return EnvironmentContextResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_environment_context_failed", error=str(e), environment_id=environment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get environment context: {str(e)}"
        )


@router.put("/environments/{environment_id}/context", response_model=EnvironmentContextResponse)
async def update_environment_context(
    environment_id: str,
    context_data: UpdateEnvironmentContextRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Update context configuration for an environment"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Verify environment exists
        env_result = (
            client.table("environments")
            .select("id")
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

        # Check if context exists
        existing_context = (
            client.table("environment_contexts")
            .select("id")
            .eq("environment_id", environment_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        now = datetime.utcnow().isoformat()

        if existing_context.data:
            # Update existing context
            update_data = {
                "knowledge_uuids": context_data.knowledge_uuids,
                "resource_ids": context_data.resource_ids,
                "updated_at": now,
            }

            result = (
                client.table("environment_contexts")
                .update(update_data)
                .eq("id", existing_context.data["id"])
                .execute()
            )

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update environment context"
                )

            logger.info(
                "environment_context_updated",
                environment_id=environment_id,
                knowledge_count=len(context_data.knowledge_uuids),
                resource_count=len(context_data.resource_ids),
                org_id=org_id,
            )

            return EnvironmentContextResponse(**result.data[0])
        else:
            # Create new context
            context_id = str(uuid.uuid4())

            new_context = {
                "id": context_id,
                "environment_id": environment_id,
                "organization_id": org_id,
                "knowledge_uuids": context_data.knowledge_uuids,
                "resource_ids": context_data.resource_ids,
                "created_at": now,
                "updated_at": now,
            }

            result = client.table("environment_contexts").insert(new_context).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create environment context"
                )

            logger.info(
                "environment_context_created",
                environment_id=environment_id,
                knowledge_count=len(context_data.knowledge_uuids),
                resource_count=len(context_data.resource_ids),
                org_id=org_id,
            )

            return EnvironmentContextResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_environment_context_failed", error=str(e), environment_id=environment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update environment context: {str(e)}"
        )


@router.delete("/environments/{environment_id}/context", status_code=status.HTTP_204_NO_CONTENT)
async def clear_environment_context(
    environment_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Clear all context for an environment (reset to empty arrays)"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Update context to empty arrays
        now = datetime.utcnow().isoformat()
        update_data = {
            "knowledge_uuids": [],
            "resource_ids": [],
            "updated_at": now,
        }

        result = (
            client.table("environment_contexts")
            .update(update_data)
            .eq("environment_id", environment_id)
            .eq("organization_id", org_id)
            .execute()
        )

        logger.info(
            "environment_context_cleared",
            environment_id=environment_id,
            org_id=org_id,
        )

        return None

    except Exception as e:
        logger.error("clear_environment_context_failed", error=str(e), environment_id=environment_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear environment context: {str(e)}"
        )
