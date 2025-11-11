"""
Multi-tenant agents router with Temporal workflow integration.

This router handles agent CRUD operations and execution submissions.
All operations are scoped to the authenticated organization.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Request
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
import structlog
import uuid
import httpx

from control_plane_api.app.middleware.auth import get_current_organization
from control_plane_api.app.lib.supabase import get_supabase
from control_plane_api.app.lib.temporal_client import get_temporal_client
from control_plane_api.app.workflows.agent_execution import AgentExecutionWorkflow, AgentExecutionInput
from control_plane_api.app.routers.projects import get_default_project_id
from control_plane_api.app.lib.validation import validate_agent_for_runtime

logger = structlog.get_logger()

router = APIRouter()


class ExecutionEnvironment(BaseModel):
    """Execution environment configuration for agents/teams"""
    env_vars: dict[str, str] = Field(default_factory=dict, description="Environment variables (key-value pairs)")
    secrets: list[str] = Field(default_factory=list, description="Secret names from Kubiya vault")
    integration_ids: list[str] = Field(default_factory=list, description="Integration UUIDs for delegated credentials")


def get_agent_projects(client, agent_id: str) -> list[dict]:
    """Get all projects an agent belongs to"""
    try:
        # Query project_agents join table
        result = (
            client.table("project_agents")
            .select("project_id, projects(id, name, key, description)")
            .eq("agent_id", agent_id)
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
        logger.warning("failed_to_fetch_agent_projects", error=str(e), agent_id=agent_id)
        return []


def get_agent_environments(client, agent_id: str) -> list[dict]:
    """Get all environments an agent is assigned to"""
    try:
        # Query agent_environments join table
        result = (
            client.table("agent_environments")
            .select("environment_id, environments(id, name, display_name, status)")
            .eq("agent_id", agent_id)
            .execute()
        )

        environments = []
        for item in result.data:
            env_data = item.get("environments")
            if env_data:
                environments.append({
                    "id": env_data["id"],
                    "name": env_data["name"],
                    "display_name": env_data.get("display_name"),
                    "status": env_data.get("status"),
                })

        return environments
    except Exception as e:
        logger.warning("failed_to_fetch_agent_environments", error=str(e), agent_id=agent_id)
        return []


def get_entity_skills(client, organization_id: str, entity_type: str, entity_id: str) -> list[dict]:
    """Get skills associated with an entity"""
    try:
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
    except Exception as e:
        logger.warning("failed_to_fetch_entity_skills", error=str(e), entity_type=entity_type, entity_id=entity_id)
        return []


def get_agent_skills_with_inheritance(client, organization_id: str, agent_id: str, team_id: str | None) -> list[dict]:
    """
    Get all skills for an agent, including those inherited from the team.
    Team skills are inherited by all team members.

    Inheritance order (later overrides earlier):
    1. Team skills (if agent is part of a team)
    2. Agent skills
    """
    seen_ids = set()
    skills = []

    # 1. Get team skills first (if agent is part of a team)
    if team_id:
        try:
            team_skills = get_entity_skills(client, organization_id, "team", team_id)
            for skill in team_skills:
                if skill["id"] not in seen_ids:
                    skills.append(skill)
                    seen_ids.add(skill["id"])
        except Exception as e:
            logger.warning("failed_to_fetch_team_skills_for_agent", error=str(e), team_id=team_id, agent_id=agent_id)

    # 2. Get agent-specific skills (these override team skills if there's a conflict)
    try:
        agent_skills = get_entity_skills(client, organization_id, "agent", agent_id)
        for skill in agent_skills:
            if skill["id"] not in seen_ids:
                skills.append(skill)
                seen_ids.add(skill["id"])
    except Exception as e:
        logger.warning("failed_to_fetch_agent_skills", error=str(e), agent_id=agent_id)

    return skills


# Pydantic schemas
class AgentCreate(BaseModel):
    name: str = Field(..., description="Agent name")
    description: str | None = Field(None, description="Agent description")
    system_prompt: str | None = Field(None, description="System prompt for the agent")
    capabilities: list = Field(default_factory=list, description="Agent capabilities")
    configuration: dict = Field(default_factory=dict, description="Agent configuration")
    model_id: str | None = Field(None, description="LiteLLM model identifier")
    model: str | None = Field(None, description="Model identifier (alias for model_id)")
    llm_config: dict = Field(default_factory=dict, description="Model-specific configuration")
    runtime: str | None = Field(None, description="Runtime type: 'default' (Agno) or 'claude_code' (Claude Code SDK)")
    runner_name: str | None = Field(None, description="Preferred runner for this agent")
    team_id: str | None = Field(None, description="Team ID to assign this agent to")
    environment_ids: list[str] = Field(default_factory=list, description="Environment IDs to deploy this agent to")
    skill_ids: list[str] = Field(default_factory=list, description="Tool set IDs to associate with this agent")
    skill_configurations: dict[str, dict] = Field(default_factory=dict, description="Tool set configurations keyed by skill ID")
    execution_environment: ExecutionEnvironment | None = Field(None, description="Execution environment: env vars, secrets, integrations")


class AgentUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    system_prompt: str | None = None
    status: str | None = None
    capabilities: list | None = None
    configuration: dict | None = None
    state: dict | None = None
    model_id: str | None = None
    model: str | None = None  # Alias for model_id
    llm_config: dict | None = None
    runtime: str | None = None
    runner_name: str | None = None
    team_id: str | None = None
    environment_ids: list[str] | None = None
    skill_ids: list[str] | None = None
    skill_configurations: dict[str, dict] | None = None
    execution_environment: ExecutionEnvironment | None = None


class AgentResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    description: str | None
    system_prompt: str | None
    status: str
    capabilities: list
    configuration: dict
    model_id: str | None
    llm_config: dict
    runtime: str | None
    runner_name: str | None
    team_id: str | None
    created_at: str
    updated_at: str
    last_active_at: str | None
    state: dict
    error_message: str | None
    projects: list[dict] = Field(default_factory=list, description="Projects this agent belongs to")
    environments: list[dict] = Field(default_factory=list, description="Environments this agent is deployed to")
    skill_ids: list[str] | None = Field(default_factory=list, description="IDs of associated skills")
    skills: list[dict] | None = Field(default_factory=list, description="Associated skills with details")
    execution_environment: ExecutionEnvironment | None = None


class AgentExecutionRequest(BaseModel):
    prompt: str = Field(..., description="The prompt to execute")
    system_prompt: str | None = Field(None, description="Optional system prompt")
    stream: bool = Field(False, description="Whether to stream the response")
    worker_queue_id: str = Field(..., description="Worker queue ID (UUID) to route execution to - REQUIRED")
    user_metadata: dict | None = Field(None, description="User attribution metadata (optional, auto-filled from token)")


class AgentExecutionResponse(BaseModel):
    execution_id: str
    workflow_id: str
    status: str
    message: str


@router.post("", response_model=AgentResponse, status_code=status.HTTP_201_CREATED)
async def create_agent(
    agent_data: AgentCreate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Create a new agent in the organization"""
    try:
        client = get_supabase()

        agent_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Handle model field - prefer 'model' over 'model_id' for backward compatibility
        model_id = agent_data.model or agent_data.model_id

        # Validate model_id against runtime type
        runtime = agent_data.runtime or "default"
        is_valid, errors = validate_agent_for_runtime(
            runtime_type=runtime,
            model_id=model_id,
            agent_config=agent_data.configuration,
            system_prompt=agent_data.system_prompt
        )
        if not is_valid:
            error_msg = "Agent validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
            logger.error(
                "agent_validation_failed",
                runtime=runtime,
                model_id=model_id,
                errors=errors,
                org_id=organization["id"]
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )

        # Store system_prompt in configuration for persistence
        configuration = agent_data.configuration.copy() if agent_data.configuration else {}
        if agent_data.system_prompt is not None:
            configuration["system_prompt"] = agent_data.system_prompt

        # Insert agent into database
        agent_record = {
            "id": agent_id,
            "organization_id": organization["id"],
            "name": agent_data.name,
            "description": agent_data.description,
            "status": "idle",
            "capabilities": agent_data.capabilities,
            "configuration": configuration,
            "model_id": model_id,
            "model_config": agent_data.llm_config,
            "runtime": agent_data.runtime or "default",
            "runner_name": agent_data.runner_name,
            "team_id": agent_data.team_id,
            # Note: skill_ids is not stored in agents table - skills are tracked via skill_associations junction table
            "execution_environment": agent_data.execution_environment.dict() if agent_data.execution_environment else {},
            "state": {},
            "created_at": now,
            "updated_at": now,
        }

        result = client.table("agents").insert(agent_record).execute()

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create agent"
            )

        agent = result.data[0]

        # Automatically assign agent to the default project
        default_project_id = get_default_project_id(organization)
        if default_project_id:
            try:
                project_agent_record = {
                    "id": str(uuid.uuid4()),
                    "project_id": default_project_id,
                    "agent_id": agent_id,
                    "role": None,
                    "added_at": now,
                    "added_by": organization.get("user_id"),
                }
                client.table("project_agents").insert(project_agent_record).execute()
                logger.info(
                    "agent_added_to_default_project",
                    agent_id=agent_id,
                    project_id=default_project_id,
                    org_id=organization["id"]
                )
            except Exception as e:
                logger.warning(
                    "failed_to_add_agent_to_default_project",
                    error=str(e),
                    agent_id=agent_id,
                    org_id=organization["id"]
                )

        # Create skill associations if skills were provided
        if agent_data.skill_ids:
            try:
                for skill_id in agent_data.skill_ids:
                    association_id = str(uuid.uuid4())
                    config_override = agent_data.skill_configurations.get(skill_id, {})

                    association_record = {
                        "id": association_id,
                        "organization_id": organization["id"],
                        "skill_id": skill_id,
                        "entity_type": "agent",
                        "entity_id": agent_id,
                        "configuration_override": config_override,
                        "created_at": now,
                    }

                    client.table("skill_associations").insert(association_record).execute()

                logger.info(
                    "agent_skills_associated",
                    agent_id=agent_id,
                    skill_count=len(agent_data.skill_ids),
                    org_id=organization["id"]
                )
            except Exception as e:
                logger.warning(
                    "failed_to_associate_agent_skills",
                    error=str(e),
                    agent_id=agent_id,
                    org_id=organization["id"]
                )

        # Create environment associations if environments were provided
        if agent_data.environment_ids:
            try:
                for environment_id in agent_data.environment_ids:
                    env_association_record = {
                        "id": str(uuid.uuid4()),
                        "agent_id": agent_id,
                        "environment_id": environment_id,
                        "organization_id": organization["id"],
                        "assigned_at": now,
                        "assigned_by": organization.get("user_id"),
                    }
                    client.table("agent_environments").insert(env_association_record).execute()

                logger.info(
                    "agent_environments_associated",
                    agent_id=agent_id,
                    environment_count=len(agent_data.environment_ids),
                    org_id=organization["id"]
                )
            except Exception as e:
                logger.warning(
                    "failed_to_associate_agent_environments",
                    error=str(e),
                    agent_id=agent_id,
                    org_id=organization["id"]
                )

        logger.info(
            "agent_created",
            agent_id=agent_id,
            agent_name=agent_data.name,
            org_id=organization["id"],
            org_slug=organization["slug"]
        )

        # Get skills with team inheritance
        team_id = agent.get("team_id")
        skills = get_agent_skills_with_inheritance(client, organization["id"], agent_id, team_id)

        # Extract system_prompt from configuration
        configuration = agent["configuration"] or {}
        system_prompt = configuration.get("system_prompt")

        return AgentResponse(
            id=agent["id"],
            organization_id=agent["organization_id"],
            name=agent["name"],
            description=agent["description"],
            system_prompt=system_prompt,
            status=agent["status"],
            capabilities=agent["capabilities"],
            configuration=agent["configuration"],
            model_id=agent["model_id"],
            llm_config=agent["model_config"] or {},
            runtime=agent.get("runtime"),
            runner_name=agent.get("runner_name"),
            team_id=agent.get("team_id"),
            created_at=agent["created_at"],
            updated_at=agent["updated_at"],
            last_active_at=agent.get("last_active_at"),
            state=agent.get("state", {}),
            error_message=agent.get("error_message"),
            projects=get_agent_projects(client, agent_id),
            environments=get_agent_environments(client, agent_id),
            skill_ids=[ts["id"] for ts in skills],
            skills=skills,
        )

    except Exception as e:
        logger.error("agent_creation_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create agent: {str(e)}"
        )


@router.get("", response_model=List[AgentResponse])
async def list_agents(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
    organization: dict = Depends(get_current_organization),
):
    """List all agents in the organization"""
    try:
        client = get_supabase()

        # Query agents for this organization
        query = client.table("agents").select("*").eq("organization_id", organization["id"])

        if status_filter:
            query = query.eq("status", status_filter)

        query = query.order("created_at", desc=True).range(skip, skip + limit - 1)

        result = query.execute()

        if not result.data:
            return []

        # Batch fetch all agent-project relationships in one query
        agent_ids = [agent["id"] for agent in result.data]
        agent_projects_result = (
            client.table("project_agents")
            .select("agent_id, projects(id, name, key, description)")
            .in_("agent_id", agent_ids)
            .execute()
        )

        # Group projects by agent_id
        projects_by_agent = {}
        for item in agent_projects_result.data or []:
            agent_id = item["agent_id"]
            project_data = item.get("projects")
            if project_data:
                if agent_id not in projects_by_agent:
                    projects_by_agent[agent_id] = []
                projects_by_agent[agent_id].append({
                    "id": project_data["id"],
                    "name": project_data["name"],
                    "key": project_data["key"],
                    "description": project_data.get("description"),
                })

        # Batch fetch environments for all agents
        agent_environments_result = (
            client.table("agent_environments")
            .select("agent_id, environments(id, name, display_name, status)")
            .in_("agent_id", agent_ids)
            .execute()
        )

        # Group environments by agent_id
        environments_by_agent = {}
        for item in agent_environments_result.data or []:
            agent_id = item["agent_id"]
            env_data = item.get("environments")
            if env_data:
                if agent_id not in environments_by_agent:
                    environments_by_agent[agent_id] = []
                environments_by_agent[agent_id].append({
                    "id": env_data["id"],
                    "name": env_data["name"],
                    "display_name": env_data.get("display_name"),
                    "status": env_data.get("status"),
                })

        # Batch fetch skills for all agents (including team inheritance)
        # Collect all unique team IDs
        team_ids = set()
        for agent in result.data:
            if agent.get("team_id"):
                team_ids.add(agent["team_id"])

        # BATCH FETCH: Get all team skills in one query
        team_skills = {}
        if team_ids:
            team_skills_result = (
                client.table("skill_associations")
                .select("entity_id, skill_id, configuration_override, skills(*)")
                .eq("organization_id", organization["id"])
                .eq("entity_type", "team")
                .in_("entity_id", list(team_ids))
                .execute()
            )

            for item in team_skills_result.data or []:
                team_id = item["entity_id"]
                skill_data = item.get("skills")
                if skill_data and skill_data.get("enabled", True):
                    if team_id not in team_skills:
                        team_skills[team_id] = []

                    config = skill_data.get("configuration", {})
                    override = item.get("configuration_override")
                    if override:
                        config = {**config, **override}

                    team_skills[team_id].append({
                        "id": skill_data["id"],
                        "name": skill_data["name"],
                        "type": skill_data["skill_type"],
                        "description": skill_data.get("description"),
                        "enabled": skill_data.get("enabled", True),
                        "configuration": config,
                    })

        # BATCH FETCH: Get all agent skills in one query
        agent_skills_result = (
            client.table("skill_associations")
            .select("entity_id, skill_id, configuration_override, skills(*)")
            .eq("organization_id", organization["id"])
            .eq("entity_type", "agent")
            .in_("entity_id", agent_ids)
            .execute()
        )

        agent_direct_skills = {}
        for item in agent_skills_result.data or []:
            agent_id = item["entity_id"]
            skill_data = item.get("skills")
            if skill_data and skill_data.get("enabled", True):
                if agent_id not in agent_direct_skills:
                    agent_direct_skills[agent_id] = []

                config = skill_data.get("configuration", {})
                override = item.get("configuration_override")
                if override:
                    config = {**config, **override}

                agent_direct_skills[agent_id].append({
                    "id": skill_data["id"],
                    "name": skill_data["name"],
                    "type": skill_data["skill_type"],
                    "description": skill_data.get("description"),
                    "enabled": skill_data.get("enabled", True),
                    "configuration": config,
                })

        # Combine team and agent skills with proper inheritance
        skills_by_agent = {}
        for agent in result.data:
            agent_id = agent["id"]
            team_id = agent.get("team_id")

            # Start with empty list
            combined_skills = []
            seen_ids = set()

            # Add team skills first (if agent is part of a team)
            if team_id and team_id in team_skills:
                for skill in team_skills[team_id]:
                    if skill["id"] not in seen_ids:
                        combined_skills.append(skill)
                        seen_ids.add(skill["id"])

            # Add agent-specific skills (these override team skills)
            if agent_id in agent_direct_skills:
                for skill in agent_direct_skills[agent_id]:
                    if skill["id"] not in seen_ids:
                        combined_skills.append(skill)
                        seen_ids.add(skill["id"])

            skills_by_agent[agent_id] = combined_skills

        agents = []
        for agent in result.data:
            # Extract system_prompt from configuration
            configuration = agent["configuration"] or {}
            system_prompt = configuration.get("system_prompt")

            agents.append(AgentResponse(
                id=agent["id"],
                organization_id=agent["organization_id"],
                name=agent["name"],
                description=agent["description"],
                system_prompt=system_prompt,
                status=agent["status"],
                capabilities=agent["capabilities"],
                configuration=agent["configuration"],
                model_id=agent["model_id"],
                llm_config=agent["model_config"] or {},
                runtime=agent.get("runtime"),
                runner_name=agent.get("runner_name"),
                team_id=agent.get("team_id"),
                created_at=agent["created_at"],
                updated_at=agent["updated_at"],
                last_active_at=agent.get("last_active_at"),
                state=agent.get("state", {}),
                error_message=agent.get("error_message"),
                projects=projects_by_agent.get(agent["id"], []),
                environments=environments_by_agent.get(agent["id"], []),
                skill_ids=[ts["id"] for ts in skills_by_agent.get(agent["id"], [])],
                skills=skills_by_agent.get(agent["id"], []),
                execution_environment=(
                    ExecutionEnvironment(**agent["execution_environment"])
                    if agent.get("execution_environment")
                    else None
                ),
            ))

        logger.info(
            "agents_listed",
            count=len(agents),
            org_id=organization["id"],
            org_slug=organization["slug"]
        )

        return agents

    except Exception as e:
        logger.error("agents_list_failed", error=str(e), org_id=organization["id"])
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list agents: {str(e)}"
        )


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Get a specific agent by ID"""
    try:
        client = get_supabase()

        result = (
            client.table("agents")
            .select("*")
            .eq("id", agent_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = result.data

        # Get skills with team inheritance
        team_id = agent.get("team_id")
        skills = get_agent_skills_with_inheritance(client, organization["id"], agent_id, team_id)

        # Parse execution_environment if it exists
        execution_env = None
        if agent.get("execution_environment"):
            try:
                execution_env = ExecutionEnvironment(**agent["execution_environment"])
            except Exception:
                execution_env = None

        # Extract system_prompt from configuration
        configuration = agent["configuration"] or {}
        system_prompt = configuration.get("system_prompt")

        return AgentResponse(
            id=agent["id"],
            organization_id=agent["organization_id"],
            name=agent["name"],
            description=agent["description"],
            system_prompt=system_prompt,
            status=agent["status"],
            capabilities=agent["capabilities"],
            configuration=agent["configuration"],
            model_id=agent["model_id"],
            llm_config=agent["model_config"] or {},
            runtime=agent.get("runtime"),
            runner_name=agent.get("runner_name"),
            team_id=agent.get("team_id"),
            created_at=agent["created_at"],
            updated_at=agent["updated_at"],
            last_active_at=agent.get("last_active_at"),
            state=agent.get("state", {}),
            error_message=agent.get("error_message"),
            projects=get_agent_projects(client, agent_id),
            environments=get_agent_environments(client, agent_id),
            skill_ids=[ts["id"] for ts in skills],
            skills=skills,
            execution_environment=execution_env,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("agent_get_failed", error=str(e), agent_id=agent_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent: {str(e)}"
        )


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(
    agent_id: str,
    agent_data: AgentUpdate,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Update an agent"""
    try:
        client = get_supabase()

        # Check if agent exists and belongs to organization
        existing = (
            client.table("agents")
            .select("id")
            .eq("id", agent_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not existing.data:
            raise HTTPException(status_code=404, detail="Agent not found")

        # Build update dict
        update_data = agent_data.model_dump(exclude_unset=True)

        # Extract skill data before database update
        skill_ids = update_data.pop("skill_ids", None)
        skill_configurations = update_data.pop("skill_configurations", None)

        # Extract environment data before database update (many-to-many via junction table)
        environment_ids = update_data.pop("environment_ids", None)

        # Extract system_prompt and store it in configuration
        system_prompt = update_data.pop("system_prompt", None)
        if system_prompt is not None:
            # Get existing agent to merge with existing configuration
            existing_agent = (
                client.table("agents")
                .select("configuration")
                .eq("id", agent_id)
                .eq("organization_id", organization["id"])
                .single()
                .execute()
            )
            existing_config = existing_agent.data.get("configuration", {}) if existing_agent.data else {}

            # Merge system_prompt into configuration
            merged_config = {**existing_config, "system_prompt": system_prompt}
            update_data["configuration"] = merged_config

        # Handle model field - prefer 'model' over 'model_id' for backward compatibility
        if "model" in update_data and update_data["model"]:
            update_data["model_id"] = update_data.pop("model")
        elif "model" in update_data:
            # Remove null model field
            update_data.pop("model")

        # Map llm_config to model_config for database
        if "llm_config" in update_data:
            update_data["model_config"] = update_data.pop("llm_config")

        # Validate model_id and runtime if being updated
        if "model_id" in update_data or "runtime" in update_data:
            # Get current agent to merge with updates
            existing_agent = (
                client.table("agents")
                .select("model_id, runtime, configuration")
                .eq("id", agent_id)
                .eq("organization_id", organization["id"])
                .single()
                .execute()
            )

            if existing_agent.data:
                # Merge updates with existing values
                final_model_id = update_data.get("model_id", existing_agent.data.get("model_id"))
                final_runtime = update_data.get("runtime", existing_agent.data.get("runtime", "default"))
                final_config = update_data.get("configuration", existing_agent.data.get("configuration", {}))

                is_valid, errors = validate_agent_for_runtime(
                    runtime_type=final_runtime,
                    model_id=final_model_id,
                    agent_config=final_config,
                    system_prompt=system_prompt
                )
                if not is_valid:
                    error_msg = "Agent validation failed:\n" + "\n".join(f"  - {err}" for err in errors)
                    logger.error(
                        "agent_validation_failed",
                        runtime=final_runtime,
                        model_id=final_model_id,
                        errors=errors,
                        org_id=organization["id"]
                    )
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=error_msg
                    )

        # Handle execution_environment - convert to dict if present
        if "execution_environment" in update_data and update_data["execution_environment"]:
            if isinstance(update_data["execution_environment"], ExecutionEnvironment):
                update_data["execution_environment"] = update_data["execution_environment"].dict()
            # If None, keep as None to preserve existing value

        # Note: skill_ids is not stored in agents table - skills are tracked via skill_associations junction table
        # The skill associations will be updated separately below if skill_ids was provided

        update_data["updated_at"] = datetime.utcnow().isoformat()

        # Update agent
        result = (
            client.table("agents")
            .update(update_data)
            .eq("id", agent_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update agent"
            )

        agent = result.data[0]

        # Update skill associations if skill_ids was provided
        if skill_ids is not None:
            try:
                # Delete existing associations (scoped to organization)
                client.table("skill_associations").delete().eq("organization_id", organization["id"]).eq("entity_type", "agent").eq("entity_id", agent_id).execute()

                # Create new associations
                now = datetime.utcnow().isoformat()
                for skill_id in skill_ids:
                    association_id = str(uuid.uuid4())
                    config_override = (skill_configurations or {}).get(skill_id, {})

                    association_record = {
                        "id": association_id,
                        "organization_id": organization["id"],
                        "skill_id": skill_id,
                        "entity_type": "agent",
                        "entity_id": agent_id,
                        "configuration_override": config_override,
                        "created_at": now,
                    }

                    client.table("skill_associations").insert(association_record).execute()

                logger.info(
                    "agent_skills_updated",
                    agent_id=agent_id,
                    skill_count=len(skill_ids),
                    org_id=organization["id"]
                )
            except Exception as e:
                logger.error(
                    "failed_to_update_agent_skills",
                    error=str(e),
                    agent_id=agent_id,
                    org_id=organization["id"]
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to update agent skills: {str(e)}"
                )

        # Update environment associations if environment_ids was provided
        if environment_ids is not None:
            try:
                # Delete existing environment associations
                client.table("agent_environments").delete().eq("agent_id", agent_id).execute()

                # Create new environment associations
                for environment_id in environment_ids:
                    env_association_record = {
                        "id": str(uuid.uuid4()),
                        "agent_id": agent_id,
                        "environment_id": environment_id,
                        "organization_id": organization["id"],
                        "assigned_at": datetime.utcnow().isoformat(),
                    }
                    client.table("agent_environments").insert(env_association_record).execute()

                logger.info(
                    "agent_environments_updated",
                    agent_id=agent_id,
                    environment_count=len(environment_ids),
                    org_id=organization["id"]
                )
            except Exception as e:
                logger.warning(
                    "failed_to_update_agent_environments",
                    error=str(e),
                    agent_id=agent_id,
                    org_id=organization["id"]
                )

        logger.info(
            "agent_updated",
            agent_id=agent_id,
            org_id=organization["id"],
            fields_updated=list(update_data.keys())
        )

        # Get skills with team inheritance
        team_id = agent.get("team_id")
        skills = get_agent_skills_with_inheritance(client, organization["id"], agent_id, team_id)

        # Parse execution_environment if it exists
        execution_env = None
        if agent.get("execution_environment"):
            try:
                execution_env = ExecutionEnvironment(**agent["execution_environment"])
            except Exception:
                execution_env = None

        # Extract system_prompt from configuration
        configuration = agent["configuration"] or {}
        system_prompt = configuration.get("system_prompt")

        return AgentResponse(
            id=agent["id"],
            organization_id=agent["organization_id"],
            name=agent["name"],
            description=agent["description"],
            system_prompt=system_prompt,
            status=agent["status"],
            capabilities=agent["capabilities"],
            configuration=agent["configuration"],
            model_id=agent["model_id"],
            llm_config=agent["model_config"] or {},
            runtime=agent.get("runtime"),
            runner_name=agent.get("runner_name"),
            team_id=agent.get("team_id"),
            created_at=agent["created_at"],
            updated_at=agent["updated_at"],
            last_active_at=agent.get("last_active_at"),
            state=agent.get("state", {}),
            error_message=agent.get("error_message"),
            projects=get_agent_projects(client, agent_id),
            environments=get_agent_environments(client, agent_id),
            skill_ids=[ts["id"] for ts in skills],
            skills=skills,
            execution_environment=execution_env,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("agent_update_failed", error=str(e), agent_id=agent_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update agent: {str(e)}"
        )


@router.delete("/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(
    agent_id: str,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """Delete an agent"""
    try:
        client = get_supabase()

        result = (
            client.table("agents")
            .delete()
            .eq("id", agent_id)
            .eq("organization_id", organization["id"])
            .execute()
        )

        if not result.data:
            raise HTTPException(status_code=404, detail="Agent not found")

        logger.info("agent_deleted", agent_id=agent_id, org_id=organization["id"])

        return None

    except HTTPException:
        raise
    except Exception as e:
        logger.error("agent_delete_failed", error=str(e), agent_id=agent_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete agent: {str(e)}"
        )


@router.post("/{agent_id}/execute", response_model=AgentExecutionResponse)
async def execute_agent(
    agent_id: str,
    execution_request: AgentExecutionRequest,
    request: Request,
    organization: dict = Depends(get_current_organization),
):
    """
    Execute an agent by submitting to Temporal workflow.

    This creates an execution record and starts a Temporal workflow.
    The actual execution happens asynchronously on the Temporal worker.

    The runner_name should come from the Composer UI where user selects
    from available runners (fetched from Kubiya API /api/v1/runners).
    """
    try:
        client = get_supabase()

        # Get agent details
        agent_result = (
            client.table("agents")
            .select("*")
            .eq("id", agent_id)
            .eq("organization_id", organization["id"])
            .single()
            .execute()
        )

        if not agent_result.data:
            raise HTTPException(status_code=404, detail="Agent not found")

        agent = agent_result.data

        # Create execution record
        execution_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()

        # Validate and get worker queue
        worker_queue_id = execution_request.worker_queue_id

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

        execution_record = {
            "id": execution_id,
            "organization_id": organization["id"],
            "execution_type": "AGENT",
            "entity_id": agent_id,
            "entity_name": agent["name"],
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

        # Extract MCP servers from agent configuration
        agent_configuration = agent.get("configuration", {})
        mcp_servers = agent_configuration.get("mcpServers", {})

        # Submit to Temporal workflow
        # Task queue is the worker queue UUID
        task_queue = worker_queue_id

        # Get Temporal client
        temporal_client = await get_temporal_client()

        # Start workflow
        # Use agent's stored system_prompt from configuration as fallback
        system_prompt = execution_request.system_prompt or agent_configuration.get("system_prompt")

        # Get API key from Authorization header
        auth_header = request.headers.get("authorization", "")
        api_key = auth_header.replace("UserKey ", "").replace("Bearer ", "") if auth_header else None

        # Get control plane URL from request
        control_plane_url = str(request.base_url).rstrip("/")

        workflow_input = AgentExecutionInput(
            execution_id=execution_id,
            agent_id=agent_id,
            organization_id=organization["id"],
            prompt=execution_request.prompt,
            system_prompt=system_prompt,
            model_id=agent.get("model_id"),
            model_config=agent.get("model_config", {}),
            agent_config=agent_configuration,
            mcp_servers=mcp_servers,
            user_metadata=user_metadata,
            runtime_type=agent.get("runtime", "default"),
        )

        workflow_handle = await temporal_client.start_workflow(
            AgentExecutionWorkflow.run,
            workflow_input,
            id=f"agent-execution-{execution_id}",
            task_queue=task_queue,
        )

        logger.info(
            "agent_execution_submitted",
            execution_id=execution_id,
            agent_id=agent_id,
            workflow_id=workflow_handle.id,
            task_queue=task_queue,
            worker_queue_id=worker_queue_id,
            worker_queue_name=worker_queue.get("name"),
            org_id=organization["id"],
            org_name=organization["name"],
        )

        return AgentExecutionResponse(
            execution_id=execution_id,
            workflow_id=workflow_handle.id,
            status="PENDING",
            message=f"Execution submitted to worker queue: {worker_queue.get('name')}",
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            "agent_execution_failed",
            error=str(e),
            agent_id=agent_id,
            org_id=organization["id"]
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute agent: {str(e)}"
        )
