from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Union, Dict, Any, Optional
from datetime import datetime
from enum import Enum
import structlog
import uuid

from control_plane_api.app.database import get_db
from control_plane_api.app.models.team import Team
from control_plane_api.app.models.agent import Agent
from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase
from control_plane_api.app.lib.temporal_client import get_temporal_client
from control_plane_api.app.workflows.agent_execution import AgentExecutionWorkflow, TeamExecutionInput
from control_plane_api.app.workflows.team_execution import TeamExecutionWorkflow
from control_plane_api.app.routers.projects import get_default_project_id
from control_plane_api.app.routers.agents_v2 import ExecutionEnvironment
from pydantic import BaseModel, Field

logger = structlog.get_logger()

router = APIRouter()


# Team status enum
class TeamStatus(str, Enum):
    """Team status enumeration"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


def get_entity_skills(client, organization_id: str, entity_type: str, entity_id: str) -> List[dict]:
    """Get skills associated with an entity"""
    # Get associations
    result = (
        client.table("skill_associations")
        .select("skill_id, configuration_override, skills(*)")
        .eq("organization_id", organization_id)
        .eq("entity_type", entity_type)
        .eq("entity_id", entity_id)
        .execute()
    )

    skills = []
    for item in result.data:
        skill_data = item.get("skills")
        if skill_data and skill_data.get("enabled", True):
            # Merge configuration with override
            config = skill_data.get("configuration", {})
            override = item.get("configuration_override")
            if override:
                config = {**config, **override}

            skills.append({
                "id": skill_data["id"],
                "name": skill_data["name"],
                "type": skill_data["skill_type"],
                "description": skill_data.get("description"),
                "enabled": skill_data.get("enabled", True),
                "configuration": config,
            })

    return skills


def get_team_projects(db, team_id: str) -> list[dict]:
    """Get all projects a team belongs to"""
    try:
        from control_plane_api.app.lib.supabase import get_supabase
        client = get_supabase()

        # Query project_teams join table
        result = (
            client.table("project_teams")
            .select("project_id, projects(id, name, key, description)")
            .eq("team_id", team_id)
            .execute()
        )

        projects = []
        for item in result.data:
            project_data = item.get("projects")
            if project_data:
                projects.append({
                    "id": project_data["id"],
                    "name": project_data["name"],
                    "key": project_data["key"],
                    "description": project_data.get("description"),
                })

        return projects
    except Exception as e:
        logger.warning("failed_to_fetch_team_projects", error=str(e), team_id=team_id)
        return []


# Enhanced Pydantic schemas aligned with Agno Team capabilities

class ReasoningConfig(BaseModel):
    """Reasoning configuration for the team"""
    enabled: bool = Field(False, description="Enable reasoning for the team")
    model: Optional[str] = Field(None, description="Model to use for reasoning")
    agent_id: Optional[str] = Field(None, description="Agent ID to use for reasoning")
    min_steps: Optional[int] = Field(1, description="Minimum reasoning steps", ge=1)
    max_steps: Optional[int] = Field(10, description="Maximum reasoning steps", ge=1, le=100)


class LLMConfig(BaseModel):
    """LLM configuration for the team"""
    model: Optional[str] = Field(None, description="Default model for the team")
    temperature: Optional[float] = Field(None, description="Temperature for generation", ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate", ge=1)
    top_p: Optional[float] = Field(None, description="Top-p sampling", ge=0.0, le=1.0)
    top_k: Optional[int] = Field(None, description="Top-k sampling", ge=0)
    stop: Optional[List[str]] = Field(None, description="Stop sequences")
    frequency_penalty: Optional[float] = Field(None, description="Frequency penalty", ge=-2.0, le=2.0)
    presence_penalty: Optional[float] = Field(None, description="Presence penalty", ge=-2.0, le=2.0)


class SessionConfig(BaseModel):
    """Session configuration for the team"""
    user_id: Optional[str] = Field(None, description="User ID for the session")
    session_id: Optional[str] = Field(None, description="Session ID")
    auto_save: bool = Field(True, description="Auto-save session state")
    persist: bool = Field(True, description="Persist session across runs")


class TeamConfiguration(BaseModel):
    """
    Comprehensive team configuration aligned with Agno's Team capabilities.
    This allows full control over team behavior, reasoning, tools, and LLM settings.
    """
    # Members
    member_ids: List[str] = Field(default_factory=list, description="List of agent IDs in the team")

    # Instructions
    instructions: Union[str, List[str]] = Field(
        default="",
        description="Instructions for the team - can be a single string or list of instructions"
    )

    # Reasoning
    reasoning: Optional[ReasoningConfig] = Field(None, description="Reasoning configuration")

    # LLM Configuration
    llm: Optional[LLMConfig] = Field(None, description="LLM configuration for the team")

    # Tools & Knowledge
    tools: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Tools available to the team - list of tool configurations"
    )
    knowledge_base: Optional[Dict[str, Any]] = Field(
        None,
        description="Knowledge base configuration (vector store, embeddings, etc.)"
    )

    # Session & State
    session: Optional[SessionConfig] = Field(None, description="Session configuration")
    dependencies: Dict[str, Any] = Field(
        default_factory=dict,
        description="External dependencies (databases, APIs, services)"
    )

    # Advanced Options
    markdown: bool = Field(True, description="Enable markdown formatting in responses")
    add_datetime_to_instructions: bool = Field(
        False,
        description="Automatically add current datetime to instructions"
    )
    structured_outputs: bool = Field(False, description="Enable structured outputs")
    response_model: Optional[str] = Field(None, description="Response model schema name")

    # Monitoring & Debugging
    debug_mode: bool = Field(False, description="Enable debug mode with verbose logging")
    monitoring: bool = Field(False, description="Enable monitoring and telemetry")

    # Custom Metadata
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional custom metadata for the team"
    )


class TeamCreate(BaseModel):
    """Create a new team with full Agno capabilities"""
    name: str = Field(..., description="Team name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Team description")
    configuration: TeamConfiguration = Field(
        default_factory=TeamConfiguration,
        description="Team configuration aligned with Agno Team"
    )
    skill_ids: list[str] = Field(default_factory=list, description="Tool set IDs to associate with this team")
    skill_configurations: dict[str, dict] = Field(default_factory=dict, description="Tool set configurations keyed by skill ID")
    execution_environment: ExecutionEnvironment | None = Field(None, description="Execution environment: env vars, secrets, integrations")


class TeamUpdate(BaseModel):
    """Update an existing team"""
    name: Optional[str] = Field(None, description="Team name", min_length=1, max_length=255)
    description: Optional[str] = Field(None, description="Team description")
    status: Optional[TeamStatus] = Field(None, description="Team status")
    runtime: Optional[str] = Field(None, description="Runtime type: 'default' (Agno) or 'claude_code' (Claude Code SDK)")
    configuration: Optional[TeamConfiguration] = Field(None, description="Team configuration")
    skill_ids: list[str] | None = None
    skill_configurations: dict[str, dict] | None = None
    environment_ids: list[str] | None = None
    execution_environment: ExecutionEnvironment | None = None


class TeamResponse(BaseModel):
    """Team response with structured configuration"""
    id: str
    organization_id: str
    name: str
    description: Optional[str]
    status: TeamStatus
    configuration: TeamConfiguration
    created_at: datetime
    updated_at: datetime
    projects: List[dict] = Field(default_factory=list, description="Projects this team belongs to")
    skill_ids: Optional[List[str]] = Field(default_factory=list, description="IDs of associated skills")
    skills: Optional[List[dict]] = Field(default_factory=list, description="Associated skills with details")
    execution_environment: ExecutionEnvironment | None = None

    class Config:
        from_attributes = True


class TeamWithAgentsResponse(TeamResponse):
    """Team response including member agents"""
    agents: List[dict]


class TeamExecutionRequest(BaseModel):
    prompt: str = Field(..., description="The prompt/task to execute")
    system_prompt: str | None = Field(None, description="Optional system prompt for team coordination")
    stream: bool = Field(False, description="Whether to stream the response")
    worker_queue_id: str = Field(..., description="Worker queue ID (UUID) to route execution to - REQUIRED")
    user_metadata: dict | None = Field(None, description="User attribution metadata (optional, auto-filled from token)")


class TeamExecutionResponse(BaseModel):
    execution_id: str
    workflow_id: str
    status: str
    message: str


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(
    team_data: TeamCreate,
    request: Request,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """
    Create a new team with full Agno capabilities.

    Supports comprehensive configuration including:
    - Member agents
    - Instructions and reasoning
    - Tools and knowledge bases
    - LLM settings
    - Session management
    """
    try:
        logger.info(
            "create_team_request",
            team_name=team_data.name,
            org_id=organization["id"],
            org_name=organization.get("name"),
            member_count=len(team_data.configuration.member_ids) if team_data.configuration.member_ids else 0,
            skill_count=len(team_data.skill_ids) if team_data.skill_ids else 0,
        )

        # Check if team name already exists in this organization
        existing_team = db.query(Team).filter(
            Team.name == team_data.name,
            Team.organization_id == organization["id"]
        ).first()
        if existing_team:
            logger.warning(
                "team_name_already_exists",
                team_name=team_data.name,
                org_id=organization["id"],
            )
            raise HTTPException(status_code=400, detail="Team with this name already exists in your organization")

        # Validate member_ids if provided
        if team_data.configuration.member_ids:
            client = get_supabase()
            logger.info(
                "validating_team_members",
                member_ids=team_data.configuration.member_ids,
                org_id=organization["id"],
            )
            for agent_id in team_data.configuration.member_ids:
                try:
                    # Query Supabase instead of local DB for consistency with GET /agents
                    result = (
                        client.table("agents")
                        .select("id")
                        .eq("id", agent_id)
                        .eq("organization_id", organization["id"])
                        .maybe_single()
                        .execute()
                    )

                    logger.debug(
                        "agent_validation_result",
                        agent_id=agent_id,
                        result_type=type(result).__name__,
                        has_data=hasattr(result, 'data') if result else False,
                    )

                    if not result or not hasattr(result, 'data') or not result.data:
                        logger.warning(
                            "agent_not_found",
                            agent_id=agent_id,
                            org_id=organization["id"],
                            result_is_none=result is None,
                        )
                        raise HTTPException(
                            status_code=400,
                            detail=f"Agent with ID '{agent_id}' not found. Please create the agent first."
                        )
                except HTTPException:
                    raise
                except Exception as e:
                    logger.error(
                        "agent_validation_failed",
                        agent_id=agent_id,
                        error=str(e),
                        error_type=type(e).__name__,
                        org_id=organization["id"],
                    )
                    raise HTTPException(
                        status_code=500,
                        detail=f"Failed to validate agent '{agent_id}': {str(e)}"
                    )

        # Convert TeamConfiguration to dict for JSON storage
        configuration_dict = team_data.configuration.model_dump(exclude_none=True)

        team = Team(
            organization_id=organization["id"],
            name=team_data.name,
            description=team_data.description,
            configuration=configuration_dict,
            skill_ids=team_data.skill_ids,
            execution_environment=team_data.execution_environment.model_dump() if team_data.execution_environment else {},
        )
        db.add(team)
        db.commit()
        db.refresh(team)

        logger.info(
            "team_created",
            team_id=str(team.id),
            team_name=team.name,
            org_id=organization["id"],
        )
    except HTTPException:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(
            "database_integrity_error",
            error=str(e),
            team_name=team_data.name,
            org_id=organization["id"],
        )
        raise HTTPException(
            status_code=400,
            detail=f"Database constraint violation: {str(e.orig) if hasattr(e, 'orig') else str(e)}"
        )
    except Exception as e:
        db.rollback()
        logger.error(
            "team_creation_failed",
            error=str(e),
            error_type=type(e).__name__,
            team_name=team_data.name,
            org_id=organization["id"],
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create team: {str(e)}"
        )

    # Sync agent.team_id relationship for initial members in Supabase
    if team_data.configuration.member_ids:
        client = get_supabase()
        for agent_id in team_data.configuration.member_ids:
            try:
                client.table("agents").update({"team_id": str(team.id)}).eq("id", agent_id).execute()
            except Exception as e:
                logger.warning(
                    "failed_to_sync_agent_team_id",
                    error=str(e),
                    agent_id=agent_id,
                    team_id=str(team.id)
                )

    # Automatically assign team to the default project
    default_project_id = get_default_project_id(organization)
    if default_project_id:
        try:
            client = get_supabase()
            project_team_record = {
                "id": str(uuid.uuid4()),
                "project_id": default_project_id,
                "team_id": str(team.id),
                "role": None,
                "added_at": datetime.utcnow().isoformat(),
                "added_by": organization.get("user_id"),
            }
            client.table("project_teams").insert(project_team_record).execute()
            logger.info(
                "team_added_to_default_project",
                team_id=str(team.id),
                project_id=default_project_id,
                org_id=organization["id"]
            )
        except Exception as e:
            logger.warning(
                "failed_to_add_team_to_default_project",
                error=str(e),
                team_id=str(team.id),
                org_id=organization["id"]
            )

    # Create skill associations if skills were provided
    if team_data.skill_ids:
        try:
            client = get_supabase()
            now = datetime.utcnow().isoformat()

            for skill_id in team_data.skill_ids:
                association_id = str(uuid.uuid4())
                config_override = team_data.skill_configurations.get(skill_id, {})

                association_record = {
                    "id": association_id,
                    "organization_id": organization["id"],
                    "skill_id": skill_id,
                    "entity_type": "team",
                    "entity_id": str(team.id),
                    "configuration_override": config_override,
                    "created_at": now,
                }

                client.table("skill_associations").insert(association_record).execute()

            logger.info(
                "team_skills_associated",
                team_id=str(team.id),
                skill_count=len(team_data.skill_ids),
                org_id=organization["id"]
            )
        except Exception as e:
            logger.warning(
                "failed_to_associate_team_skills",
                error=str(e),
                team_id=str(team.id),
                org_id=organization["id"]
            )

    # Parse configuration back to TeamConfiguration for response
    response_team = TeamResponse(
        id=str(team.id),
        organization_id=team.organization_id,
        name=team.name,
        description=team.description,
        status=team.status,
        configuration=TeamConfiguration(**team.configuration),
        created_at=team.created_at,
        updated_at=team.updated_at,
        projects=get_team_projects(db, str(team.id)),
    )
    return response_team


@router.get("", response_model=List[TeamWithAgentsResponse])
def list_teams(
    skip: int = 0,
    limit: int = 100,
    status_filter: Optional[TeamStatus] = None,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """
    List all teams with their configurations and member agents.

    Supports filtering by status and pagination.
    Only returns teams belonging to the current organization.
    """
    try:
        query = db.query(Team).filter(Team.organization_id == organization["id"])
        if status_filter:
            query = query.filter(Team.status == status_filter)
        teams = query.offset(skip).limit(limit).all()

        if not teams:
            return []

        client = get_supabase()
        team_ids = [str(team.id) for team in teams]

        # BATCH 1: Fetch all projects for all teams in one query
        try:
            projects_result = (
                client.table("project_teams")
                .select("team_id, projects(id, name, key, description)")
                .in_("team_id", team_ids)
                .execute()
            )
        except Exception as project_error:
            logger.error("failed_to_fetch_projects", error=str(project_error), org_id=organization["id"])
            projects_result = type('obj', (object,), {'data': []})  # Empty result object

        # Group projects by team_id
        projects_by_team = {}
        for item in projects_result.data or []:
            team_id = item["team_id"]
            project_data = item.get("projects")
            if project_data:
                if team_id not in projects_by_team:
                    projects_by_team[team_id] = []
                projects_by_team[team_id].append({
                    "id": project_data["id"],
                    "name": project_data["name"],
                    "key": project_data["key"],
                    "description": project_data.get("description"),
                })

        # BATCH 2: Fetch all skill associations for all teams in one query
        try:
            skills_result = (
                client.table("skill_associations")
                .select("entity_id, skill_id, configuration_override, skills(*)")
                .eq("organization_id", organization["id"])
                .eq("entity_type", "team")
                .in_("entity_id", team_ids)
                .execute()
            )
        except Exception as skill_error:
            logger.error("failed_to_fetch_skills", error=str(skill_error), org_id=organization["id"])
            skills_result = type('obj', (object,), {'data': []})  # Empty result object

        # Group skills by team_id
        skills_by_team = {}
        for item in skills_result.data or []:
            team_id = item["entity_id"]
            skill_data = item.get("skills")
            if skill_data and skill_data.get("enabled", True):
                if team_id not in skills_by_team:
                    skills_by_team[team_id] = []

                # Merge configuration with override
                config = skill_data.get("configuration", {})
                override = item.get("configuration_override")
                if override:
                    config = {**config, **override}

                skills_by_team[team_id].append({
                    "id": skill_data["id"],
                    "name": skill_data["name"],
                    "type": skill_data["skill_type"],
                    "description": skill_data.get("description"),
                    "enabled": skill_data.get("enabled", True),
                    "configuration": config,
                })

        # BATCH 3: Collect all unique agent IDs from all teams
        all_agent_ids = set()
        for team in teams:
            try:
                team_config = TeamConfiguration(**(team.configuration or {}))
                if team_config.member_ids:
                    all_agent_ids.update(team_config.member_ids)
            except Exception as config_error:
                logger.warning("failed_to_parse_team_config", error=str(config_error), team_id=str(team.id))

        # Fetch all agents in one query
        agents_by_id = {}
        if all_agent_ids:
            try:
                db_agents = db.query(Agent).filter(Agent.id.in_(list(all_agent_ids))).all()
                agents_by_id = {
                    str(agent.id): {
                        "id": str(agent.id),
                        "name": agent.name,
                        "status": agent.status,
                        "capabilities": agent.capabilities,
                        "description": agent.description,
                    }
                    for agent in db_agents
                }
            except Exception as agent_error:
                logger.error("failed_to_fetch_agents", error=str(agent_error), org_id=organization["id"])

        # Build response for each team
        result = []
        for team in teams:
            try:
                team_id = str(team.id)
                team_config = TeamConfiguration(**(team.configuration or {}))

                # Get agents for this team from the batched data
                agents = []
                if team_config.member_ids:
                    agents = [agents_by_id[agent_id] for agent_id in team_config.member_ids if agent_id in agents_by_id]

                # Get skills from batched data
                skills = skills_by_team.get(team_id, [])
                skill_ids = [ts["id"] for ts in skills]

                result.append(TeamWithAgentsResponse(
                    id=team_id,
                    organization_id=team.organization_id,
                    name=team.name,
                    description=team.description,
                    status=team.status,
                    configuration=team_config,
                    created_at=team.created_at,
                    updated_at=team.updated_at,
                    projects=projects_by_team.get(team_id, []),
                    agents=agents,
                    skill_ids=skill_ids,
                    skills=skills,
                ))
            except Exception as team_error:
                logger.error("failed_to_build_team_response", error=str(team_error), team_id=str(team.id))
                # Skip this team and continue with others

        logger.info(
            "teams_listed_successfully",
            count=len(result),
            org_id=organization["id"],
        )

        return result

    except Exception as e:
        logger.error(
            "teams_list_failed",
            error=str(e),
            error_type=type(e).__name__,
            org_id=organization["id"]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list teams: {str(e)}"
        )


@router.get("/{team_id}", response_model=TeamWithAgentsResponse)
def get_team(
    team_id: str,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """
    Get a specific team by ID with full configuration and member agents.

    Returns the team with structured configuration and list of member agents.
    Only returns teams belonging to the current organization.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == organization["id"]
    ).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Parse configuration
    team_config = TeamConfiguration(**(team.configuration or {}))

    # Get agents from configuration.member_ids (source of truth)
    # instead of team.agents relationship to avoid ghost agents
    member_ids = team_config.member_ids
    agents = []
    if member_ids:
        # Query agents that actually exist in the database
        db_agents = db.query(Agent).filter(Agent.id.in_(member_ids)).all()
        agents = [
            {
                "id": str(agent.id),
                "name": agent.name,
                "status": agent.status,
                "capabilities": agent.capabilities,
                "description": agent.description,
            }
            for agent in db_agents
        ]

    # Get skills for this team
    client = get_supabase()
    skills = get_entity_skills(client, organization["id"], "team", team_id)
    skill_ids = [ts["id"] for ts in skills]

    # Include agents in response
    return TeamWithAgentsResponse(
        id=str(team.id),
        organization_id=team.organization_id,
        name=team.name,
        description=team.description,
        status=team.status,
        configuration=team_config,
        created_at=team.created_at,
        updated_at=team.updated_at,
        projects=get_team_projects(db, team_id),
        agents=agents,
        skill_ids=skill_ids,
        skills=skills,
    )


@router.patch("/{team_id}", response_model=TeamResponse)
def update_team(
    team_id: str,
    team_data: TeamUpdate,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """
    Update a team's configuration, name, description, or status.

    Supports partial updates - only provided fields are updated.
    Validates member_ids if configuration is being updated.
    Only allows updating teams belonging to the current organization.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == organization["id"]
    ).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    update_data = team_data.model_dump(exclude_unset=True)

    # Extract skill data before processing
    skill_ids = update_data.pop("skill_ids", None)
    skill_configurations = update_data.pop("skill_configurations", None)

    # Extract environment data before processing (many-to-many via junction table)
    environment_ids = update_data.pop("environment_ids", None)

    # Handle execution_environment - convert to dict if present
    if "execution_environment" in update_data and update_data["execution_environment"]:
        if isinstance(update_data["execution_environment"], ExecutionEnvironment):
            update_data["execution_environment"] = update_data["execution_environment"].model_dump()
        # If None, keep as None to preserve existing value

    logger.info(
        "team_update_request",
        team_id=team_id,
        has_skill_ids=skill_ids is not None,
        skill_count=len(skill_ids) if skill_ids else 0,
        skill_ids=skill_ids,
    )

    # Check if name is being updated and if it already exists
    if "name" in update_data and update_data["name"] != team.name:
        existing_team = db.query(Team).filter(Team.name == update_data["name"]).first()
        if existing_team:
            raise HTTPException(status_code=400, detail="Team with this name already exists")

    # Handle configuration update specially
    if "configuration" in update_data and update_data["configuration"]:
        new_config = update_data["configuration"]

        # new_config is already a dict from model_dump(exclude_unset=True)
        # Validate member_ids if provided and sync the agent.team_id relationship
        if isinstance(new_config, dict) and 'member_ids' in new_config:
            new_member_ids = set(new_config.get('member_ids', []))
            client = get_supabase()

            # Validate all agent IDs exist in Supabase
            for agent_id in new_member_ids:
                result = (
                    client.table("agents")
                    .select("id")
                    .eq("id", agent_id)
                    .eq("organization_id", organization["id"])
                    .maybe_single()
                    .execute()
                )
                if not result.data:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Agent with ID '{agent_id}' not found. Please create the agent first."
                    )

            # Sync the agent.team_id relationship in Supabase
            # Get current team members from configuration
            current_config = TeamConfiguration(**(team.configuration or {}))
            current_member_ids = set(current_config.member_ids or [])

            # Remove agents that are no longer in the team
            agents_to_remove = current_member_ids - new_member_ids
            for agent_id in agents_to_remove:
                try:
                    client.table("agents").update({"team_id": None}).eq("id", agent_id).execute()
                except Exception as e:
                    logger.warning("failed_to_remove_agent_from_team", error=str(e), agent_id=agent_id)

            # Add agents that are newly added to the team
            agents_to_add = new_member_ids - current_member_ids
            for agent_id in agents_to_add:
                try:
                    client.table("agents").update({"team_id": team_id}).eq("id", agent_id).execute()
                except Exception as e:
                    logger.warning("failed_to_add_agent_to_team", error=str(e), agent_id=agent_id)

        # new_config is already a dict, just assign it
        team.configuration = new_config
        del update_data["configuration"]

    # Update other fields
    for field, value in update_data.items():
        if hasattr(team, field):
            setattr(team, field, value)

    # Update skill_ids if provided
    if skill_ids is not None:
        team.skill_ids = skill_ids

    team.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(team)

    # Update skill associations if skill_ids was provided
    if skill_ids is not None:
        try:
            client = get_supabase()

            # Delete existing associations
            client.table("skill_associations").delete().eq("entity_type", "team").eq("entity_id", team_id).execute()

            # Create new associations
            now = datetime.utcnow().isoformat()
            for skill_id in skill_ids:
                association_id = str(uuid.uuid4())
                config_override = (skill_configurations or {}).get(skill_id, {})

                association_record = {
                    "id": association_id,
                    "organization_id": organization["id"],
                    "skill_id": skill_id,
                    "entity_type": "team",
                    "entity_id": team_id,
                    "configuration_override": config_override,
                    "created_at": now,
                }

                client.table("skill_associations").insert(association_record).execute()

            logger.info(
                "team_skills_updated",
                team_id=team_id,
                skill_count=len(skill_ids),
                org_id=organization["id"]
            )
        except Exception as e:
            logger.warning(
                "failed_to_update_team_skills",
                error=str(e),
                team_id=team_id,
                org_id=organization["id"]
            )

    # Update environment associations if environment_ids was provided
    if environment_ids is not None:
        try:
            client = get_supabase()

            # Delete existing environment associations
            client.table("team_environments").delete().eq("team_id", team_id).execute()

            # Create new environment associations
            for environment_id in environment_ids:
                env_association_record = {
                    "id": str(uuid.uuid4()),
                    "team_id": team_id,
                    "environment_id": environment_id,
                    "organization_id": organization["id"],
                    "assigned_at": datetime.utcnow().isoformat(),
                }
                client.table("team_environments").insert(env_association_record).execute()

            logger.info(
                "team_environments_updated",
                team_id=team_id,
                environment_count=len(environment_ids),
                org_id=organization["id"]
            )
        except Exception as e:
            logger.warning(
                "failed_to_update_team_environments",
                error=str(e),
                team_id=team_id,
                org_id=organization["id"]
            )

    # Return with parsed configuration
    return TeamResponse(
        id=str(team.id),
        organization_id=team.organization_id,
        name=team.name,
        description=team.description,
        status=team.status,
        configuration=TeamConfiguration(**(team.configuration or {})),
        created_at=team.created_at,
        updated_at=team.updated_at,
        projects=get_team_projects(db, team_id),
    )


@router.delete("/{team_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_team(
    team_id: str,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """Delete a team - only if it belongs to the current organization"""
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == organization["id"]
    ).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    db.delete(team)
    db.commit()
    return None


@router.post("/{team_id}/agents/{agent_id}", response_model=TeamWithAgentsResponse)
def add_agent_to_team(
    team_id: str,
    agent_id: str,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """
    Add an agent to a team.

    This sets the agent's team_id foreign key. You can also manage members
    through the team's configuration.member_ids field.
    Only allows adding agents to teams belonging to the current organization.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == organization["id"]
    ).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.organization_id == organization["id"]
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    agent.team_id = team_id
    db.commit()
    db.refresh(team)

    # Parse configuration
    team_config = TeamConfiguration(**(team.configuration or {}))

    # Get agents from configuration.member_ids (source of truth)
    member_ids = team_config.member_ids
    agents = []
    if member_ids:
        db_agents = db.query(Agent).filter(Agent.id.in_(member_ids)).all()
        agents = [
            {
                "id": str(a.id),
                "name": a.name,
                "status": a.status,
                "capabilities": a.capabilities,
                "description": a.description,
            }
            for a in db_agents
        ]

    # Return team with agents
    return TeamWithAgentsResponse(
        id=str(team.id),
        organization_id=team.organization_id,
        name=team.name,
        description=team.description,
        status=team.status,
        configuration=team_config,
        created_at=team.created_at,
        updated_at=team.updated_at,
        agents=agents,
    )


@router.delete("/{team_id}/agents/{agent_id}", response_model=TeamWithAgentsResponse)
def remove_agent_from_team(
    team_id: str,
    agent_id: str,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """
    Remove an agent from a team.

    This clears the agent's team_id foreign key.
    Only allows removing agents from teams belonging to the current organization.
    """
    team = db.query(Team).filter(
        Team.id == team_id,
        Team.organization_id == organization["id"]
    ).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    agent = db.query(Agent).filter(
        Agent.id == agent_id,
        Agent.team_id == team_id,
        Agent.organization_id == organization["id"]
    ).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found in this team")

    agent.team_id = None
    db.commit()
    db.refresh(team)

    # Parse configuration
    team_config = TeamConfiguration(**(team.configuration or {}))

    # Get agents from configuration.member_ids (source of truth)
    member_ids = team_config.member_ids
    agents = []
    if member_ids:
        db_agents = db.query(Agent).filter(Agent.id.in_(member_ids)).all()
        agents = [
            {
                "id": str(a.id),
                "name": a.name,
                "status": a.status,
                "capabilities": a.capabilities,
                "description": a.description,
            }
            for a in db_agents
        ]

    # Return team with agents
    return TeamWithAgentsResponse(
        id=str(team.id),
        organization_id=team.organization_id,
        name=team.name,
        description=team.description,
        status=team.status,
        configuration=team_config,
        created_at=team.created_at,
        updated_at=team.updated_at,
        agents=agents,
    )


@router.post("/{team_id}/execute", response_model=TeamExecutionResponse)
async def execute_team(
    team_id: str,
    execution_request: TeamExecutionRequest,
    request: Request,
    db: Session = Depends(get_db),
    organization: dict = Depends(get_current_organization),
):
    """
    Execute a team task by submitting to Temporal workflow.

    This creates an execution record and starts a Temporal workflow.
    The actual execution happens asynchronously on the Temporal worker.

    The runner_name should come from the Composer UI where user selects
    from available runners (fetched from Kubiya API /api/v1/runners).
    """
    try:
        # Get team details from local DB
        team = db.query(Team).filter(
            Team.id == team_id,
            Team.organization_id == organization["id"]
        ).first()

        if not team:
            raise HTTPException(status_code=404, detail="Team not found")

        # Parse team configuration
        team_config = TeamConfiguration(**(team.configuration or {}))

        # Validate and get worker queue
        worker_queue_id = execution_request.worker_queue_id

        client = get_supabase()
        queue_result = (
            client.table("worker_queues")
            .select("*")
            .eq("id", worker_queue_id)
            .eq("organization_id", organization["id"])
            .maybe_single()
            .execute()
        )

        if not queue_result.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Worker queue '{worker_queue_id}' not found. Please select a valid worker queue."
            )

        worker_queue = queue_result.data

        # Check if queue has active workers
        if worker_queue.get("status") != "active":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Worker queue '{worker_queue.get('name')}' is not active"
            )

        # Extract user metadata - ALWAYS use JWT-decoded organization data as source of truth
        user_metadata = execution_request.user_metadata or {}
        # Override with JWT data (user can't spoof their identity)
        user_metadata["user_id"] = organization.get("user_id")
        user_metadata["user_email"] = organization.get("user_email")
        user_metadata["user_name"] = organization.get("user_name")
        # Keep user_avatar from request if provided (not in JWT)
        if not user_metadata.get("user_avatar"):
            user_metadata["user_avatar"] = None

        logger.info(
            "execution_user_metadata",
            user_id=user_metadata.get("user_id"),
            user_name=user_metadata.get("user_name"),
            user_email=user_metadata.get("user_email"),
            org_id=organization.get("id"),
        )

        # Create execution record in Supabase
        execution_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        execution_record = {
            "id": execution_id,
            "organization_id": organization["id"],
            "execution_type": "TEAM",
            "entity_id": team_id,
            "entity_name": team.name,
            "prompt": execution_request.prompt,
            "system_prompt": execution_request.system_prompt,
            "status": "PENDING",
            "worker_queue_id": worker_queue_id,
            "runner_name": worker_queue.get("name"),  # Store queue name for display
            "user_id": user_metadata.get("user_id"),
            "user_name": user_metadata.get("user_name"),
            "user_email": user_metadata.get("user_email"),
            "user_avatar": user_metadata.get("user_avatar"),
            "usage": {},
            "execution_metadata": {
                "kubiya_org_id": organization["id"],
                "kubiya_org_name": organization["name"],
                "worker_queue_name": worker_queue.get("display_name") or worker_queue.get("name"),
                "team_execution": True,
            },
            "created_at": now,
            "updated_at": now,
        }

        exec_result = client.table("executions").insert(execution_record).execute()

        if not exec_result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create execution record"
            )

        # Add creator as the first participant (owner role) for multiplayer support
        user_id = user_metadata.get("user_id")
        if user_id:
            try:
                import uuid as uuid_lib
                client.table("execution_participants").insert({
                    "id": str(uuid_lib.uuid4()),
                    "execution_id": execution_id,
                    "organization_id": organization["id"],
                    "user_id": user_id,
                    "user_name": user_metadata.get("user_name"),
                    "user_email": user_metadata.get("user_email"),
                    "user_avatar": user_metadata.get("user_avatar"),
                    "role": "owner",
                }).execute()
                logger.info(
                    "owner_participant_added",
                    execution_id=execution_id,
                    user_id=user_id,
                )
            except Exception as participant_error:
                logger.warning(
                    "failed_to_add_owner_participant",
                    error=str(participant_error),
                    execution_id=execution_id,
                )
                # Don't fail execution creation if participant tracking fails

        # Extract MCP servers from team configuration if available
        mcp_servers = team_config.metadata.get("mcpServers", {}) if team_config.metadata else {}

        # Use LLM config from team configuration if available
        model_id = team_config.llm.model if team_config.llm and team_config.llm.model else "kubiya/claude-sonnet-4"

        # Build model config from LLM configuration
        model_config = {}
        if team_config.llm:
            if team_config.llm.temperature is not None:
                model_config["temperature"] = team_config.llm.temperature
            if team_config.llm.max_tokens is not None:
                model_config["max_tokens"] = team_config.llm.max_tokens
            if team_config.llm.top_p is not None:
                model_config["top_p"] = team_config.llm.top_p
            if team_config.llm.stop is not None:
                model_config["stop"] = team_config.llm.stop
            if team_config.llm.frequency_penalty is not None:
                model_config["frequency_penalty"] = team_config.llm.frequency_penalty
            if team_config.llm.presence_penalty is not None:
                model_config["presence_penalty"] = team_config.llm.presence_penalty

        # Submit to Temporal workflow
        # Task queue is the worker queue UUID
        task_queue = worker_queue_id

        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Start workflow
        # Use team instructions as fallback system prompt if not provided in request
        system_prompt = execution_request.system_prompt
        if not system_prompt and team_config.instructions:
            # Convert instructions to string if it's a list
            if isinstance(team_config.instructions, list):
                system_prompt = "\n".join(team_config.instructions)
            else:
                system_prompt = team_config.instructions

        # Get API key from Authorization header
        auth_header = request.headers.get("authorization", "")
        api_key = auth_header.replace("UserKey ", "").replace("Bearer ", "") if auth_header else None

        # Get control plane URL from request
        control_plane_url = str(request.base_url).rstrip("/")

        workflow_input = TeamExecutionInput(
            execution_id=execution_id,
            team_id=team_id,
            organization_id=organization["id"],
            prompt=execution_request.prompt,
            system_prompt=system_prompt,
            model_id=model_id,
            model_config=model_config,
            team_config=team.configuration,
            mcp_servers=mcp_servers,
            user_metadata=user_metadata,
            runtime_type=team.runtime.value if team.runtime else "default",
            control_plane_url=control_plane_url,
            api_key=api_key,
        )

        workflow_handle = await temporal_client.start_workflow(
            TeamExecutionWorkflow.run,
            workflow_input,  # Pass TeamExecutionInput directly
            id=f"team-execution-{execution_id}",
            task_queue=task_queue,
        )

        logger.info(
            "team_execution_submitted",
            execution_id=execution_id,
            team_id=team_id,
            workflow_id=workflow_handle.id,
            task_queue=task_queue,
            worker_queue_id=worker_queue_id,
            worker_queue_name=worker_queue.get("name"),
            org_id=organization["id"],
            org_name=organization["name"],
        )

        return TeamExecutionResponse(
            execution_id=execution_id,
            workflow_id=workflow_handle.id,
            status="PENDING",
            message=f"Execution submitted to worker queue: {worker_queue.get('name')}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "team_execution_failed",
            error=str(e),
            team_id=team_id,
            org_id=organization["id"]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute team: {str(e)}"
        )


@router.post("/{team_id}/execute/stream")
def execute_team_stream(
    team_id: str,
    execution_request: TeamExecutionRequest,
    db: Session = Depends(get_db),
):
    """
    Execute a team task with streaming response.

    The team leader coordinates and delegates the task to appropriate team members.
    Results are streamed back in real-time.
    """
    from control_plane_api.app.services.litellm_service import litellm_service

    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Get team agents
    agents = team.agents
    if not agents:
        raise HTTPException(
            status_code=400,
            detail="Team has no agents. Add agents to the team before executing tasks."
        )

    # Build team coordination prompt
    agent_descriptions = []
    for agent in agents:
        caps = ", ".join(agent.capabilities) if agent.capabilities else "general"
        agent_descriptions.append(
            f"- {agent.name}: {agent.description or 'No description'} (Capabilities: {caps})"
        )

    # Create a coordination system prompt
    coordination_prompt = f"""You are a Team Coordinator managing a team with the following agents:

{chr(10).join(agent_descriptions)}

Your task is to:
1. Analyze the user's request
2. Determine which agent(s) are best suited for the task
3. Delegate or route the task appropriately
4. Synthesize and present the results

User Request: {execution_request.prompt}

Please coordinate the team to complete this request effectively."""

    # Parse team configuration
    team_config = TeamConfiguration(**(team.configuration or {}))

    # Use LLM config from team configuration if available
    model = team_config.llm.model if team_config.llm and team_config.llm.model else "kubiya/claude-sonnet-4"

    # Build LLM kwargs from configuration
    llm_kwargs = {}
    if team_config.llm:
        if team_config.llm.temperature is not None:
            llm_kwargs["temperature"] = team_config.llm.temperature
        if team_config.llm.max_tokens is not None:
            llm_kwargs["max_tokens"] = team_config.llm.max_tokens
        if team_config.llm.top_p is not None:
            llm_kwargs["top_p"] = team_config.llm.top_p
        if team_config.llm.stop is not None:
            llm_kwargs["stop"] = team_config.llm.stop
        if team_config.llm.frequency_penalty is not None:
            llm_kwargs["frequency_penalty"] = team_config.llm.frequency_penalty
        if team_config.llm.presence_penalty is not None:
            llm_kwargs["presence_penalty"] = team_config.llm.presence_penalty

    # Execute coordination using LiteLLM (streaming)
    return StreamingResponse(
        litellm_service.execute_agent_stream(
            prompt=coordination_prompt,
            model=model,
            system_prompt=execution_request.system_prompt or "You are an expert team coordinator. Delegate tasks efficiently and synthesize results clearly.",
            **llm_kwargs,
        ),
        media_type="text/event-stream",
    )
