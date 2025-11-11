"""
Team Context router - Manage contextual settings for teams.

Allows attaching knowledge and resources to teams for agent execution context.
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
class UpdateTeamContextRequest(BaseModel):
    knowledge_uuids: List[str] = Field(default_factory=list, description="Array of knowledge UUIDs")
    resource_ids: List[str] = Field(default_factory=list, description="Array of resource IDs from Meilisearch")


class TeamContextResponse(BaseModel):
    id: str
    team_id: str
    organization_id: str
    knowledge_uuids: List[str]
    resource_ids: List[str]
    created_at: str
    updated_at: str


@router.get("/teams/{team_id}/context", response_model=TeamContextResponse)
async def get_team_context(
    team_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get context configuration for a team"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Verify team exists
        team_result = (
            client.table("teams")
            .select("id")
            .eq("id", team_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if not team_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        # Get or create context
        context_result = (
            client.table("team_contexts")
            .select("*")
            .eq("team_id", team_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if context_result.data:
            return TeamContextResponse(**context_result.data)

        # Create default context if it doesn't exist
        context_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        default_context = {
            "id": context_id,
            "team_id": team_id,
            "organization_id": org_id,
            "knowledge_uuids": [],
            "resource_ids": [],
            "created_at": now,
            "updated_at": now,
        }

        result = client.table("team_contexts").insert(default_context).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create team context"
            )

        logger.info(
            "team_context_created",
            team_id=team_id,
            org_id=org_id,
        )

        return TeamContextResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_team_context_failed", error=str(e), team_id=team_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get team context: {str(e)}"
        )


@router.put("/teams/{team_id}/context", response_model=TeamContextResponse)
async def update_team_context(
    team_id: str,
    context_data: UpdateTeamContextRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Update context configuration for a team"""
    try:
        client = get_supabase()
        org_id = organization["id"]

        # Verify team exists
        team_result = (
            client.table("teams")
            .select("id")
            .eq("id", team_id)
            .eq("organization_id", org_id)
            .single()
            .execute()
        )

        if not team_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Team not found"
            )

        # Check if context exists
        existing_context = (
            client.table("team_contexts")
            .select("id")
            .eq("team_id", team_id)
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
                client.table("team_contexts")
                .update(update_data)
                .eq("id", existing_context.data["id"])
                .execute()
            )

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to update team context"
                )

            logger.info(
                "team_context_updated",
                team_id=team_id,
                knowledge_count=len(context_data.knowledge_uuids),
                resource_count=len(context_data.resource_ids),
                org_id=org_id,
            )

            return TeamContextResponse(**result.data[0])
        else:
            # Create new context
            context_id = str(uuid.uuid4())

            new_context = {
                "id": context_id,
                "team_id": team_id,
                "organization_id": org_id,
                "knowledge_uuids": context_data.knowledge_uuids,
                "resource_ids": context_data.resource_ids,
                "created_at": now,
                "updated_at": now,
            }

            result = client.table("team_contexts").insert(new_context).execute()

            if not result.data:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create team context"
                )

            logger.info(
                "team_context_created",
                team_id=team_id,
                knowledge_count=len(context_data.knowledge_uuids),
                resource_count=len(context_data.resource_ids),
                org_id=org_id,
            )

            return TeamContextResponse(**result.data[0])

    except HTTPException:
        raise
    except Exception as e:
        logger.error("update_team_context_failed", error=str(e), team_id=team_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update team context: {str(e)}"
        )


@router.delete("/teams/{team_id}/context", status_code=status.HTTP_204_NO_CONTENT)
async def clear_team_context(
    team_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Clear all context for a team (reset to empty arrays)"""
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
            client.table("team_contexts")
            .update(update_data)
            .eq("team_id", team_id)
            .eq("organization_id", org_id)
            .execute()
        )

        logger.info(
            "team_context_cleared",
            team_id=team_id,
            org_id=org_id,
        )

        return None

    except Exception as e:
        logger.error("clear_team_context_failed", error=str(e), team_id=team_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear team context: {str(e)}"
        )
