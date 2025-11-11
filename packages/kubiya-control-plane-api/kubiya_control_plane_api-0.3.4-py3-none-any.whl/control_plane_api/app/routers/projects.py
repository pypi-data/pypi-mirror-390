"""
Projects router - Jira-style multi-project management.

This router handles project CRUD operations and manages associations
between projects, agents, and teams.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import uuid

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase

logger = structlog.get_logger()

router = APIRouter()


# Pydantic schemas
class ProjectCreate(BaseModel):
    name: str = Field(..., description="Project name")
    key: str = Field(..., description="Short project key (e.g., JIRA, PROJ)", min_length=2, max_length=50)
    description: str | None = Field(None, description="Project description")
    goals: str | None = Field(None, description="Project goals and objectives")
    settings: dict = Field(default_factory=dict, description="Project settings")
    visibility: str = Field("private", description="Project visibility: private or org")
    restrict_to_environment: bool = Field(False, description="Restrict to specific runners/environment")
    policy_ids: List[str] = Field(default_factory=list, description="List of OPA policy IDs for access control")
    default_model: str | None = Field(None, description="Default LLM model for this project")


class ProjectUpdate(BaseModel):
    name: str | None = None
    key: str | None = None
    description: str | None = None
    goals: str | None = None
    settings: dict | None = None
    status: str | None = None
    visibility: str | None = None
    restrict_to_environment: bool | None = None
    policy_ids: List[str] | None = None
    default_model: str | None = None


class ProjectResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    key: str
    description: str | None
    goals: str | None
    settings: dict
    status: str
    visibility: str
    owner_id: str | None
    owner_email: str | None
    restrict_to_environment: bool = False
    policy_ids: List[str] = []
    default_model: str | None = None
    created_at: str
    updated_at: str
    archived_at: str | None

    # Counts
    agent_count: int = 0
    team_count: int = 0


class ProjectAgentAdd(BaseModel):
    agent_id: str = Field(..., description="Agent UUID to add to project")
    role: str | None = Field(None, description="Agent role in project")


class ProjectTeamAdd(BaseModel):
    team_id: str = Field(..., description="Team UUID to add to project")
    role: str | None = Field(None, description="Team role in project")


def ensure_default_project(organization: dict) -> Optional[dict]:
    """
    Ensure the organization has a default project.
    Creates one if it doesn't exist.

    Returns the default project or None if creation failed.
    """
    try:
        client = get_supabase()

        # Check if default project exists
        existing = (
            client.table("projects")
            .select("*")
            .eq("organization_id", organization["id"])
            .eq("key", "DEFAULT")
            .execute()
        )

        if existing.data:
            return existing.data[0]

        # Create default project
        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        default_project = {
            "id": project_id,
            "organization_id": organization["id"],
            "name": "Default",
            "key": "DEFAULT",
            "description": "Default project for agents and teams",
            "settings": {
                "policy_ids": [],
                "default_model": None,
                "goals": None,
                "restrict_to_environment": False
            },
            "status": "active",
            "visibility": "org",
            "owner_id": organization.get("user_id"),
            "owner_email": organization.get("user_email"),
            "created_at": now,
            "updated_at": now,
        }

        result = client.table("projects").insert(default_project).execute()

        if result.data:
            logger.info(
                "default_project_created",
                project_id=project_id,
                org_id=organization["id"],
            )
            return result.data[0]

        return None

    except Exception as e:
        logger.error("ensure_default_project_failed", error=str(e), org_id=organization.get("id"))
        return None


def get_default_project_id(organization: dict) -> Optional[str]:
    """
    Get the default project ID for an organization.
    Creates the default project if it doesn't exist.

    Returns the project ID or None if creation failed.
    """
    project = ensure_default_project(organization)
    return project["id"] if project else None


@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Create a new project"""
    try:
        client = get_supabase()

        # Check if key already exists for this organization
        existing = (
            client.table("projects")
            .select("id")
            .eq("organization_id", organization["id"])
            .eq("key", project_data.key.upper())
            .execute()
        )

        if existing.data:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Project with key '{project_data.key.upper()}' already exists"
            )

        project_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        project_record = {
            "id": project_id,
            "organization_id": organization["id"],
            "name": project_data.name,
            "key": project_data.key.upper(),
            "description": project_data.description,
            # Store policy_ids, default_model, goals, and restrict_to_environment in settings JSON field
            "settings": {
                **project_data.settings,
                "policy_ids": project_data.policy_ids,
                "default_model": project_data.default_model,
                "goals": project_data.goals,
                "restrict_to_environment": project_data.restrict_to_environment
            },
            "status": "active",
            "visibility": project_data.visibility,
            "owner_id": organization.get("user_id"),
            "owner_email": organization.get("user_email"),
            "created_at": now,
            "updated_at": now,
        }

        result = client.table("projects").insert(project_record).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create project"
            )

        project = result.data[0]

        logger.info(
            "project_created",
            project_id=project_id,
            project_key=project["key"],
            org_id=organization["id"],
        )

        # Extract policy_ids, default_model, goals, and restrict_to_environment from settings for response
        policy_ids = project.get("settings", {}).get("policy_ids", [])
        default_model = project.get("settings", {}).get("default_model")
        goals = project.get("settings", {}).get("goals")
        restrict_to_environment = project.get("settings", {}).get("restrict_to_environment", False)

        return ProjectResponse(
            **{**project, "policy_ids": policy_ids, "default_model": default_model, "goals": goals, "restrict_to_environment": restrict_to_environment},
            agent_count=0,
            team_count=0,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("project_creation_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get("/default", response_model=ProjectResponse)
async def get_default_project(
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get the default project for the organization (creates if doesn't exist)"""
    try:
        client = get_supabase()

        # Ensure default project exists
        default_project = ensure_default_project(organization)

        if not default_project:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to get or create default project"
            )

        # Get counts for the default project
        agent_count_result = (
            client.table("project_agents")
            .select("id", count="exact")
            .eq("project_id", default_project["id"])
            .execute()
        )
        agent_count = agent_count_result.count or 0

        team_count_result = (
            client.table("project_teams")
            .select("id", count="exact")
            .eq("project_id", default_project["id"])
            .execute()
        )
        team_count = team_count_result.count or 0

        # Extract settings fields
        policy_ids = default_project.get("settings", {}).get("policy_ids", [])
        default_model = default_project.get("settings", {}).get("default_model")
        goals = default_project.get("settings", {}).get("goals")
        restrict_to_environment = default_project.get("settings", {}).get("restrict_to_environment", False)

        return ProjectResponse(
            **{**default_project, "policy_ids": policy_ids, "default_model": default_model, "goals": goals, "restrict_to_environment": restrict_to_environment},
            agent_count=agent_count,
            team_count=team_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("get_default_project_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get default project: {str(e)}"
        )


@router.get("", response_model=List[ProjectResponse])
async def list_projects(
    request: Request,
    status_filter: str | None = None,
    organization: dict = Depends(get_current_organization),
):
    """List all projects in the organization"""
    try:
        client = get_supabase()

        # Ensure default project exists for this organization
        ensure_default_project(organization)

        # Query projects
        query = client.table("projects").select("*").eq("organization_id", organization["id"])

        if status_filter:
            query = query.eq("status", status_filter)

        query = query.order("created_at", desc=True)
        result = query.execute()

        if not result.data:
            return []

        # Batch fetch all agent counts in one query
        project_ids = [project["id"] for project in result.data]
        agent_counts_result = (
            client.table("project_agents")
            .select("project_id")
            .in_("project_id", project_ids)
            .execute()
        )

        # Count agents per project
        agent_count_map = {}
        for item in agent_counts_result.data or []:
            project_id = item["project_id"]
            agent_count_map[project_id] = agent_count_map.get(project_id, 0) + 1

        # Batch fetch all team counts in one query
        team_counts_result = (
            client.table("project_teams")
            .select("project_id")
            .in_("project_id", project_ids)
            .execute()
        )

        # Count teams per project
        team_count_map = {}
        for item in team_counts_result.data or []:
            project_id = item["project_id"]
            team_count_map[project_id] = team_count_map.get(project_id, 0) + 1

        # Build response with pre-fetched counts
        projects = []
        for project in result.data:
            # Extract policy_ids, default_model, goals, and restrict_to_environment from settings for response
            policy_ids = project.get("settings", {}).get("policy_ids", [])
            default_model = project.get("settings", {}).get("default_model")
            goals = project.get("settings", {}).get("goals")
            restrict_to_environment = project.get("settings", {}).get("restrict_to_environment", False)

            projects.append(
                ProjectResponse(
                    **{**project, "policy_ids": policy_ids, "default_model": default_model, "goals": goals, "restrict_to_environment": restrict_to_environment},
                    agent_count=agent_count_map.get(project["id"], 0),
                    team_count=team_count_map.get(project["id"], 0),
                )
            )

        logger.info(
            "projects_listed",
            count=len(projects),
            org_id=organization["id"],
        )

        return projects

    except Exception as e:
        logger.error("projects_list_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get a specific project by ID"""
    try:
        client = get_supabase()

        result = (
            client.table("projects")
            .select("*")
            .eq("id", project_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Project not found")

        project = result.data

        # Get counts
        agent_count_result = (
            client.table("project_agents")
            .select("id", count="exact")
            .eq("project_id", project_id)
            .execute()
        )
        agent_count = agent_count_result.count or 0

        team_count_result = (
            client.table("project_teams")
            .select("id", count="exact")
            .eq("project_id", project_id)
            .execute()
        )
        team_count = team_count_result.count or 0

        # Extract policy_ids, default_model, goals, and restrict_to_environment from settings for response
        policy_ids = project.get("settings", {}).get("policy_ids", [])
        default_model = project.get("settings", {}).get("default_model")
        goals = project.get("settings", {}).get("goals")
        restrict_to_environment = project.get("settings", {}).get("restrict_to_environment", False)

        return ProjectResponse(
            **{**project, "policy_ids": policy_ids, "default_model": default_model, "goals": goals, "restrict_to_environment": restrict_to_environment},
            agent_count=agent_count,
            team_count=team_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("project_get_failed", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: str,
    project_data: ProjectUpdate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Update a project"""
    try:
        client = get_supabase()

        # Check if project exists
        existing = (
            client.table("projects")
            .select("id")
            .eq("id", project_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not existing.data:
            raise HTTPException(status_code=404, detail="Project not found")

        # Build update dict
        update_data = project_data.model_dump(exclude_unset=True)

        # Handle policy_ids, default_model, goals, and restrict_to_environment - store in settings if provided
        settings_updates = {}
        if "policy_ids" in update_data:
            settings_updates["policy_ids"] = update_data.pop("policy_ids")
        if "default_model" in update_data:
            settings_updates["default_model"] = update_data.pop("default_model")
        if "goals" in update_data:
            settings_updates["goals"] = update_data.pop("goals")
        if "restrict_to_environment" in update_data:
            settings_updates["restrict_to_environment"] = update_data.pop("restrict_to_environment")

        # Apply settings updates if any
        if settings_updates:
            if "settings" in update_data:
                update_data["settings"].update(settings_updates)
            else:
                # Need to merge with existing settings
                existing_project = (
                    client.table("projects")
                    .select("settings")
                    .eq("id", project_id)
                    .single()
                    .execute()
                )
                existing_settings = existing_project.data.get("settings", {}) if existing_project.data else {}
                update_data["settings"] = {**existing_settings, **settings_updates}

        # Uppercase key if provided
        if "key" in update_data:
            update_data["key"] = update_data["key"].upper()

        update_data["updated_at"] = datetime.utcnow().isoformat()

        # Update project
        result = (
            client.table("projects")
            .update(update_data)
            .eq("id", project_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update project"
            )

        project = result.data[0]

        # Get counts
        agent_count_result = (
            client.table("project_agents")
            .select("id", count="exact")
            .eq("project_id", project_id)
            .execute()
        )
        agent_count = agent_count_result.count or 0

        team_count_result = (
            client.table("project_teams")
            .select("id", count="exact")
            .eq("project_id", project_id)
            .execute()
        )
        team_count = team_count_result.count or 0

        logger.info(
            "project_updated",
            project_id=project_id,
            org_id=organization["id"],
        )

        # Extract policy_ids, default_model, goals, and restrict_to_environment from settings for response
        policy_ids = project.get("settings", {}).get("policy_ids", [])
        default_model = project.get("settings", {}).get("default_model")
        goals = project.get("settings", {}).get("goals")
        restrict_to_environment = project.get("settings", {}).get("restrict_to_environment", False)

        return ProjectResponse(
            **{**project, "policy_ids": policy_ids, "default_model": default_model, "goals": goals, "restrict_to_environment": restrict_to_environment},
            agent_count=agent_count,
            team_count=team_count,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("project_update_failed", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Delete a project (cascades to associations)"""
    try:
        client = get_supabase()

        result = (
            client.table("projects")
            .delete()
            .eq("id", project_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Project not found")

        logger.info("project_deleted", project_id=project_id, org_id=organization["id"])

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("project_delete_failed", error=str(e), project_id=project_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )


# Agent associations
@router.post("/{project_id}/agents", status_code=status.HTTP_201_CREATED)
async def add_agent_to_project(
    project_id: str,
    agent_data: ProjectAgentAdd,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Add an agent to a project"""
    try:
        client = get_supabase()

        # Verify project exists
        project_check = (
            client.table("projects")
            .select("id")
            .eq("id", project_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not project_check.data:
            raise HTTPException(status_code=404, detail="Project not found")

        # Verify agent exists and belongs to org
        agent_check = (
            client.table("agents")
            .select("id")
            .eq("id", agent_data.agent_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not agent_check.data:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Add association
        association = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "agent_id": agent_data.agent_id,
            "role": agent_data.role,
            "added_at": datetime.utcnow().isoformat(),
            "added_by": organization.get("user_id"),
        }

        result = client.table("project_agents").insert(association).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add agent to project"
            )

        logger.info(
            "agent_added_to_project",
            project_id=project_id,
            agent_id=agent_data.agent_id,
            org_id=organization["id"],
        )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("add_agent_to_project_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add agent: {str(e)}"
        )


@router.get("/{project_id}/agents")
async def list_project_agents(
    project_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """List all agents in a project"""
    try:
        client = get_supabase()

        # Get project agents with agent details
        result = (
            client.table("project_agents")
            .select("*, agents(*)")
            .eq("project_id", project_id)
            .execute()
        )

        logger.info(
            "project_agents_listed",
            project_id=project_id,
            count=len(result.data),
            org_id=organization["id"],
        )

        return result.data

    except Exception as e:
        logger.error("list_project_agents_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.delete("/{project_id}/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_agent_from_project(
    project_id: str,
    agent_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Remove an agent from a project"""
    try:
        client = get_supabase()

        result = (
            client.table("project_agents")
            .delete()
            .eq("project_id", project_id)
            .eq("agent_id", agent_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Association not found")

        logger.info(
            "agent_removed_from_project",
            project_id=project_id,
            agent_id=agent_id,
            org_id=organization["id"],
        )

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("remove_agent_from_project_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove agent: {str(e)}"
        )


# Team associations (similar to agents)
@router.post("/{project_id}/teams", status_code=status.HTTP_201_CREATED)
async def add_team_to_project(
    project_id: str,
    team_data: ProjectTeamAdd,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Add a team to a project"""
    try:
        client = get_supabase()

        # Verify project and team exist
        project_check = (
            client.table("projects")
            .select("id")
            .eq("id", project_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not project_check.data:
            raise HTTPException(status_code=404, detail="Project not found")

        team_check = (
            client.table("teams")
            .select("id")
            .eq("id", team_data.team_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not team_check.data:
            raise HTTPException(status_code=404, detail="Team not found")

        # Add association
        association = {
            "id": str(uuid.uuid4()),
            "project_id": project_id,
            "team_id": team_data.team_id,
            "role": team_data.role,
            "added_at": datetime.utcnow().isoformat(),
            "added_by": organization.get("user_id"),
        }

        result = client.table("project_teams").insert(association).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add team to project"
            )

        logger.info(
            "team_added_to_project",
            project_id=project_id,
            team_id=team_data.team_id,
            org_id=organization["id"],
        )

        return result.data[0]

    except HTTPException:
        raise
    except Exception as e:
        logger.error("add_team_to_project_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add team: {str(e)}"
        )


@router.get("/{project_id}/teams")
async def list_project_teams(
    project_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """List all teams in a project"""
    try:
        client = get_supabase()

        result = (
            client.table("project_teams")
            .select("*, teams(*)")
            .eq("project_id", project_id)
            .execute()
        )

        logger.info(
            "project_teams_listed",
            project_id=project_id,
            count=len(result.data),
            org_id=organization["id"],
        )

        return result.data

    except Exception as e:
        logger.error("list_project_teams_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list teams: {str(e)}"
        )


@router.delete("/{project_id}/teams/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_team_from_project(
    project_id: str,
    team_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Remove a team from a project"""
    try:
        client = get_supabase()

        result = (
            client.table("project_teams")
            .delete()
            .eq("project_id", project_id)
            .eq("team_id", team_id)
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Association not found")

        logger.info(
            "team_removed_from_project",
            project_id=project_id,
            team_id=team_id,
            org_id=organization["id"],
        )

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("remove_team_from_project_failed", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to remove team: {str(e)}"
        )
